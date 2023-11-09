#!/bin/bash

set -xeoa pipefail

#######################################################################################
# CHECK PRE-REQUISITES
#######################################################################################

# make sure that Homebrew is installed
if ! [[ $(which brew) ]]; then
    echo "Homebrew is not installed, please install it before continuing."
    exit 1
fi

# check for docker installation
if ! [[ $(which docker) && $(docker --version) ]]; then
    echo "Docker not found, please install docker."
    exit 1
fi

#######################################################################################
# INSTALL TOOLS
#######################################################################################

### Install jq (?) ###
if ! [[ $(which jq) ]]; then
    echo "jq not found"
    echo "Installing jq"
    brew install jq
fi

### Install curl (?) ###

if ! [[ $(which curl) ]]; then
    echo "Curl not found"
    echo "Installing curl"
    brew install curl
fi

### Install kubectl (?) ###

RECOMMENDED_KUBECTL_VERSION="v1.24.0"
RECOMMENDED_MAJOR=$(echo $RECOMMENDED_KUBECTL_VERSION | cut -d'v' -f 2 | cut -d'.' -f 1)
RECOMMENDED_MINOR=$(echo $RECOMMENDED_KUBECTL_VERSION | cut -d'.' -f 2)


function install_kubectl {
    echo "Installing kubectl ($RECOMMENDED_KUBECTL_VERSION)"
    ARCH=$(uname -m)

    curl -LO https://dl.k8s.io/release/"$RECOMMENDED_KUBECTL_VERSION"/bin/darwin/"$ARCH"/kubectl
    chmod +x ./kubectl
    mkdir -p ${HOME}/.local/bin
    mv ./kubectl ${HOME}/.local/bin/kubectl

    # make sure ~/.local/bin is in $PATH
    if [[ ":$PATH:" != *:${HOME}/.local/bin:* ]]; then
        if [ "$BASH_VERSION" ]; then
            SRC_FILE="$HOME/.bash_profile"
        elif [ "$ZSH_VERSION" ]; then
            SRC_FILE="$HOME/.zshrc"
        else
            echo "Current shell is not Bash nor Zsh"
            exit 1
        fi
        echo 'Adding ~/.local/bin to $PATH'
        echo "" >> $SRC_FILE
        echo 'PATH="$HOME/.local/bin:$PATH"' >> $SRC_FILE
        source $SRC_FILE
    fi

    kubectl version --client --output=yaml
}

if ! [[ $(which kubectl) ]]; then
    echo "kubectl not found"
    install_kubectl
else
    # Check if kubectl version is the recommended one
    CURRENT_KUBECTL_VERSION=$(kubectl version --client | grep -oE '(GitVersion:)[^ ]*' | cut -f 2 -d'"')
    CURRENT_MAJOR=$(echo "$CURRENT_KUBECTL_VERSION" | cut -d'v' -f 2 | cut -d'.' -f 1)
    CURRENT_MINOR=$(echo "$CURRENT_KUBECTL_VERSION" | cut -d'.' -f 2)

    if [[ $RECOMMENDED_MAJOR != "$CURRENT_MAJOR" ]] || [[ $RECOMMENDED_MINOR != "$CURRENT_MINOR" ]]; then
      echo
      echo "The recommended kubectl version is $RECOMMENDED_KUBECTL_VERSION, yours is $CURRENT_KUBECTL_VERSION"
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

### Install Kind (?) ###

if ! [[ $(which kind) ]]; then
    echo "kind not found"
    echo "Installing kind"
    brew install kind
fi

echo Done!

exit 0
