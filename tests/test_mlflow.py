import subprocess
import time
import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd
import pytest
from mlflow.tracking import MlflowClient
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.linear_model import ElasticNet
import os
from minio import Minio
import uuid
import logging

from .conftest import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MLFLOW_TRACKING_URI = "http://localhost:5000"

MINIO_URI = "localhost:9000"
BUCKET_NAME = 'mlflow'

MLFLOW_EXPERIMENT_NAME = f"mlflow-minio-test-{str(uuid.uuid4())[:5]}"
MODEL_NAME = "ElasticnetWineModel"

os.environ['MLFLOW_S3_ENDPOINT_URL'] = 'http://localhost:9000/'
os.environ['AWS_ACCESS_KEY_ID'] = AWS_ACCESS_KEY_ID
os.environ['AWS_SECRET_ACCESS_KEY'] = AWS_SECRET_ACCESS_KEY


@pytest.mark.order(3)
def test_create_experiment():
    with subprocess.Popen(["kubectl", "-n", "mlflow", "port-forward", "svc/mlflow", "5000:5000"], stdout=True) as proc:
        try:
            time.sleep(2)  # give some time to the port-forward connection
            mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
            client = MlflowClient()
            rand_id = str(uuid.uuid4())[:5]
            experiment_id = client.create_experiment(f"Test-{rand_id}")
            logger.info(f"Experiment id: {experiment_id}")
            client.delete_experiment(experiment_id)
            logger.info("Done")
        except Exception as e:
            logger.error(f"ERROR: {e}")
            raise e
        finally:
            proc.terminate()


@pytest.mark.order(4)
def test_minio_create_bucket():

    bucket_name = f"test-{str(uuid.uuid4())[:5]}"

    client = Minio(
        MINIO_URI,
        access_key=AWS_ACCESS_KEY_ID,
        secret_key=AWS_SECRET_ACCESS_KEY,
        secure=False,
    )

    with subprocess.Popen(["kubectl", "-n", "mlflow", "port-forward", "svc/mlflow-minio-service", "9000:9000"], stdout=True) as proc:
        try:
            time.sleep(2)  # give some time to the port-forward connection
            client.make_bucket(bucket_name)
            client.remove_bucket(bucket_name)
            logger.info("Done")
        except Exception as e:
            logger.error(f"ERROR: {e}")
            raise e
        finally:
            proc.terminate()


def eval_metrics(actual, pred):
    rmse = np.sqrt(mean_squared_error(actual, pred))
    mae = mean_absolute_error(actual, pred)
    r2 = r2_score(actual, pred)
    return rmse, mae, r2


def clean_up():
    logger.info(f"Cleaning experiment and model")
    client = MlflowClient()
    experiment = client.get_experiment_by_name(MLFLOW_EXPERIMENT_NAME)
    experiment_id = experiment.experiment_id

    # client.delete_experiment(experiment_id)

    client.delete_registered_model(MODEL_NAME)

    logger.info(f"Cleaning artifacts")
    minioClient = Minio(
        MINIO_URI,
        access_key=AWS_ACCESS_KEY_ID,
        secret_key=AWS_SECRET_ACCESS_KEY,
        secure=False,
    )
    objects_to_delete = minioClient.list_objects(
        bucket_name=BUCKET_NAME, prefix=experiment_id, recursive=True
    )

    for obj in objects_to_delete:
        logger.info(f"Deleting artifact: {obj.object_name}")
        minioClient.remove_object(bucket_name=BUCKET_NAME, object_name=obj.object_name)


def run_experiment():

    np.random.seed(40)

    # Read the wine-quality csv file from the URL
    csv_url = "http://archive.ics.uci.edu/ml/machine-learning-databases/wine-quality/winequality-red.csv"

    data = pd.read_csv(csv_url, sep=";")

    # Split the data into training and test sets. (0.75, 0.25) split.
    train, test = train_test_split(data)

    # The predicted column is "quality" which is a scalar from [3, 9]
    train_x = train.drop(["quality"], axis=1)
    test_x = test.drop(["quality"], axis=1)
    train_y = train[["quality"]]
    test_y = test[["quality"]]

    alpha = 0.5
    l1_ratio = 0.5

    logger.info(f"Using MLflow tracking URI: {MLFLOW_TRACKING_URI}")
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

    logger.info(f"Using MLflow experiment: {MLFLOW_EXPERIMENT_NAME}")
    mlflow.set_experiment(MLFLOW_EXPERIMENT_NAME)

    with mlflow.start_run():
        lr = ElasticNet(alpha=alpha, l1_ratio=l1_ratio, random_state=42)

        logger.info("Fitting model...")

        lr.fit(train_x, train_y)

        logger.info("Finished fitting")

        predicted_qualities = lr.predict(test_x)

        (rmse, mae, r2) = eval_metrics(test_y, predicted_qualities)

        print("Elasticnet model (alpha=%f, l1_ratio=%f):" % (alpha, l1_ratio))
        print("  RMSE: %s" % rmse)
        print("  MAE: %s" % mae)
        print("  R2: %s" % r2)

        logger.info("Logging parameters to MLflow")
        mlflow.log_param("alpha", alpha)
        mlflow.log_param("l1_ratio", l1_ratio)
        mlflow.log_metric("rmse", rmse)
        mlflow.log_metric("r2", r2)
        mlflow.log_metric("mae", mae)

        logger.info("Logging trained model")
        mlflow.sklearn.log_model(lr, "model", registered_model_name=MODEL_NAME)

        # clean up experiment and artifacts
        clean_up()


@pytest.mark.order(5)
def test_mlflow_end_to_end():

    with subprocess.Popen(["kubectl", "-n", "mlflow", "port-forward", "svc/mlflow", "5000:5000"], stdout=False) as proc1:
        with subprocess.Popen(["kubectl", "-n", "mlflow", "port-forward", "svc/mlflow-minio-service", "9000:9000"], stdout=False) as proc2:
            try:
                time.sleep(2)  # give some time to the port-forward connection
                run_experiment()
                logger.info("Done")
            except Exception as e:
                logger.error(f"ERROR: {e}")
                raise e
            finally:
                proc1.terminate()
                proc2.terminate()
