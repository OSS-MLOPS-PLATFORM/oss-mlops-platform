## Create Google Cloud resources

In this step, we will create a Google Cloud resources: a cloud storage bucket, an artifact registry repository, service accounts, and a GKE cluster.

## Pre-requisites

- [Preparation](./01_Preparation.md)

**The environment variables set in `Preparation` are expected to be set in your shell.**

## Create Google Cloud project

> If you have a Google Cloud project with billing enabled, skip this step.

Create a new Google Cloud project using your method of choice. The project must have billing enabled.

## Configure `gcloud`

Configure `gcloud` CLI to point to the correct project. For example:

```bash
gcloud config set project $PROJECT_ID
```

Check that you are on the right project and using the correct GCP account:

```bash
gcloud config list
```

Enable services:

```bash
gcloud services enable artifactregistry.googleapis.com storage-component.googleapis.com container.googleapis.com
```

## Create Google Cloud Storage (GCS) buckets

Create a bucket with [uniform bucket-level access](https://cloud.google.com/storage/docs/uniform-bucket-level-access):

```bash
gsutil mb -b on -l $REGION gs://$BUCKET_NAME
```

```bash
gsutil mb -b on -l $REGION gs://$BUCKET_NAME_MLFLOW
```

> `gsutil` command should be availble from `gcloud` installation.

Set up versioning to track remote in Google Cloud Storage buckets created before:

```bash
gsutil versioning set on gs://$BUCKET_NAME
gsutil versioning set on gs://$BUCKET_NAME_MLFLOW
```

## Create an artifact registry repository

Create the artifact registry repository:

```bash
gcloud artifacts repositories create $REPOSITORY_NAME \
    --repository-format=Docker  \
    --location=$REGION \
    --description="MLOps Docker images"
```

To confirm, you can navigate to "Artifact Registry (Repositories)" resource page on GCP console and check your newly created artifact registry.

## Create service accounts

Service accounts are needed for the following applications:

- MLflow
- Kubeflow + Kserve
- KServe  ???
- Optional: GKE nodes  ???

Create service accounts for each service, replacing the service account ID, description and display name as needed:

Create service accounts:

```bash
gcloud iam service-accounts create $MLFLOW_SERVICE_ACCOUNT_ID \
    --description="SA for MLflow in GKE" \
    --display-name="mlops-mlflow"
gcloud iam service-accounts create $KUBEFLOW_SERVICE_ACCOUNT_ID \
    --description="SA for Kubeflow in GKE" \
    --display-name="mlops-kfp"
gcloud iam service-accounts create $KSERVE_SERVICE_ACCOUNT_ID \
    --description="SA for KServe in GKE" \
    --display-name="mlops-kserve"
```

### Service account for GKE nodes


It is [not recommended](https://cloud.google.com/kubernetes-engine/docs/how-to/hardening-your-cluster#use_least_privilege_sa) to run GKE clusters using the Compute Engine default service account. Consider creating a dedicated IAM service account for GKE nodes.

Create the service account with the minimum required permissions:

```bash
gcloud iam service-accounts create $GKE_SA_NAME \
  --display-name=$GKE_SA_NAME

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member "serviceAccount:$GKE_SA_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
  --role roles/logging.logWriter

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member "serviceAccount:$GKE_SA_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
  --role roles/monitoring.metricWriter

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member "serviceAccount:$GKE_SA_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
  --role roles/monitoring.viewer

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member "serviceAccount:$GKE_SA_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
  --role roles/stackdriver.resourceMetadata.writer
```

In addition, give the service account permission to pull images from the newly created Artifact Registry repository:

```bash
gcloud artifacts repositories add-iam-policy-binding $REPOSITORY_NAME \
    --location=$REGION \
    --member="serviceAccount:$GKE_SA_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/artifactregistry.reader"
```

### Custom roles

A custom role is needed for the users to access Kubeflow the different services. Create the following YAML file and name it, for example, as `mlops-kfp-user.yaml`:

```yaml
title: mlops_kfp_user
description: Has access to retrieve GKE cluster credentials and port-forward to any service (including Kubeflow API) on GKE
stage: alpha
includedPermissions:
- container.clusters.get
- container.clusters.getCredentials
- container.clusters.list
- container.pods.get
- container.pods.list
- container.services.get
- container.services.list
- container.services.proxy
```

Define the role ID:

```bash

export KFP_USER_ROLE_ID=mlops_kfp_user

```

Create the role:

```bash

gcloud iam roles create $KFP_USER_ROLE_ID --project=$PROJECT_ID --file=mlops_kfp_user.yaml

```

### Policy bindings

Service accounts need to be assigned the following [roles](https://cloud.google.com/iam/docs/understanding-roles#predefined_roles):

- MLflow: Artifact Registry Reader (`roles/artifactregistry.reader`), Storage Object Viewer (`roles/storage.objectViewer`)
- Kubeflow: Artifact Registry Reader (`roles/artifactregistry.reader`), Storage Object Admin (`roles/storage.objectAdmin`)
- KServe: Storage Object Viewer (`roles/storage.objectViewer`)

> These roles grant access on project-level. In the future, we want to grant access only to specific buckets or repositories.

> See the appendix below for explanation why these roles are needed.

[//]: # (> The Artifact Registry Reader permission is only required if you patch Kubernetes service accounts with image pull secrets instead of attaching the permissions to the GKE service account.)

Add role binding for each service account and role, for your project:

```bash
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:SERVICE_ACCOUNT_ID@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="ROLE_NAME"
```

For example:

```bash
# MLflow
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$MLFLOW_SERVICE_ACCOUNT_ID@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/artifactregistry.reader"
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$MLFLOW_SERVICE_ACCOUNT_ID@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/storage.objectViewer"

## Kubeflow
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$KUBEFLOW_SERVICE_ACCOUNT_ID@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/storage.objectAdmin"
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$KUBEFLOW_SERVICE_ACCOUNT_ID@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/artifactregistry.reader"

# KServe
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$KSERVE_SERVICE_ACCOUNT_ID@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/storage.objectAdmin"
```

## Create a cluster in Google Kubernetes Engine (GKE)

Available machine types can be listed with

```bash
gcloud compute machine-types list
```

> See the [machine families documentation](https://cloud.google.com/compute/docs/machine-types) to pick the correct machine type. For production usage, you can choose a mainstream machine type such as `e2-standard-2` or `n2-standard-2`, which will use 2x resources compared to above.

> Inspect the following command before running it and modify as needed.

Create a Kubernetes cluster with similar settings to those created by AI Platform Kubeflow Pipelines installation:

```bash
gcloud beta container --project $PROJECT_ID clusters create $CLUSTER_NAME --zone $ZONE --no-enable-basic-auth --release-channel "stable" --machine-type $MACHINE_TYPE --image-type "COS_CONTAINERD" --disk-type "pd-standard" --disk-size "100" --metadata disable-legacy-endpoints=true --scopes "https://www.googleapis.com/auth/compute","https://www.googleapis.com/auth/devstorage.read_only","https://www.googleapis.com/auth/logging.write","https://www.googleapis.com/auth/monitoring","https://www.googleapis.com/auth/cloud-platform","https://www.googleapis.com/auth/servicecontrol","https://www.googleapis.com/auth/service.management.readonly","https://www.googleapis.com/auth/trace.append" --logging=SYSTEM,WORKLOAD --monitoring=SYSTEM --no-enable-ip-alias --network "projects/$PROJECT_ID/global/networks/default" --subnetwork "projects/$PROJECT_ID/regions/$REGION/subnetworks/default" --no-enable-intra-node-visibility --enable-autoscaling --no-enable-master-authorized-networks --addons HorizontalPodAutoscaling,HttpLoadBalancing,ApplicationManager,GcePersistentDiskCsiDriver --enable-autoupgrade --enable-autorepair --max-surge-upgrade 1 --max-unavailable-upgrade 0 --enable-shielded-nodes --node-locations $ZONE --workload-pool=$PROJECT_ID.svc.id.goog --min-nodes "1" --max-nodes $MAX_NUMBER_OF_NODES --service-account="$GKE_SA_NAME@$PROJECT_ID.iam.gserviceaccount.com"
```

The option `--workload-pool=...` enables [Workload Identity](https://cloud.google.com/kubernetes-engine/docs/how-to/workload-identity). You can remove this if you want to use service account keys to access Google Cloud services from pods.

The option `--service-account` sets the service account. Remove this if you want to use Compute Engine default service account for nodes. This simplifies setting access to, for example, Docker images but is not recommended for production environments. See the [documentation](https://cloud.google.com/kubernetes-engine/docs/how-to/hardening-your-cluster).

The command above creates a [single-zone cluster](https://cloud.google.com/kubernetes-engine/docs/concepts/types-of-clusters). If you are targeting production, see [here](https://cloud.google.com/kubernetes-engine/docs/concepts/types-of-clusters) to find correct type for your cluster.

This will take a few minutes. To confirm navigate to "Kubernetes Engine" resource page on GCP console and check your newly created cluster.

Update `kubeconfig` file with appropriate credentials and endpoint information to point `kubectl` at the newly-created cluster:

```bash
gcloud container clusters get-credentials $CLUSTER_NAME --zone=$ZONE
```

By default, credentials are written to `HOME/.kube/config`.

## Setup GKE usage metering tracking using a BigQuery dataset

This step helps understand GKE usage and connects it to billing. 
For more information please refer to [official doc](https://cloud.google.com/kubernetes-engine/docs/how-to/cluster-usage-metering).

If your project does not already have a dataset for tracking yet you can create a BigQuery dataset in the same region as your billing data, which is `EU` for Silo's case. 

```bash
RESOURCE_USAGE_DATASET=your_gke_tracking_dataset
LOCATION=EU

bq --location=$LOCATION mk -d \
--description "Dataset for GKE usage metering tracking" \
$PROJECT_ID:$RESOURCE_USAGE_DATASET
```
Then set up the tracking:

```bash
gcloud container clusters update $CLUSTER_NAME --resource-usage-bigquery-dataset $RESOURCE_USAGE_DATASET
```

Check that tracking is successfully setup:
```bash
gcloud container clusters describe $CLUSTER_NAME  --zone=europe-west1-b --format="value(resourceUsageExportConfig)"
```
Output should show the bigquery dataset tracking this cluster, for example:
```bash
bigqueryDestination={'datasetId': 'your-gke-tracking-dataset'};consumptionMeteringConfig={'enabled': True}

```

After this step dataset will start tracking the GKE usage of the new cluster. Data will be populated in the following tables under your tracking dataset:

* `gke_usage_eugke_cluster_resource_consumption`

* `gke_usage_eugke_cluster_resource_usage`


You can use the same dataset to track other clusters in the same project when you create new clusters. It's recommended to setup tracking for all the clusters upon creating the cluster. Note that the clusters can only be tracked by BigQuery datasets in the same projects. 


## Create Cloud SQL instance

Kubeflow Pipelines and MLflow use an SQL database to persist data. It is possible to use in-cluster databases for persisting data. However, **using a managed Cloud SQL instance is recommended for production purposes**. Skip this part if you do not want to use a managed Cloud SQL instance.

> If you have any trouble creating the instance or want to learn more, see the [official documentation](https://cloud.google.com/sql/docs/mysql/create-instance). Also see [pricing](https://cloud.google.com/sql/pricing).

Create a new database instance with [`gcloud sql instances create`](https://cloud.google.com/sdk/gcloud/reference/sql/instances/create):

```bash
gcloud sql instances create $CLOUDSQL_INSTANCE_NAME \
--project=$PROJECT_ID \
--database-version=MYSQL_8_0 \
--cpu=2 \
--memory=7680MB \
--storage-size=10 \
--storage-type=SSD \
--region=$REGION \
--assign-ip
```

See the [documentation](https://cloud.google.com/sql/docs/mysql/instance-settings) how to customize the settings. For example, consider adding `--storage-auto-increase` to automatically allocate more storage.

Set a strong password for the "root@%" MySQL user:

```bash
export CLOUDSQL_PASSWORD=$(python -c "import secrets; print(secrets.token_urlsafe(), end='')")
gcloud sql users set-password root \
--host=% \
--instance $CLOUDSQL_INSTANCE_NAME \
--password $CLOUDSQL_PASSWORD \
--project $PROJECT_ID
```

Create user for Cloud SQL Auth Proxy with no password:

```bash
gcloud sql users create mlops \
--host="cloudsqlproxy~%" \
--instance=$CLOUDSQL_INSTANCE_NAME \
--project $PROJECT_ID
```

This `mlops` user is later used to access Cloud SQL.

### Appendix: Required permissions

Services need the following permissions:

**MLflow**

- Read logged artifacts from Google Storage bucket
- Pull MLflow Docker image from artifact registry (if the permission is not attached to the node pool service account)
- Connect to Cloud SQL (only if using managed SQL database)

**Kubeflow**

- Read data from Storage bucket
- Write training artifacts to Storage bucket (if using managed GCS storage)
- Pull Docker image used for training from artifact registry (if the permission is not attached to the node pool service account)
- Connect to Cloud SQL (only if using managed SQL database)

**KServe**

- Read model artifacts from Storage bucket
