<h1>Deploy Kubeflow Pipelines (KFP)</h1>

## Pre-requisites

- [1_Setup_local_cluster.md](1_Setup_local_cluster.md)

## 1. Prepare `kubectl` context

Check your current context in `kubectl` and make sure it is pointing to the target cluster we created in the previous tutorial (`kind-mlops-platform`). 

```bash
# check current context
kubectl config current-context
```

Switch `kubectl` to the right context by modifying the variables if necessary:

```bash
kubectl config use-context kind-mlops-platform
```

You can also list all the available contexts with:

```bash
# list all contexts
kubectl config get-contexts
```

## 2. Install Kubeflow

Render manifests:

```bash
kustomize build deployment/kubeflow/manifests/in-cluster-setup
```

See differences to existing deployment:

```bash
kustomize build deployment/kubeflow/manifests/in-cluster-setup | kubectl diff -f -
```

Deploy:

```bash
kustomize build deployment/kubeflow/manifests/in-cluster-setup | kubectl apply -f -
```

> **Deployment will take several minutes.** If you see any errors in the previous
> command output, it could be a simple race condition error. Try running the command
> again.

Check status of the pods with:

```bash
kubectl get pods --all-namespaces
```

All pods should be in `Running` state.


## Access Kubeflow dashboard

Run the following to port-forward Istio's Ingress-Gateway to local port `8080`:

```sh
kubectl port-forward svc/istio-ingressgateway -n istio-system 8080:80
```

After running the command, you can access the Kubeflow Central Dashboard at [http://localhost:8080/](http://localhost:8080/).

You should see the login screen. You can use the default user's credential to login. 

The default email address is `user@example.com` and the default password is `12341234`.


## 3. Create AWS secret for MLflow access

Create a secret to allow Kubeflow and Kserve to access the MLflow MinIO storage:

```bash
kubectl apply -f deployment/custom/aws-secret.yaml
```

## 4. Create service account for kserve access to the MLflow MinIO storage

```bash
kubectl apply -f deployment/custom/kserve-sa.yaml
```

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

Sometimes, just deleting the failing pod, so that it get recreated, will fix the issue. 

```bash
kubectl delete pod -n kubeflow <pod_name>
```