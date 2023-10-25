import subprocess
import pathlib
from dotenv import load_dotenv
import os

ENV_FILE = pathlib.Path(__file__).parent.parent / "config.env"
load_dotenv(dotenv_path=ENV_FILE)

CLUSTER_NAME = os.getenv("CLUSTER_NAME")
assert CLUSTER_NAME is not None
CONTEXT_NAME = f"kind-{CLUSTER_NAME}"

HOST_IP = os.getenv("HOST_IP")
assert HOST_IP is not None

# MLFLOW
MLFLOW_ENV_FILE = pathlib.Path(__file__).parent.parent / "deployment/mlflow/env/local" / "config.env"
MLFLOW_SECRETS_FILE = pathlib.Path(__file__).parent.parent / "deployment/mlflow/env/local" / "secret.env"

load_dotenv(dotenv_path=MLFLOW_ENV_FILE, override=True)
AWS_ACCESS_KEY_ID = os.getenv("MINIO_ACCESS_KEY")
assert AWS_ACCESS_KEY_ID is not None

load_dotenv(dotenv_path=MLFLOW_SECRETS_FILE, override=True)
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
assert AWS_SECRET_ACCESS_KEY is not None


def pytest_sessionstart(session):
    """
    Called after the Session object has been created and
    before performing collection and entering the run test loop.
    """
    print(f"Set up kubectl context ({CONTEXT_NAME}) before starting the tests.")

    subprocess.run(["kubectl", "config", "use-context", CONTEXT_NAME], stdout=True)
