import subprocess
import logging
import pathlib
import pytest
import os
from envsubst import envsubst

from .conftest import HOST_IP
from .test_kfp import run_pipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BUILD_FILE = pathlib.Path(__file__).parent / "resources" / "registry" / "build_push_image.sh"
PIPELINE_TEMPLATE = pathlib.Path(__file__).parent / "resources" / "registry" / "pipeline.yaml.template"

IMAGE_NAME = "kfp-registry-test-image"
EXPERIMENT_NAME = "Test Experiment (Registry)"


def build_push_image():
    logging.info(f"Building and pushing image to local registry...")
    subprocess.run([str(BUILD_FILE), HOST_IP], stdout=True)


def render_pipeline_yaml(output: str):
    """Use the pipeline.yaml.template to create the final pipeline.yaml with the
    correct registry IP by replacing the "${HOST_IP}" placeholder."""
    with open(PIPELINE_TEMPLATE, "r") as f_tpl:
        with open(output, "w") as f_out:
            f_out.write(envsubst(f_tpl.read()))


@pytest.mark.order(7)
@pytest.mark.skipif(
    os.environ.get('INSTALL_LOCAL_REGISTRY') == 'false',
    reason="No local image registry was installed."
)
def test_push_image():
    # build the base docker image and load it into the cluster
    build_push_image()


@pytest.mark.order(8)
@pytest.mark.timeout(120)
@pytest.mark.skipif(
    os.environ.get('INSTALL_LOCAL_REGISTRY') == 'false',
    reason="No local image registry was installed."
)
def test_run_pipeline_using_registry(tmp_path):

    # build the base docker image and load it into the cluster
    build_push_image()

    # create pipeline.yaml with the right registry IP address
    pipeline_file = tmp_path / "pipeline.yaml"
    render_pipeline_yaml(output=str(pipeline_file))

    # submit and run pipeline
    run_pipeline(pipeline_file=str(pipeline_file), experiment_name=EXPERIMENT_NAME)
