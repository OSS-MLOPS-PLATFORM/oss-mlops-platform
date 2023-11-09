#!/usr/bin/env bash

set -eux

IMAGE_NAME=try-out/kfp-test-image

IMAGE_TAG=test-kfp

FULL_IMAGE_NAME=${IMAGE_NAME}:${IMAGE_TAG}

cd "$(dirname "$0")"

docker build -t "$FULL_IMAGE_NAME" .

# load the image into the local "kind" cluster with name "kind-ep"
kind load docker-image "$FULL_IMAGE_NAME" --name kind-ep

# to push the image to a remote repository instead
# docker push "$FULL_IMAGE_NAME"