## Installation

> Supported OS: Linux, macOS.

Change the settings in [`config.env`](config.env) if needed.

Install the experimentation platform with:

```bash
./setup.sh [--test] [--debug]
```

- `--test`: Use this flag to run the tests right after installation.
- `--debug`: Print extra output information.

> **WARNING:** Using the `--test` flag will install the `requirements-tests.txt` in your current python environment.

## Test the deployment (manually)

If you just deployed the platform, it will take a while to become ready. You can use
the following script to make sure the deployment is ready and all resource are running
correctly.

```bash
# install test requirements
pip install -r tests/requirements-tests.txt
```

```bash
# wait for the deployment to be ready
python tests/wait_deployment_ready.py --timeout 30
```

Run the tests with:

```bash
pytest tests/ [-vrP] [--log-cli-level=INFO]
```

*These are the same tests that are run automatically if you use the `--test` flag on installation.*


## Deleting the deployment

Delete the cluster:
```bash
# e.g. $ kind delete cluster --name kind-ep
kind delete cluster --name [CLUSTER_NAME]
```

If you also installed the local docker registry (`config.env` > `INSTALL_LOCAL_REGISTRY="true"`):

```bash
# check if it is running (kind-registry)
$ docker ps

CONTAINER ID   IMAGE        COMMAND                  CREATED        STATUS        PORTS                       NAMES
6d7e3ef4e1fe   registry:2   "/entrypoint.sh /etc…"   2 hours ago    Up 2 hours    127.0.0.1:5001->5000/tcp    kind-registry
```

```bash
# delete it
docker rm -f $(docker ps -aqf "name=kind-registry")
```
