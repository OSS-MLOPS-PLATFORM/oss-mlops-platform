# Deploy Kubeflow

In this step, we deploy Kubeflow Pipelines (KFP) to our GKE cluster.

## Pre-requisites

- [Preparation](./01_Preparation.md)
- [Create GCP resources](./02_Create_GCP_Resources.md)

**The environment variables set in `Preparation` are expected to be set in your shell.**

Check if the cluster credentials are retrieved:

```bash
gcloud container clusters get-credentials $CLUSTER_NAME --zone=$ZONE
```

### Prepare `kubectl` context

Check your current context in `kubectl` and make sure it is pointing to the target cluster for this task. 

```bash
kubectl config current-context
```

Output format in `gke_[PROJECT_ID]_[ZONE]_[CLUSTER_NAME]`

Switch `kubectl` to the right context by modifying the variables if necessary:

```
kubectl config use-context gke_${PROJECT_ID}_${ZONE}_${CLUSTER_NAME}
```


## Option 1: Deploy using in-cluster MySQL and storage bucket (MinIO) for artifacts


Render manifests:

```bash
kustomize build deployment/kubeflow/manifests/example
```

See differences to existing deployment:

```bash
kustomize build deployment/kubeflow/manifests/example | kubectl diff -f -
```

Deploy:

```bash
kustomize build deployment/kubeflow/manifests/apps/pipeline/upstream/cluster-scoped-resources | kubectl apply -f -
```

```bash
kustomize build deployment/kubeflow/manifests/example | kubectl apply -f -
```

> **Deployment will take several minutes.** If you see any errors in the previous
> command output, it could be a simple race condition error. Try running the command
> again.

Check status of the pods with:

```bash
kubectl get pods --all-namespaces
```

All pods should be in `Running` state.


## Custom Kubeflow resources

In order to run the [demo notebooks](../tutorials/demo_notebooks) and other use-cases, we need to create these two additional resources:

- A secret that MLflow can use to access the storage bucket (MinIO): [aws-secret.yaml](../../deployment/kubeflow-custom/aws-secret.yaml)
- A service account to allow Kserve to access the storage bucket (MinIO) where the model artifacts are stored: [kserve-sa.yaml](../../deployment/kubeflow-custom/kserve-sa.yaml)

```bash
kubectl apply -k deployment/kubeflow-custom
```

## Access Kubeflow dashboard

Run the following to port-forward Istio's Ingress-Gateway to local port `8080`:

```sh
kubectl port-forward svc/istio-ingressgateway -n istio-system 8080:80
```

After running the command, you can access the Kubeflow Central Dashboard at [http://localhost:8080/](http://localhost:8080/).

You should see the login screen. You can use the default user's credential to login. 

The default email address is `user@example.com` and the default password is `12341234`.


## Set up access to Google Cloud resources

We need to ensure containers running in Kubeflow Pipelines can access Google Cloud services like storage buckets. [Workload identity](https://cloud.google.com/kubernetes-engine/docs/concepts/workload-identity) is the recommended way. Alternatively, one can export service account keys and store them as Kubernetes secrets.

### Alternative 1: Workload identity (recommended)

Here we setup access using [workload identity federation](https://cloud.google.com/kubernetes-engine/docs/how-to/workload-identity).

**This step is only required when deploying Option 2.** Allow the Kubernetes service account `default-editor` to impersonate the IAM Kubeflow service account by adding an IAM policy binding between the two service accounts. This binding allows the Kubernetes service account to act as the IAM service account:

```bash
gcloud iam service-accounts add-iam-policy-binding $KUBEFLOW_SERVICE_ACCOUNT_ID@$PROJECT_ID.iam.gserviceaccount.com \
    --role roles/iam.workloadIdentityUser \
    --member "serviceAccount:$PROJECT_ID.svc.id.goog[kubeflow-user-example-com/default-editor]"
```

> The part `[kubeflow/pipeline-runner]` refers to the Kubernetes service account `default-editor` in namespace `kubeflow-user-example-com`. Adjust accordingly if needed.

Annotate the Kubernetes service account with the email address of the IAM service account:

```bash
kubectl -n kubeflow-user-example-com annotate serviceaccount default-editor iam.gke.io/gcp-service-account=$KUBEFLOW_SERVICE_ACCOUNT_ID@$PROJECT_ID.iam.gserviceaccount.com
```

### Alternative 2: Service account keys

KFP service account `pipeline-runner` also needs to read and write data from/to Cloud Storage. Add the key as secret named `user-gcp-sa`:

```bash
kubectl create secret -n kubeflow generic user-gcp-sa --from-file=user-gcp-sa.json=kfp-sa-key.json
```

This secret `user-gcp-sa` needs to be configured in Kubeflow pipeline step definitions to give access to Cloud Storage. For example:

```python
from kfp.gcp import use_gcp_secret
# ...
pull_data_step = ... # Define Kubeflow Pipeline step
pull_data_step.apply(use_gcp_secret(secret_name="user-gcp-sa"))
```

## Create Kubeflow secret

Create the necessary secrets for KFP to access the storage bucket:

```bash
kubectl apply -k deployment/custom/kubeflow-custom/env/kubeflow
```

## Creating User Profiles

To see how to create user profiles, please refer to official documentation: [link](https://www.kubeflow.org/docs/components/multi-tenancy/getting-started/).


## Troubleshooting

### 1. Check the status of the pods

```bash
kubectl get pods -n kubeflow
```

### 2. Kubeflow known issues

Race condition errors can occur when deploying Kubeflow. If this happens, delete the Kubeflow namespace and redeploy the stack.

```bash
kubectl delete ns kubeflow

while ! kustomize build deployment | kubectl apply -f -; do echo "Retrying to apply resources"; sleep 10; done
```

Sometimes, just deleting the failing pod, so that it gets recreated, will fix the issue. 

```bash
kubectl delete pod -n kubeflow <pod_name>
```