# Deploy MLflow

In this guide, we deploy [MLflow tracking server](https://www.mlflow.org/docs/latest/tracking.html#mlflow-tracking-servers) to Kubernetes.

The deployment uses Google Storage bucket as [artifact store](https://www.mlflow.org/docs/latest/tracking.html#artifact-stores) as a location for large data and training artifacts (for example, models).

MLflow also requires an SQL database as [backend store](https://www.mlflow.org/docs/latest/tracking.html#backend-stores). There are two deployment alternatives:

- using in-cluster PostgreSQL database
- using [Cloud SQL](https://cloud.google.com/sql)

Using in-cluster database is easier to setup and cheaper to run. However, using Cloud SQL is recommended for production deployments.

## Pre-requisites

- [Preparation](./01_Preparation.md)
- [Create GCP resources](./02_Create_GCP_Resources.md)

**The environment variables set in `Preparation` are expected to be set in your shell.**

## Understand Kustomize

Kubernetes resources are deployed using [Kustomize](https://kustomize.io/). See [this presentation](https://docs.google.com/presentation/d/1-j7ux5-P9HcftKlXM9KHKgrG0EgwwGEKE3f01Sp0oes/edit?usp=sharing) and [this tutorial](https://kubernetes.io/docs/tasks/manage-kubernetes-objects/kustomization/) to understand the basics.

## MLflow Docker image

> TODO: Currently the image is located in a Silo's public repository.

## Setup Kustomize overlay

The folder [`deployment/mlflow`](/deployment/mlflow) contains a [Kustomize](https://kubernetes.io/docs/tasks/manage-kubernetes-objects/kustomization/)
[overlay](https://kubernetes.io/docs/tasks/manage-kubernetes-objects/kustomization/#bases-and-overlays)
that can be used for deploying MLFlow. The base can be found in [`mlflow/base`](/deployment/mlflow/base) repository.

Modify the value of `DEFAULT_ARTIFACT_ROOT` in [deployment/mlflow/base/config.env](/deployment/mlflow/base/config.env)
by filling in the URL of the Google Storage bucket that you created before (`BUCKET_NAME_MLFLOW`).

## MLflow deployment

### Alternative 1: Using Cloud SQL

In the Cloud SQL instance you created before, create database with name `mlflowdb`:

```bash
gcloud sql databases create mlflowdb \
--instance=$CLOUDSQL_INSTANCE_NAME \
--project=$PROJECT_ID
```

Modify the value of `GCP_CLOUDSQL_INSTANCE_NAME` in [deployment/mlflow/env/gcp-cloudsql/params.env](/deployment/mlflow/env/gcp-cloudsql/params.env)
by filling in your Cloud SQL instance (`<PROJECT_ID>.<REGION>.<CLOUDSQL_INSTANCE_NAME>`).

Ensure the manifest is valid:

```bash
# deployment/mlflow
kubectl kustomize deployment/mlflow/env/gcp-cloudsql
```

Deploy MLflow:

```bash
kubectl apply -k deployment/mlflow/env/gcp-cloudsql
```

### Alternative 2: Using in-cluster database


Ensure the manifest is valid:

```bash
# deployment/mlflow
kubectl kustomize deployment/mlflow/env/gcp
```

Deploy MLflow:

```bash
kubectl apply -k deployment/mlflow/env/gcp
```


## Set up access to Google Cloud resources

We need to setup access to Google Cloud services for MLflow. [Workload identity](https://cloud.google.com/kubernetes-engine/docs/concepts/workload-identity) is the recommended way. Alternatively, one can export service account keys and store them as Kubernetes secrets.

> You can also use the Compute Engine default service account of your nodes. If you do not specify a service account during node pool creation, GKE uses the Compute Engine default service account for the project. The Compute Engine service account is shared by all workloads deployed on that node. This can result in over-provisioning of permissions, which violates the principle of least privilege and is inappropriate for multi-tenant clusters.

### Workload Identity Federation (recommended)

Here we se tup access using [workload identity federation](https://cloud.google.com/kubernetes-engine/docs/how-to/workload-identity).

Allow the Kubernetes service account `mlflow` in `mlflow` namespace to impersonate the IAM MLflow service account by adding an IAM policy binding between the two service accounts. This binding allows the Kubernetes service account to act as the IAM service account:

```bash
gcloud iam service-accounts add-iam-policy-binding $MLFLOW_SERVICE_ACCOUNT_ID@$PROJECT_ID.iam.gserviceaccount.com \
    --role roles/iam.workloadIdentityUser \
    --member "serviceAccount:$PROJECT_ID.svc.id.goog[mlflow/mlflow]"
```

> The part `[mlflow/mlflow]` refers to Kubernetes service account `mlflow` in namespace `mlflow`. Adjust accordingly if needed.

Annotate the Kubernetes service account with the email address of the IAM service account:

```bash
kubectl -n mlflow annotate serviceaccount mlflow iam.gke.io/gcp-service-account=$MLFLOW_SERVICE_ACCOUNT_ID@$PROJECT_ID.iam.gserviceaccount.com
```

### Cloud SQL access (only for Cloud SQL)

> Only needed when using the alternative 1: Using Cloud SQL

To allow MLflow to access Cloud SQL, we need to grant the kubernetes service account
`mlflow-cloudsql-proxy` in namespace mlflow with permissions to access Cloud SQL.


Create a new GCP service account:

```bash
export MLFLOW_CLOUDSQL_SERVICE_ACCOUNT_ID=mlflow-csql-proxy-${RESOURCE_SUFFIX}
```

```bash
gcloud iam service-accounts create $MLFLOW_CLOUDSQL_SERVICE_ACCOUNT_ID \
    --description="SA for MLflow CloudSQL proxy in GKE" \
    --display-name="mlops-mlflow-cloudsql-proxy"
````

Grant the service account with permissions to access Cloud SQL:

```bash
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$MLFLOW_CLOUDSQL_SERVICE_ACCOUNT_ID@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/cloudsql.client"
````

Allow the Kubernetes service account `mlflow-cloudsql-proxy` in `mlflow` namespace to
impersonate the IAM MLflow CloudSQL service account.

```bash
gcloud iam service-accounts add-iam-policy-binding $MLFLOW_CLOUDSQL_SERVICE_ACCOUNT_ID@$PROJECT_ID.iam.gserviceaccount.com \
    --role roles/iam.workloadIdentityUser \
    --member "serviceAccount:$PROJECT_ID.svc.id.goog[mlflow/mlflow-cloudsql-proxy]"
```

Annotate the Kubernetes service account with the email address of the IAM service account:

```bash
kubectl -n mlflow annotate serviceaccount mlflow-cloudsql-proxy iam.gke.io/gcp-service-account=$MLFLOW_CLOUDSQL_SERVICE_ACCOUNT_ID@$PROJECT_ID.iam.gserviceaccount.com
```

## Check deployment health

Wait until pods labeled as `mlflow` and `postgres` become ready:

```bash
kubectl -n mlflow wait --for=condition=ready pod -l app=mlflow
kubectl -n mlflow wait --for=condition=ready pod -l app=postgres
```

See the pods running in `mlflow` namespace. All pods should be ready and running.

```bash
$ kubectl -n mlflow get pods
NAME                       READY   STATUS    RESTARTS   AGE
mlflow-ff6c958b8-p5whr     1/1     Running   1          25h
postgres-989f7bcff-kmt86   1/1     Running   1          25h
```

If anything is wrong, you can read the pod logs with:

```bash
kubectl -n mlflow logs -l app=mlflow
```

To access MLFlow UI locally, forward a local port to MLFlow server:

```bash
kubectl -n mlflow port-forward svc/mlflow 5000:5000
```

Now MLFlow's UI should be reachable at [`http://localhost:5000`](http://localhost:5000).