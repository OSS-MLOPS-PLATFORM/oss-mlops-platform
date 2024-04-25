import os
import subprocess
import logging
import pathlib
import time

import kfp
import pytest
import re
import requests
from urllib.parse import urlsplit

from .conftest import CLUSTER_NAME, IS_STANDALONE_KFP

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BUILD_FILE = pathlib.Path(__file__).parent / "resources" / "kfp" / "build_image.sh"
PIPELINE_FILE = pathlib.Path(__file__).parent / "resources" / "kfp" / "pipeline.yaml"

IMAGE_NAME = "kfp-test-img"
EXPERIMENT_NAME = "Test Experiment"
KUBEFLOW_ENDPOINT = "http://localhost:8080"
KUBEFLOW_USERNAME = "user@example.com"
KUBEFLOW_PASSWORD = "12341234"
KUBEFLOW_USER_NAMESPACE = "kubeflow-user-example-com"


def get_istio_auth_session(url: str, username: str, password: str) -> dict:
    """
    Determine if the specified URL is secured by Dex and try to obtain a session cookie.
    WARNING: only Dex `staticPasswords` and `LDAP` authentication are currently supported
             (we default default to using `staticPasswords` if both are enabled)

    :param url: Kubeflow server URL, including protocol
    :param username: Dex `staticPasswords` or `LDAP` username
    :param password: Dex `staticPasswords` or `LDAP` password
    :return: auth session information
    """
    # define the default return object
    auth_session = {
        "endpoint_url": url,    # KF endpoint URL
        "redirect_url": None,   # KF redirect URL, if applicable
        "dex_login_url": None,  # Dex login URL (for POST of credentials)
        "is_secured": None,     # True if KF endpoint is secured
        "session_cookie": None  # Resulting session cookies in the form "key1=value1; key2=value2"
    }
    # use a persistent session (for cookies)
    with requests.Session() as s:
        ################
        # Determine if Endpoint is Secured
        ################
        resp = s.get(url, allow_redirects=True)
        if resp.status_code != 200:
            raise RuntimeError(
                f"HTTP status code '{resp.status_code}' for GET against: {url}"
            )
        auth_session["redirect_url"] = resp.url

        # if we were NOT redirected, then the endpoint is UNSECURED
        if len(resp.history) == 0:
            auth_session["is_secured"] = False
            return auth_session
        else:
            auth_session["is_secured"] = True

        ################
        # Get Dex Login URL
        ################
        redirect_url_obj = urlsplit(auth_session["redirect_url"])

        # if we are at `/auth?=xxxx` path, we need to select an auth type
        if re.search(r"/auth$", redirect_url_obj.path):

            #######
            # TIP: choose the default auth type by including ONE of the following
            #######

            # OPTION 1: set "staticPasswords" as default auth type
            redirect_url_obj = redirect_url_obj._replace(
                path=re.sub(r"/auth$", "/auth/local", redirect_url_obj.path)
            )
            # OPTION 2: set "ldap" as default auth type
            # redirect_url_obj = redirect_url_obj._replace(
            #     path=re.sub(r"/auth$", "/auth/ldap", redirect_url_obj.path)
            # )

        # if we are at `/auth/xxxx/login` path, then no further action is needed
        # (we can use it for login POST)
        if re.search(r"/auth/.*/login$", redirect_url_obj.path):
            auth_session["dex_login_url"] = redirect_url_obj.geturl()

        # else, we need to be redirected to the actual login page
        else:
            # this GET should redirect us to the `/auth/xxxx/login` path
            resp = s.get(redirect_url_obj.geturl(), allow_redirects=True)
            if resp.status_code != 200:
                raise RuntimeError(
                    f"HTTP status code '{resp.status_code}' "
                    f"for GET against: {redirect_url_obj.geturl()}"
                )
            # set the login url
            auth_session["dex_login_url"] = resp.url

        ################
        # Attempt Dex Login
        ################
        resp = s.post(
            auth_session["dex_login_url"],
            data={"login": username, "password": password},
            allow_redirects=True
        )
        if len(resp.history) == 0:
            raise RuntimeError(
                f"Login credentials were probably invalid - "
                f"No redirect after POST to: {auth_session['dex_login_url']}"
            )
        # store the session cookies in a "key1=value1; key2=value2" string
        auth_session["session_cookie"] = "; ".join(
            [f"{c.name}={c.value}" for c in s.cookies]
        )

    return auth_session


def run_pipeline(pipeline_file: str, experiment_name: str):
    """Run a pipeline on a Kubeflow cluster."""
    with subprocess.Popen(["kubectl", "-n", "istio-system", "port-forward", "svc/istio-ingressgateway", "8080:80"], stdout=True) as proc: # noqa: E501
        try:
            time.sleep(2)  # give some time to the port-forward connection
            auth_session = get_istio_auth_session(
                url=KUBEFLOW_ENDPOINT,
                username=KUBEFLOW_USERNAME,
                password=KUBEFLOW_PASSWORD
            )
            client = kfp.Client(
                host=f"{KUBEFLOW_ENDPOINT}/pipeline",
                cookies=auth_session["session_cookie"],
                namespace=KUBEFLOW_USER_NAMESPACE,
            )
            created_run = client.create_run_from_pipeline_package(
                pipeline_file=pipeline_file,
                enable_caching=False,
                arguments={},
                run_name="kfp_test_run",
                experiment_name=experiment_name,
                namespace=KUBEFLOW_USER_NAMESPACE
            )
            run_id = created_run.run_id
            logger.info(f"Submitted run with ID: {run_id}")
            logger.info(f"Waiting for run {run_id} to complete....")
            run_detail = created_run.wait_for_run_completion()
            _handle_job_end(run_detail)

            # clean up
            experiment = client.get_experiment(
                experiment_name=experiment_name, namespace=KUBEFLOW_USER_NAMESPACE
            )
            client.delete_experiment(experiment.id)
            logger.info("Done")

        except Exception as e:
            logger.error(f"ERROR: {e}")
            raise e
        finally:
            proc.terminate()


def run_pipeline_standalone_kfp(pipeline_file: str, experiment_name: str):
    """Run a pipeline on a standalone Kubeflow Pipelines cluster."""
    with subprocess.Popen(["kubectl", "-n", "kubeflow", "port-forward", "svc/ml-pipeline-ui", "8080:80"], stdout=True) as proc:  # noqa: E501
        try:
            time.sleep(2)  # give some time to the port-forward connection

            client = kfp.Client(
                host=f"{KUBEFLOW_ENDPOINT}/pipeline",
            )
            created_run = client.create_run_from_pipeline_package(
                pipeline_file=pipeline_file,
                enable_caching=False,
                arguments={},
                run_name="kfp_test_run",
                experiment_name=experiment_name,
            )
            run_id = created_run.run_id
            logger.info(f"Submitted run with ID: {run_id}")
            logger.info(f"Waiting for run {run_id} to complete....")
            run_detail = created_run.wait_for_run_completion()
            _handle_job_end(run_detail)

            # clean up
            experiment = client.get_experiment(experiment_name=experiment_name)
            client.delete_experiment(experiment.id)
            logger.info("Done")

        except Exception as e:
            logger.error(f"ERROR: {e}")
            raise e
        finally:
            proc.terminate()


def _handle_job_end(run_detail):
    finished_run = run_detail.to_dict()["run"]
    created_at = finished_run["created_at"]
    finished_at = finished_run["finished_at"]
    duration_secs = (finished_at - created_at).total_seconds()
    status = finished_run["status"]
    logger.info(f"Run finished in {round(duration_secs)} seconds with status: {status}")

    if status != "Succeeded":
        raise Exception(f"Run failed: {run_detail.run.id}")


def build_load_image():
    output = subprocess.check_output(
        ["docker", "exec", f"{CLUSTER_NAME}-control-plane", "crictl", "images"]
    )
    if IMAGE_NAME in output.decode():
        logging.info(f"Image already in cluster.")
    else:
        logging.info(f"Image not found in cluster. Building and loading image...")
        subprocess.run([str(BUILD_FILE)], stdout=True)


@pytest.mark.order(6)
@pytest.mark.timeout(240)
@pytest.mark.skipif(IS_STANDALONE_KFP, reason="It is not Kubeflow")
def test_run_pipeline():
    # build the base docker image and load it into the cluster
    build_load_image()
    # submit and run pipeline
    run_pipeline(pipeline_file=str(PIPELINE_FILE), experiment_name=EXPERIMENT_NAME)


@pytest.mark.order(6)
@pytest.mark.timeout(240)
@pytest.mark.skipif(not IS_STANDALONE_KFP, reason="It is not standalone KFP")
def test_run_pipeline_standalone_kfp():
    # build the base docker image and load it into the cluster
    build_load_image()
    # submit and run pipeline
    run_pipeline_standalone_kfp(
        pipeline_file=str(PIPELINE_FILE), experiment_name=EXPERIMENT_NAME
    )


if __name__ == "__main__":
    test_run_pipeline()
