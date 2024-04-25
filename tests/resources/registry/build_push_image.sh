#!/usr/bin/env bash

set -eux

HOST_IP=$1

REGISTRY="$HOST_IP:5001"
IMAGE_NAME="kfp-registry-test-image"
IMAGE_TAG="reg-test-kfp"

FULL_IMAGE_NAME=${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}

cd "$(dirname "$0")"

docker build -t "$FULL_IMAGE_NAME" .

# to push the image to a remote repository instead
docker push "$FULL_IMAGE_NAME"