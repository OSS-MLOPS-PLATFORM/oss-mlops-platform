# Ray Setup

## TOC
  - [1. Install KubeRay operator](#1-install-kuberay-operator)
  - [2. Install Ray cluster](#2-install-ray-cluster)
  - [3. Connect to Ray and run a job (via Kubeflow)](#3-connect-to-ray-and-run-a-job-via-kubeflow)
    - [3.1 Forward the port of Istio’s Ingress-Gateway](#31-forward-the-port-of-istios-ingress-gateway)
    - [3.2 Create a JupyterLab via Kubeflow Central Dashboard](#32-create-a-jupyterlab-via-kubeflow-central-dashboard)
    - [3.3 Run a Ray job](#33-run-a-ray-job)
  - [4. Access Ray dashboard](#4-access-ray-dashboard)
  - [5. Connect to Ray cluster from local machine](#5-connect-to-ray-cluster-from-local-machine)

## Prerequisites

- [Helm](https://helm.sh/)

    ```bash
    # you can use the install_helm.sh script to install Helm if you haven't already
    bash scripts/install_helm.sh
    ```

## 1. Install KubeRay operator

```bash
helm repo add kuberay https://ray-project.github.io/kuberay-helm/
helm repo update

# Install both CRDs and KubeRay operator v1.0.0.
helm install kuberay-operator kuberay/kuberay-operator --version 1.0.0

# Confirm that the operator is running in the namespace `default`.
kubectl get pods
# NAME                                READY   STATUS    RESTARTS   AGE
# kuberay-operator-7fbdbf8c89-pt8bk   1/1     Running   0          27s
```

## 2. Install Ray cluster

```bash
# Create a RayCluster CR, and the KubeRay operator will reconcile a Ray cluster
# with 1 head Pod and 1 worker Pod.
helm install raycluster kuberay/ray-cluster --version 1.0.0 --set image.tag=2.7.0

# Check RayCluster
kubectl get pod -l ray.io/cluster=raycluster-kuberay
# NAME                                          READY   STATUS    RESTARTS   AGE
# raycluster-kuberay-head-bz77b                 1/1     Running   0          64s
# raycluster-kuberay-worker-workergroup-8gr5q   1/1     Running   0          63s
```

To customize the Ray cluster (e.g. number of worker Pods), you can modify the default Helm values:

```bash
helm show values kuberay/ray-cluster > values.yaml
# Modify the values.yaml, then install the Ray cluster with the customized values.
helm install raycluster kuberay/ray-cluster -f values.yaml --version 1.0.0 --set image.tag=2.7.0
```

For more details, please refer to Ray-Kubeflow [documentation](https://docs.ray.io/en/latest/cluster/kubernetes/k8s-ecosystem/kubeflow.html).