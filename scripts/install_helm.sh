#!/bin/bash

set -xeo pipefail

### Install helm (?) ###
if ! [[ $(which helm) ]]; then
  echo "helm not found"
  echo "Installing helm"

  # Define Helm version
  HELM_VERSION="v3.13.3"

  # Determine OS and architecture
  OS="$(uname -s)"
  ARCH="$(uname -m)"

  # Set download URL based on OS and architecture
  if [ "$OS" = "Linux" ]; then
    URL="https://get.helm.sh/helm-${HELM_VERSION}-linux-amd64.tar.gz"
    TAR_FOLDER="linux-amd64"
  elif [ "$OS" = "Darwin" ]; then
    if [ "$ARCH" = "x86_64" ]; then
      URL="https://get.helm.sh/helm-${HELM_VERSION}-darwin-amd64.tar.gz"
      TAR_FOLDER="darwin-amd64"
    elif [ "$ARCH" = "arm64" ]; then
      URL="https://get.helm.sh/helm-${HELM_VERSION}-darwin-arm64.tar.gz"
      TAR_FOLDER="darwin-arm64"
    else
      echo "Unsupported architecture: $ARCH"
      exit 1
    fi
  else
    echo "Unsupported operating system: $OS"
    exit 1
  fi

  # Download and unpack Helm
  curl -LO $URL
  tar -zxvf "helm-${HELM_VERSION}-${TAR_FOLDER}.tar.gz"

  # Move Helm to a system path
  chmod +x ${TAR_FOLDER}/helm
  mv ${TAR_FOLDER}/helm /usr/local/bin/helm

  # Clean up
  rm -rf ${TAR_FOLDER}
  rm "helm-${HELM_VERSION}-${TAR_FOLDER}.tar.gz"

  echo "Helm $HELM_VERSION installed successfully"
fi
