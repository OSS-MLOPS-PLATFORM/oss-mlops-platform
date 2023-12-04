<h1>Deploy MLflow</h1>

In this guide, we deploy [MLflow](https://mlflow.org/) tracking server to Kubernetes.

[MLflow](https://mlflow.org/) is an open source platform to manage the ML lifecycle, including experimentation, reproducibility, deployment, and a central model registry.

The deployment uses [MinIO](https://min.io/) as artifact store as a location for large data and training artifacts (for example, models).
MinIO is a High Performance Object Storage native to Kubernetes and API compatible with Amazon S3 cloud storage service.

MLflow also requires an SQL database as backend store. This deployment uses an in-cluster PostgreSQL database for that purpose.

## Pre-requisites

- [1_Setup_local_cluster.md](1_Setup_local_cluster.md)


## Understand Kustomize

Kubernetes' resources are deployed using [Kustomize](https://kustomize.io/).
See [this presentation](https://docs.google.com/presentation/d/1-j7ux5-P9HcftKlXM9KHKgrG0EgwwGEKE3f01Sp0oes/edit?usp=sharing)
and [this tutorial](https://kubernetes.io/docs/tasks/manage-kubernetes-objects/kustomization/)
to understand the basics.

## MLflow Docker image

Dockerfile use to build the docker image for MLflow can be found [`here`](/docker/mlflow).

## Deploy MLFlow

The folder [`deployment/mlflow`](/deployment/mlflow) contains a [Kustomize](https://kubernetes.io/docs/tasks/manage-kubernetes-objects/kustomization/) [overlay](https://kubernetes.io/docs/tasks/manage-kubernetes-objects/kustomization/#bases-and-overlays)
that can be used for deploying MLFlow.

Feel free to replace the default secrets in [`mlflow/secret.env`](/deployment/mlflow/secret.env).

Print Kubernetes resources that you would deploy:

```bash
kubectl kustomize deployment/mlflow/env/local
```

Deploy the stack:

```bash
kubectl apply -k deployment/mlflow/env/local
```

## Check deployment health

Wait until pods labeled as `mlflow` and `postgres` become ready:

```bash
kubectl -n mlflow wait --for=condition=ready pod -l app=postgres
kubectl -n mlflow wait --for=condition=ready pod -l app=mlflow
kubectl -n mlflow wait --for=condition=ready pod -l app=mlflow-minio
```

See the pods running in `mlflow` namespace. All pods should be ready and running.

```bash
$ kubectl -n mlflow get pods
mlflow-7b7c7b6d68-mflj4         1/1     Running   0          13m
mlflow-minio-674cb5cc55-hlkrq   1/1     Running   0          3h32m
postgres-547474dc58-8fscf       1/1     Running   0          3h37m
```

If anything is wrong, you can read the pod logs with:

```bash
kubectl -n mlflow logs -l app=mlflow
```

## Access MLflow UI

To access MLFlow UI locally, forward a local port to MLFlow server:

```bash
kubectl -n mlflow port-forward svc/mlflow 5000:5000
```

Now MLFlow's UI should be reachable at [`http://localhost:5000`](http://localhost:5000).

## Access Minio UI

To access MinIO UI locally, forward a local port to MinIO console:

```bash
kubectl -n mlflow port-forward svc/mlflow-minio-service 9001:9001
```

Now MinIO's UI should be reachable at [`http://localhost:9001`](http://localhost:9001).

The default user and password are both `minioadmin`. They are defined in the [`mlflow/config.env`](/deployment/mlflow/config.env) and [`mlflow/secret.env`](/deployment/mlflow/secret.env) environment files.

To access MinIO Server locally, forward a local port to MinIO server:

```bash
kubectl -n mlflow port-forward svc/mlflow-minio-service 9000:9000
```

> In a later tutorial, we will see how to set up the ingress controller so that we can access
> mlflow and minio without having to use `port-forward`.

## Try out MLflow

Follow the instructions of the [MLflow sample](../resources/try-mlflow/README.md)
to test the MLflow/MinIO setup.
