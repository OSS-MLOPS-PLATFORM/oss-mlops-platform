## Test MLFlow deployment

First, make sure mlflow and minio server are both, MLflow ([http://localhost:5000](http://localhost:5000))
and Minio ([http://localhost:9000](http://localhost:9000)), are accessible:

MLflow:

```bash
kubectl -n mlflow port-forward svc/mlflow 5000:5000
```

MinIO:

```bash
kubectl -n mlflow port-forward svc/mlflow-minio-service 9000:9000
```

### Create an experiment run

Create a new working directory and a virtual environment with your method of choice.

Install dependencies:

```bash
pip install mlflow google-cloud-storage scikit-learn boto3
```

Create a sample Python file named `train.py` adapted from [train.py](https://github.com/mlflow/mlflow/blob/master/examples/sklearn_elasticnet_wine/train.py) used in the [MLflow tutorial](https://www.mlflow.org/docs/latest/tutorials-and-examples/tutorial.html):

```python
# train.py
# Adapted from https://github.com/mlflow/mlflow/blob/master/examples/sklearn_elasticnet_wine/train.py
import os
import logging
import sys

import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.linear_model import ElasticNet
import os

os.environ['MLFLOW_S3_ENDPOINT_URL'] = 'http://localhost:9000/'
os.environ['AWS_ACCESS_KEY_ID'] = 'minioadmin' 
os.environ['AWS_SECRET_ACCESS_KEY'] = 'minioadmin'

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MLFLOW_TRACKING_URI = "http://localhost:5000"
MLFLOW_EXPERIMENT_NAME = "mlflow-minio-test"


def eval_metrics(actual, pred):
    rmse = np.sqrt(mean_squared_error(actual, pred))
    mae = mean_absolute_error(actual, pred)
    r2 = r2_score(actual, pred)
    return rmse, mae, r2


def main():
    np.random.seed(40)

    # Read the wine-quality csv file from the URL
    csv_url = (
        "http://archive.ics.uci.edu/ml/machine-learning-databases/wine-quality/winequality-red.csv"
    )

    data = pd.read_csv(csv_url, sep=";")

    # Split the data into training and test sets. (0.75, 0.25) split.
    train, test = train_test_split(data)

    # The predicted column is "quality" which is a scalar from [3, 9]
    train_x = train.drop(["quality"], axis=1)
    test_x = test.drop(["quality"], axis=1)
    train_y = train[["quality"]]
    test_y = test[["quality"]]

    alpha = float(sys.argv[1]) if len(sys.argv) > 1 else 0.5
    l1_ratio = float(sys.argv[2]) if len(sys.argv) > 2 else 0.5

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

        logger.info("Elasticnet model (alpha=%f, l1_ratio=%f):" % (alpha, l1_ratio))
        logger.info("  RMSE: %s" % rmse)
        logger.info("  MAE: %s" % mae)
        logger.info("  R2: %s" % r2)

        logger.info("Logging parameters to MLflow")
        mlflow.log_param("alpha", alpha)
        mlflow.log_param("l1_ratio", l1_ratio)
        mlflow.log_metric("rmse", rmse)
        mlflow.log_metric("r2", r2)
        mlflow.log_metric("mae", mae)

        logger.info("Logging trained model")
        mlflow.sklearn.log_model(lr, "model", registered_model_name="ElasticnetWineModel")

if __name__ == '__main__':
    main()

```

Run the script:

```bash
python train.py
```

After the script finishes, navigate to the MLflow UI at [http://localhost:5000](http://localhost:5000),
and you should see your run under the experiment "mlflow-minio-test". Browse the run parameters, metrics and artifacts.