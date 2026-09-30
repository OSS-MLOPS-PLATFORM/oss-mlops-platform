
# deploy_model_component.py
from kfp.v2.dsl import component

@component(
    base_image="python:3.9",
    packages_to_install=["kserve==0.11.0"],
    output_component_file='src/components_yaml/deploy_model_component.yaml',
)
def deploy_model(model_name: str, storage_uri: str):
    """
    Deploy the model as an inference service with Kserve.
    """
    import logging
    from kubernetes import client
    from kserve import KServeClient
    from kserve import constants
    from kserve import V1beta1InferenceService
    from kserve import V1beta1InferenceServiceSpec
    from kserve import V1beta1PredictorSpec
    from kserve import V1beta1SKLearnSpec
    from kubernetes.client import V1ResourceRequirements

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    model_uri = f"{storage_uri}/{model_name}"
    logger.info(f"MODEL URI: {model_uri}")

    namespace = 'kserve-inference'
    kserve_version='v1beta1'
    api_version = constants.KSERVE_GROUP + '/' + kserve_version

    isvc = V1beta1InferenceService(
        api_version = api_version,
        kind = constants.KSERVE_KIND,
        metadata = client.V1ObjectMeta(
            name = model_name,
            namespace = namespace,
            annotations = {'sidecar.istio.io/inject':'false'}
        ),
        spec = V1beta1InferenceServiceSpec(
            predictor=V1beta1PredictorSpec(
                service_account_name="kserve-sa",
                min_replicas=1,
                max_replicas = 1,
                sklearn=V1beta1SKLearnSpec(
                    storage_uri=model_uri,
                    resources=V1ResourceRequirements(
                        requests={"cpu": "100m", "memory": "512Mi"},
                        limits={"cpu": "300m", "memory": "512Mi"}
                    )
                ),
            )
        )
    )
    KServe = KServeClient()
    KServe.create(isvc)
