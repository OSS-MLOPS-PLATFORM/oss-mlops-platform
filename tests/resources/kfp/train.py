import mlflow

MLFLOW_TRACKING_URI = "http://mlflow.mlflow.svc.cluster.local:5000"
MLFLOW_EXPERIMENT_NAME = "Kubeflow Pipeline test run"


def main():
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    experiment = mlflow.get_experiment_by_name(MLFLOW_EXPERIMENT_NAME)

    if experiment is None:
        experiment_id = mlflow.create_experiment(MLFLOW_EXPERIMENT_NAME)
    else:
        experiment_id = experiment.experiment_id

    with mlflow.start_run(experiment_id=experiment_id) as run:
        mlflow.log_param("my", "param")
        mlflow.log_metric("score", 100)


if __name__ == '__main__':
    main()
