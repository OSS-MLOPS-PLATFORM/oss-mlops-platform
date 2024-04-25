#!/bin/bash

set -eo pipefail

helm repo add kuberay https://ray-project.github.io/kuberay-helm/
helm repo update

# Install both CRDs and KubeRay operator v1.0.0.
helm install kuberay-operator kuberay/kuberay-operator --version 1.0.0

# wait for the operator to be ready
kubectl wait --for=condition=available --timeout=1200s deployment/kuberay-operator

# Install KubeRay cluster
helm install raycluster kuberay/ray-cluster --version 1.0.0 --set image.tag=2.7.0
