#!/bin/bash

set -eoa pipefail

#######################################################################################
# CHECK PRE-REQUISITES
#######################################################################################

# check for docker installation
if ! [[ $(which docker) && $(docker --version) ]]; then
    echo "Docker not found, please install docker."
    exit 1
fi

#######################################################################################
# INSTALL TOOLS
#######################################################################################

### Install curl (?) ###

if ! [[ $(which curl) ]]; then
    echo "Curl not found"
    echo "Installing curl"
    sudo apt install curl -y
fi

### Install kubectl (?) ###

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

RECOMMENDED_KUBECTL_VERSION="v1.28.2"
RECOMMENDED_MAJOR=$(echo $RECOMMENDED_KUBECTL_VERSION | cut -d'v' -f 2 | cut -d'.' -f 1)
RECOMMENDED_MINOR=$(echo $RECOMMENDED_KUBECTL_VERSION | cut -d'.' -f 2)

function install_kubectl {
  echo "Installing kubectl ($RECOMMENDED_KUBECTL_VERSION)"
  curl -LO https://dl.k8s.io/release/"$RECOMMENDED_KUBECTL_VERSION"/bin/linux/amd64/kubectl
  chmod +x kubectl
  mkdir -p ~/.local/bin
  mv ./kubectl ~/.local/bin/kubectl
  add_local_bin_to_path
  kubectl version --client
}

if ! [[ $(which kubectl) ]]; then
  echo "kubectl not found"
  install_kubectl

  else
    # check the version is the recommended
    CURRENT_KUBECTL_VERSION=$(kubectl version --client | grep -oP '(?<=GitVersion:")[^"]*|(?<=Client Version: v)[^ ]*')
    CURRENT_MAJOR=$(echo $CURRENT_KUBECTL_VERSION | cut -d'v' -f 2 | cut -d'.' -f 1)
    CURRENT_MINOR=$(echo $CURRENT_KUBECTL_VERSION | cut -d'.' -f 2)

    if [[ $RECOMMENDED_MAJOR != $CURRENT_MAJOR ]] || [[ $RECOMMENDED_MINOR != $CURRENT_MINOR ]]; then

      echo
      echo "The recommended kubectl version is $RECOMMENDED_KUBECTL_VERSION, your is $CURRENT_KUBECTL_VERSION"
      while true; do
        read -p "Do you wish to install kubectl ($RECOMMENDED_KUBECTL_VERSION)? (y/n): " yn
        case $yn in
            [Yy]* ) install_kubectl; break;;
            [Nn]* ) break;;
            * ) echo "Please answer yes or no.";;
        esac
      done

    fi
fi

### Install Kustomize (?)

RECOMMENDED_VERSION_MAJOR=5

function install_kustomize {
  echo "Installing kustomize"
  curl -s "https://raw.githubusercontent.com/kubernetes-sigs/kustomize/master/hack/install_kustomize.sh" | bash -s -- 5.2.1
  chmod +x kustomize
  mkdir -p ~/.local/bin
  mv ./kustomize ~/.local/bin/kustomize
  add_local_bin_to_path
  kustomize version
}

if ! [[ $(which kustomize) ]]; then
  echo "kustomize not found"
  install_kustomize

  else
    # check the version is the recommended
    KUSTOMIZE_VERSION=$(kustomize version)
    VERSION_MAJOR=$(echo $KUSTOMIZE_VERSION | cut -d'v' -f 2 | cut -d'.' -f 1)

    if [[ $VERSION_MAJOR != $RECOMMENDED_VERSION_MAJOR ]] ; then

      echo
      echo "The recommended version is $RECOMMENDED_VERSION_MAJOR.x.x, your is $VERSION_MAJOR.x.x"
      while true; do
        read -p "Do you wish to install a newer kustomize version? (y/n): " yn
        case $yn in
            [Yy]* ) install_kustomize; break;;
            [Nn]* ) break;;
            * ) echo "Please answer yes or no.";;
        esac
      done

    fi
fi

### Install Kind (?) ###

if ! [[ $(which kind) ]]; then
    echo "kind not found"
    echo "Installing kind"
    curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.14.0/kind-linux-amd64
    chmod +x ./kind
    mkdir -p ~/.local/bin
    mv ./kind ~/.local/bin/kind
    add_local_bin_to_path
    kind version
fi

echo Done!

exit 0