#!/bin/bash

set -xeoa pipefail

#######################################################################################
# The following shell script will create a local docker registry and connect the
# registry to the cluster network
#
# Usage: $ export HOST_IP=127.0.0.1; ./install_local_registry.sh
#
# source: https://kind.sigs.k8s.io/docs/user/local-registry/
#######################################################################################

REG_NAME='kind-registry'
REG_PORT='5001'

# create registry container unless it already exists
if [ "$(docker inspect -f '{{.State.Running}}' "${REG_NAME}" 2>/dev/null || true)" != 'true' ]; then
  docker run -d --restart=always -p "${HOST_IP}:${REG_PORT}:5000" --name "${REG_NAME}" registry:2
fi

# connect the registry to the cluster network if not already connected
if [ "$(docker inspect -f='{{json .NetworkSettings.Networks.kind}}' "${REG_NAME}")" = 'null' ]; then
  docker network connect "kind" "${REG_NAME}"
fi

# Document the local registry
# https://github.com/kubernetes/enhancements/tree/master/keps/sig-cluster-lifecycle/generic/1755-communicating-a-local-registry
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: ConfigMap
metadata:
  name: local-registry-hosting
  namespace: kube-public
data:
  localRegistryHosting.v1: |
    host: "${HOST_IP}:${REG_PORT}"
    help: "https://kind.sigs.k8s.io/docs/user/local-registry/"
EOF