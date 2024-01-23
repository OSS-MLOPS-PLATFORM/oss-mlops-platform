#!/bin/bash

set -xeoa pipefail

source config.env

RUN_TESTS=false
LOG_LEVEL_TESTS="WARNING"

while true; do
if [ "$1" = "--test" -o "$1" = "-t" ]; then
    RUN_TESTS=true
    shift 1
elif [ "$1" = "--debug" -o "$1" = "-d" ]; then
    LOG_LEVEL_TESTS="INFO"
    shift 1
else
    break
fi
done

echo Cluster name set to: "$CLUSTER_NAME"
echo Host IP set to: "$HOST_IP"
echo Run tests after installation set to: "$RUN_TESTS"

# CHECK DISK SPACE
RECOMMENDED_DISK_SPACE=26214400
RECOMMENDED_DISK_SPACE_GB=$(($RECOMMENDED_DISK_SPACE / 1024 / 1024))

DISK_SPACE=$(df -k . | awk -F ' ' '{print $4}' | sed -n '2 p')
DISK_SPACE_GB=$(($DISK_SPACE / 1024 / 1024))

if [[ DISK_SPACE < $RECOMMENDED_DISK_SPACE ]]; then
    echo "WARNING: Not enough disk space detected!"
    echo "The recommended is > ${RECOMMENDED_DISK_SPACE_GB} GB of disk space. You have ${DISK_SPACE_GB} GB."
    while true; do
        read -p "Do you want to continue with the installation? (y/n): " yn
        case $yn in
            [Yy]* ) break;;
            [Nn]* ) exit 1;;
            * ) echo "Please answer yes or no.";;
        esac
      done
fi

# CHECK CPU COUNT
RECOMMENDED_CPUS=16

# Detect the OS
OS=$(uname)

if [ "$OS" = "Darwin" ]; then
    # For macOS
    CPU_COUNT=$(sysctl -n hw.ncpu)
else
    # For Linux
    CPU_COUNT=$(nproc)
fi

if [[ $CPU_COUNT -lt $RECOMMENDED_CPUS ]]; then
    echo "WARNING: Not enough CPU cores detected!"
    echo "The recommended is >= ${RECOMMENDED_CPUS} CPU cores. You have ${CPU_COUNT} cores."
    while true; do
        read -p "Do you want to continue with the installation? (y/n): " yn
        case $yn in
            [Yy]* ) break;;
            [Nn]* ) exit 1;;
            * ) echo "Please answer yes or no.";;
        esac
    done
fi

# INSTALL TOOLS
if [[ "$(uname)" == "Darwin" ]]; then
  bash scripts/install_tools_mac.sh  # Using default bash because /bin/bash is an old version (3)
else
  /bin/bash scripts/install_tools.sh
fi

# CREATE CLUSTER
function fail {
    printf "If the previous error is caused because the cluster already exists, you can deleted it with the following command: kind delete cluster --name $CLUSTER_NAME \n" "$1" >&2
    exit "${2-1}" ## Return a code specified by $2, or 1 by default.
}

/bin/bash scripts/create_cluster.sh || fail

kubectl cluster-info --context kind-$CLUSTER_NAME

# DEPLOY LOCAL DOCKER REGISTRY
if [ "$INSTALL_LOCAL_REGISTRY" = true ]; then
  /bin/bash scripts/install_local_registry.sh
fi

# DEPLOY STACK
kubectl config use-context kind-$CLUSTER_NAME

# Create a temporary file
tmpfile=$(mktemp)
# Build the kustomization and store the output in the temporary file
kustomize build deployment > "$tmpfile"

while true; do
  if kubectl apply -f "$tmpfile"; then
      echo "Resources successfully applied."
      rm "$tmpfile"
      break
  else
      echo "Retrying to apply resources. Be patient, this might take a while..."
      sleep 10
  fi
done

# DEPLOY RAY
if [ "$INSTALL_RAY" = true ]; then
  echo "Installing Ray"
  /bin/bash scripts/install_helm.sh
  /bin/bash scripts/install_ray.sh
fi

echo
echo Installation completed!
echo

# TESTS
if [ "$RUN_TESTS" = "true" ]; then
  /bin/bash scripts/run_tests.sh
fi

exit 0
