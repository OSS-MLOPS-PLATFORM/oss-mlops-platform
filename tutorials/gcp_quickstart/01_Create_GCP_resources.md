<h1>Create Google Cloud resources</h1>

## Set environment variables

```bash
export REPOSITORY_NAME=rd-kubeflow-test

# Google Cloud project ID
export PROJECT_ID=silo-mlops-stack-1

# Google Cloud region
export REGION=europe-north1

# Google Cloud zone
export ZONE=europe-north1-b

# GKE cluster name
export CLUSTER_NAME=rd-kubeflow-test

# GKE cluster machine type
export MACHINE_TYPE="e2-standard-4"

# Kubeflow pipeline runner Google service accountIAM
export KFP_SERVICE_ACCOUNT_ID=kubeflow-test-kfp-sa

# max number of nodes
export MAX_NUMBER_OF_NODES="5"
```

## Create an artifact registry repository

Create the artifact registry repository:

```bash
gcloud artifacts repositories create $REPOSITORY_NAME \
    --repository-format=Docker  \
    --location=$REGION \
    --description="Kubeflow test repository"
```

To confirm, you can navigate to "Artifact Registry (Repositories)" resource page on GCP console and check your newly created artifact registry.

## Create service accounts

Throughout the guide, we need to provide the workloads running in Kubernetes access to Google Cloud services. See [here](https://cloud.google.com/kubernetes-engine/docs/concepts/security-overview) for the list of all options.

### Service accounts

Service accounts are needed for the following applications:

- Kubeflow Pipelines
- Optional: GKE nodes

Create service accounts for each service, replacing the service account ID, description and display name as needed:

Create service accounts:

```bash
gcloud iam service-accounts create $KFP_SERVICE_ACCOUNT_ID \
    --description="SA for Kubeflow Pipelines in GKE" \
    --display-name="kubeflow-test-kfp-sa"
```

### Policy bindings

Service accounts need to be assigned the following [roles](https://cloud.google.com/iam/docs/understanding-roles#predefined_roles):

- Kubeflow Pipelines: Artifact Registry Reader (`roles/artifactregistry.reader`)

[//]: # (> The Artifact Registry Reader permission is only required if you patch Kubernetes service accounts with image pull secrets instead of attaching the permissions to the GKE service account.)


```bash

# Kubeflow Pipelines
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$KFP_SERVICE_ACCOUNT_ID@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/artifactregistry.reader"
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
gcloud beta container --project $PROJECT_ID clusters create $CLUSTER_NAME --zone $ZONE --no-enable-basic-auth --release-channel "stable" --machine-type $MACHINE_TYPE --image-type "cos_containerd" --disk-type "pd-standard" --disk-size "100" --metadata disable-legacy-endpoints=true --scopes "https://www.googleapis.com/auth/compute","https://www.googleapis.com/auth/devstorage.read_only","https://www.googleapis.com/auth/logging.write","https://www.googleapis.com/auth/monitoring","https://www.googleapis.com/auth/cloud-platform","https://www.googleapis.com/auth/servicecontrol","https://www.googleapis.com/auth/service.management.readonly","https://www.googleapis.com/auth/trace.append" --num-nodes "3" --logging=SYSTEM,WORKLOAD --monitoring=SYSTEM --no-enable-ip-alias --network "projects/$PROJECT_ID/global/networks/default" --subnetwork "projects/$PROJECT_ID/regions/$REGION/subnetworks/default" --no-enable-intra-node-visibility --enable-autoscaling --min-nodes "1" --max-nodes $MAX_NUMBER_OF_NODES --no-enable-master-authorized-networks --addons HorizontalPodAutoscaling,HttpLoadBalancing,ApplicationManager,GcePersistentDiskCsiDriver --enable-autoupgrade --enable-autorepair --max-surge-upgrade 1 --max-unavailable-upgrade 0 --enable-shielded-nodes --node-locations $ZONE --workload-pool=$PROJECT_ID.svc.id.goog
```

The option `--workload-pool=...` enables [Workload Identity](https://cloud.google.com/kubernetes-engine/docs/how-to/workload-identity). You can remove this if you want to use service account keys to access Google Cloud services from pods.

The command above creates a [single-zone cluster](https://cloud.google.com/kubernetes-engine/docs/concepts/types-of-clusters). If you are targeting production, see [here](https://cloud.google.com/kubernetes-engine/docs/concepts/types-of-clusters) to find correct type for your cluster.

This will take a few minutes. To confirm navigate to "Kubernetes Engine" resource page on GCP console and check your newly created cluster.

Update `kubeconfig` file with appropriate credentials and endpoint information to point `kubectl` at the newly-created cluster:

```bash
gcloud container clusters get-credentials $CLUSTER_NAME --zone=$ZONE
```

By default, credentials are written to `HOME/.kube/config`.
