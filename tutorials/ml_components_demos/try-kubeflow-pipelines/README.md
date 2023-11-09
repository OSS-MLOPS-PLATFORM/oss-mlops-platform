# Sample Kubeflow component and pipeline

This is a sample of a Kubeflow Pipeline component and pipeline adapted from [here](https://github.com/kubeflow/pipelines/tree/sdk/release-1.8/components/sample/keras/train_classifier).

The purpose is to show how to create a simple pipeline component and run a KFP pipeline.
By default, the example uses a local Kind cluster (`kind-ep`) and the local docker repository. Modify the files appropriately for your own environment if needed.

This example uses custom containers for components. You may also want to learn about [building Python function-based components](https://www.kubeflow.org/docs/components/pipelines/sdk-v2/python-function-components/) as an alternative approach.

This example uses [Pipelines SDK v2](https://www.kubeflow.org/docs/components/pipelines/sdk-v2/).

## Pre-requisites

Ensure your `kubectl` has correct context pointing to the desired cluster. For example, for the `kind-ep` cluster:

```bash
kubectl config use-context kind-kind-ep
```

## Push container image

The file [`train.py`](./train.py) contains sample for model training. MLflow is used for experiment tracking.

The file [`Dockerfile`](./Dockerfile) contains the commands to assemble a Docker image for training.

Image is built [`build_image.sh`](./build_image.sh). Read through the script. By default, images are loaded into the local cluster directly from the local docker repository using the `kind load docker-image` command.

Build and load the image into the cluster:

```bash
./build_image.sh
```

## Create component

Kubeflow pipeline component for training is defined in [`component.yaml`](./component.yaml). See the documentation on [component specification](https://www.kubeflow.org/docs/components/pipelines/reference/component-spec/) to understand how components are defined. In brief, every component has 

- metadata such as name and description
- implementation specifying how to execute the component instance: Docker image, command and arguments
- interface specifying the inputs and outputs

Update the container image under `implementation.container.image` so that it matches the image pushed with `build_image.sh`.

## Create pipeline

The file [`pipeline.py`](./pipeline.py) contains the definition for the Kubeflow pipeline:

```python
# pipeline.py
import kfp

# Load component from YAML file
train_op = kfp.components.load_component_from_file('component.yaml')

@kfp.dsl.pipeline(name='Example Kubeflow pipeline', description='Pipeline to test an example component')
def pipeline():
    train_task = train_op()

def compile():
    kfp.compiler.Compiler().compile(
        pipeline_func=pipeline,
        package_path='pipeline.yaml'
    )

if __name__ == '__main__':
    compile()
```

Compile the pipeline to `pipeline.yaml`:

```bash
python pipeline.py
```

Submit pipeline run to Kubeflow Pipelines:

```bash
python submit.py
```

You can also submit the pipeline file manually in Kubeflow Pipelines UI.

## Dashboards

The default way of accessing Kubeflow is via port-forward. This enables you to get started quickly without imposing any requirements on your environment. Run the following to port-forward Istio's Ingress-Gateway to local port `8080`:

```sh
kubectl port-forward svc/istio-ingressgateway -n istio-system 8080:80
```

After running the command, you can access the Kubeflow Central Dashboard by doing the following:

1. Open your browser and visit [http://localhost:8080/](http://localhost:8080/). You should get the Dex login screen.
2. Login with the default user's credential. The default email address is `user@example.com` and the default password is `12341234`.

To access MLFlow UI, forward a local port to MLFlow server with:

```bash
kubectl -n mlflow port-forward svc/mlflow 5000:5000
```

Then access the MLflow UI at [`http://localhost:5000`](http://localhost:5000).
