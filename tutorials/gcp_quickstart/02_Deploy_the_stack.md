<h1>Deployment</h1>

## 1. Prerequisites

- [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/)
- [kustomize](https://kubectl.docs.kubernetes.io/installation/kustomize/)

## 2. Deploy the stack

Deploy all the components of the platform with:

```bash
while ! kustomize build deployment | kubectl apply -f -; do echo "Retrying to apply resources"; sleep 10; done
```

## Troubleshooting

### 1. Check the status of the pods

```bash
kubectl get pods -A
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