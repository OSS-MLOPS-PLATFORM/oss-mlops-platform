# evaluate_component.py
from kfp.v2.dsl import component

@component(
    base_image="python:3.10",
    packages_to_install=["numpy", "mlflow~=2.4.1"],
    output_component_file='src/components_yaml/evaluate_component.yaml',
)
def evaluate(
    run_id: str,
    mlflow_tracking_uri: str,
    threshold_metrics: dict
) -> bool:
    """
    Evaluate component: Compares metrics from training with given thresholds.

    Args:
        run_id (string):  MLflow run ID
        mlflow_tracking_uri (string): MLflow tracking URI
        threshold_metrics (dict): Minimum threshold values for each metric
    Returns:
        Bool indicating whether evaluation passed or failed.
    """
    from mlflow.tracking import MlflowClient
    import logging

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    client = MlflowClient(tracking_uri=mlflow_tracking_uri)
    info = client.get_run(run_id)
    training_metrics = info.data.metrics

    logger.info(f"Training metrics: {training_metrics}")

    # compare the evaluation metrics with the defined thresholds
    for key, value in threshold_metrics.items():
        if key not in training_metrics or training_metrics[key] > value:
            logger.error(f"Metric {key} failed. Evaluation not passed!")
            return False
    return True