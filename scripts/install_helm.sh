#!/bin/bash

set -eo pipefail

function add_local_bin_to_path {
  # make sure ~/.local/bin is in $PATH
  BASE=~
  if [[ ":$PATH:" != *${BASE}/.local/bin* ]]; then
    echo 'Adding ~/.local/bin to $PATH in ~/.profile)'
    echo "" >> ~/.profile
    echo 'PATH="$HOME/.local/bin:$PATH"' >> ~/.profile
    source ~/.profile
  fi
}

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
  mkdir -p ~/.local/bin
  mv ${TAR_FOLDER}/helm ~/.local/bin/helm
  add_local_bin_to_path
  helm version

  # Clean up
  rm -rf ${TAR_FOLDER}
  rm "helm-${HELM_VERSION}-${TAR_FOLDER}.tar.gz"

  echo "Helm $HELM_VERSION installed successfully"
fi
