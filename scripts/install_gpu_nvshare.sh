#!/bin/bash

set -eo pipefail

kubectl apply -f https://raw.githubusercontent.com/grgalex/nvshare/main/kubernetes/manifests/nvshare-system.yaml && \
kubectl apply -f https://raw.githubusercontent.com/grgalex/nvshare/main/kubernetes/manifests/nvshare-system-quotas.yaml && \
kubectl apply -f https://raw.githubusercontent.com/grgalex/nvshare/main/kubernetes/manifests/device-plugin.yaml && \
kubectl apply -f https://raw.githubusercontent.com/grgalex/nvshare/main/kubernetes/manifests/scheduler.yaml