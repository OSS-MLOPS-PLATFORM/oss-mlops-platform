import subprocess
import logging
import time
import pathlib
from dotenv import load_dotenv
import os

import argparse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser()
parser.add_argument(
    "-t", "--timeout", help="Maximum to wait for.", required=False, type=float
)

ENV_FILE = pathlib.Path(__file__).parent.parent / "config.env"
load_dotenv(dotenv_path=ENV_FILE)

CLUSTER_NAME = os.getenv("CLUSTER_NAME")
assert CLUSTER_NAME is not None
CONTEXT_NAME = f"kind-{CLUSTER_NAME}"

subprocess.run(["kubectl", "config", "use-context", CONTEXT_NAME], stdout=True)


def all_pods_ready(namespace: str):
    output = subprocess.check_output(["kubectl", "get", "pods", "-n", namespace])

    logger.info("\n" + output.decode())

    for line in output.decode().strip().split("\n")[1:]:

        name, ready, status, restarts = line.split()[:4]

        # skip this pod which is always down
        if name.startswith("proxy-agent") and namespace == "kubeflow":
            continue

        if status != "Completed" and (ready[0] == "0" or status != "Running"):
            logger.info(f"Resources not ready (namespace={namespace}).")
            return False

    logger.info(f"All resources are ready (namespace={namespace}).")
    return True


def get_all_namespaces():
    out = subprocess.check_output(["kubectl", "get", "namespaces"]).decode()
    all_namespaces = [n.split()[0] for n in out.strip().split("\n")[1:]]
    return all_namespaces


def wait_deployment_ready(timeout: float = None):

    start_time = time.time()

    namespaces = get_all_namespaces()
    namespaces = [{"name": name, "ready": False} for name in namespaces]

    all_ready = False

    while not all_ready:

        for namespace in namespaces:
            if not namespace["ready"]:
                namespace["ready"] = all_pods_ready(namespace=namespace["name"])

        all_ready = all([namespace["ready"] for namespace in namespaces])

        if all_ready:
            logger.info(f"Cluster ready!")
            break
        else:
            if timeout and time.time() - start_time > timeout * 60:
                raise TimeoutError
            else:
                logger.info(f"Waiting for resources...")
                time.sleep(10)


if __name__ == "__main__":
    args = parser.parse_args()
    logger.info(vars(args))

    wait_deployment_ready(args.timeout)
