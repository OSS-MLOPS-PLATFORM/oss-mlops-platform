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

## Troubleshooting

### Error: namespace "kubeflow-user-example-com not found

This is not an error, and it is expected. Some of the things being deployed depend on other components, which need to be deployed and become ready first.
For example, the namespace `kubeflow-user-example-com` is created by a `kubeflow` component. That's why we deploy in a loop until everything is applied successfully:

```bash
while true; do
  if kubectl apply -f "$tmpfile"; then
      echo "Resources successfully applied."
      rm "$tmpfile"
      break
  else
      echo "Retrying to apply resources. Be patient, this might take a while..."
      sleep 10
  fi
done
```

Once the main `kubeflow` deployment is ready, the `kubeflow-user-example-com` namespace will be created, and the command should finish successfully.

However, if there is an underlying issue, the loop might never finish. In this case, you can check the status of the deployment with:

```bash
kubectl get pods --all-namespaces
```

Everything should be either in `Running` state, or being deployed (`ContainerCreating`). If there is an error, you will see it in the `STATUS` column.

If there is an error, you can check the logs of the pod with:

```bash
kubectl logs -n [NAMESPACE] [POD_NAME]
```