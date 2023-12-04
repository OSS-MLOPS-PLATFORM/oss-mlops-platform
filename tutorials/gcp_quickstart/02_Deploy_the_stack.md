<h1>Deployment</h1>

## 1. Prerequisites

- [curl](https://curl.se/)
- [docker](https://docs.docker.com/engine/install/ubuntu/)
- [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/)
- [kind](https://kind.sigs.k8s.io/docs/user/quick-start/#installation)

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