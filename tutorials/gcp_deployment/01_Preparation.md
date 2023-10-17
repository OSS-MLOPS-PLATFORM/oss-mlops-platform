# Preparation

In this step, we install the necessary tools and prepare the repository.

## Install tools

**`gcloud`**

Install [`gcloud`](https://cloud.google.com/sdk/gcloud) command-line tool following the [`instructions`](https://cloud.google.com/sdk/docs/install). 

Run `gcloud auth login` to authenticate and `gcloud init` to initiate.

Update `gcloud` components:

```
$ gcloud components update
```

**`kubectl`**

Install `kubectl` following the [instructions](https://kubernetes.io/docs/tasks/tools/) and ensure it is available in your `PATH`.

## Prepare the deployment repository

## Set variables

Create a file named `env.sh` in your working directory and fill in the values as follows:

```bash
# 1. Edit <placeholders>.
# 2. Other env vars are configurable, but with default values set below.

# Google Cloud project ID
export PROJECT_ID=<google-cloud-project-id>

# Google Cloud region
export REGION=europe-west1

# Google Cloud zone
export ZONE=europe-west1-b

export RESOURCE_SUFFIX=<your-suffix>

# Cloud Storage bucket for Kubeflow data and artifacts
# For example: gs://mlops-CLIENT-NAME
export BUCKET_NAME=mlops-${RESOURCE_SUFFIX}

# MLflow storage bucket
export BUCKET_NAME_MLFLOW=mlflow-${RESOURCE_SUFFIX}

# Artifact Registry Docker repository name
# For example: mlops-CLIENT-NAME
export REPOSITORY_NAME=mlops-${RESOURCE_SUFFIX}

# GKE cluster name
# For example: mlops-CLIENT-NAME
export CLUSTER_NAME=mlops-${RESOURCE_SUFFIX}

# GKE cluster machine type
export MACHINE_TYPE="e2-standard-4"

# MLflow Google service account name
export MLFLOW_SERVICE_ACCOUNT_ID=mlops-mlflow-${RESOURCE_SUFFIX}

# Kubeflow pipeline runner Google service accountIAM
export KUBEFLOW_SERVICE_ACCOUNT_ID=mlops-kfp-${RESOURCE_SUFFIX}

# KServe Google service account
export KSERVE_SERVICE_ACCOUNT_ID=mlops-kserve-${RESOURCE_SUFFIX}

# GKE Google Service account
export GKE_SA_NAME=mlops-gke-${RESOURCE_SUFFIX}

# Only needed if you use Cloud SQL as managed database
export CLOUDSQL_INSTANCE_NAME=mlops-${RESOURCE_SUFFIX}

# Only needed if you use storage bucket for artifacts
export RESOURCE_PREFIX=mlops

# max number of nodes
export MAX_NUMBER_OF_NODES="5"
```

Set the environment variables in your shell:

```bash
source env.sh
```

> As of March 2021, `europe-north1` does not have GPUs available. See [availability](https://cloud.google.com/compute/docs/gpus/gpu-regions-zones).
> Take this into account when filling in `REGION` and `ZONE`.

**Variables must be set throughout the rest of this guide.**


