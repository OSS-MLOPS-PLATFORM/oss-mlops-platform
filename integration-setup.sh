#!/bin/bash

set -eoa pipefail

# Internal directory where to store platform settings
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
PLATFORM_DIR="$SCRIPT_DIR/.platform"
mkdir -p "$PLATFORM_DIR"
PLATFORM_CONFIG="$PLATFORM_DIR/.config"
cp "$SCRIPT_DIR/config.env" $PLATFORM_CONFIG

source $PLATFORM_CONFIG

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

SETUP_INTEGRATION=false
echo
read -p "Setup integration (y/n) (default is [n]): " choice
case "$choice" in
    y|Y ) SETUP_INTEGRATION=true ;;
    * ) SETUP_INTEGRATION=false ;;
esac

if [[ "$SETUP_INTEGRATION" = false ]]; then
    DEFAULT_DEPLOYMENT_OPTION="kubeflow-monitoring"
    echo
    echo "Please choose the deployment option:"
    echo "[1] Kubeflow (all components)"
    echo "[2] Kubeflow (without monitoring)"
    echo "[3] Standalone KFP"
    echo "[4] Standalone KFP (without monitoring)"
    echo "[5] Standalone KFP and Kserve"
    echo "[6] Standalone KFP and Kserve (without monitoring)"
    read -p "Enter the number of your choice [1-6] (default is [1]): " choice
    case "$choice" in
        1 ) DEPLOYMENT_OPTION="kubeflow-monitoring" ;;
        2 ) DEPLOYMENT_OPTION="kubeflow" ;;
        3 ) DEPLOYMENT_OPTION="standalone-kfp-monitoring" ;;
        4 ) DEPLOYMENT_OPTION="standalone-kfp" ;;
        5 ) DEPLOYMENT_OPTION="standalone-kfp-kserve-monitoring" ;;
        6 ) DEPLOYMENT_OPTION="standalone-kfp-kserve" ;;
        * ) DEPLOYMENT_OPTION="$DEFAULT_DEPLOYMENT_OPTION" ;;
    esac
else
    DEFAULT_DEPLOYMENT_OPTION="integration-kubeflow-monitoring"
    echo
    echo "Please choose the deployment option:"
    echo "[1] Kubeflow (all components)"
    echo "[2] Kubeflow (some components removed)"
    echo "[3] Standalone KFP"
    echo "[4] Standalone KFP and Kserve"
    read -p "Enter the number of your choice [1-4] (default is [1]): " choice
    case "$choice" in
        1 ) DEPLOYMENT_OPTION="integration-kubeflow-monitoring" ;;
        2 ) DEPLOYMENT_OPTION="integration-reduced-kubeflow-monitoring" ;;
        3 ) DEPLOYMENT_OPTION="integration-standalone-kfp-monitoring" ;;
        4 ) DEPLOYMENT_OPTION="integration-standalone-kfp-kserve-monitoring" ;;
        * ) DEPLOYMENT_OPTION="$DEFAULT_DEPLOYMENT_OPTION" ;;
    esac
fi

INSTALL_LOCAL_REGISTRY=true
echo
read -p "Install local Docker registry? (y/n) (default is [y]): " choice
case "$choice" in
    n|N ) INSTALL_LOCAL_REGISTRY=false ;;
    * ) INSTALL_LOCAL_REGISTRY=true ;;
esac

SETUP_GPU_CLUSTER=false
echo
read -p "Setup GPU Cluster (Requires atleast 1 GPU) (y/n) (default is [n]): " choice
case "$choice" in
    y|Y ) SETUP_GPU_CLUSTER=true ;;
    * ) SETUP_GPU_CLUSTER=false ;;
esac

INSTALL_RAY=false
echo
read -p "Install Ray? (It requires ~4 additional CPUs) (y/n) (default is [n]): " choice
case "$choice" in
    y|Y ) INSTALL_RAY=true ;;
    * ) INSTALL_RAY=false ;;
esac

SETUP_GPU_RAY=false
if [ "$INSTALL_RAY" = true ]; then
    echo
    read -p "Setup GPU Ray (Requires atleast 1 GPU) (y/n) (default is [n]): " choice
    case "$choice" in
        y|Y ) SETUP_GPU_RAY=true ;;
        * ) SETUP_GPU_RAY=false ;;
    esac
esac

# Save selections to settings file
echo -e "\nDEPLOYMENT_OPTION=$DEPLOYMENT_OPTION" >> $PLATFORM_CONFIG
echo -e "\nINSTALL_LOCAL_REGISTRY=$INSTALL_LOCAL_REGISTRY" >> $PLATFORM_CONFIG
echo -e "\nINSTALL_RAY=$INSTALL_RAY" >> $PLATFORM_CONFIG

# CHECK DISK SPACE
RECOMMENDED_DISK_SPACE_KUBEFLOW=26214400
RECOMMENDED_DISK_SPACE_KUBEFLOW_GB=$(($RECOMMENDED_DISK_SPACE_KUBEFLOW / 1024 / 1024))
RECOMMENDED_DISK_SPACE_KFP=18874368
RECOMMENDED_DISK_SPACE_KFP_GB=$(($RECOMMENDED_DISK_SPACE_KFP / 1024 / 1024))

if [[ $DEPLOYMENT_OPTION == *"kfp"* ]]; then
    RECOMMENDED_DISK_SPACE=$RECOMMENDED_DISK_SPACE_KFP
    RECOMMENDED_DISK_SPACE_GB=$RECOMMENDED_DISK_SPACE_KFP_GB
else
    RECOMMENDED_DISK_SPACE=$RECOMMENDED_DISK_SPACE_KUBEFLOW
    RECOMMENDED_DISK_SPACE_GB=$RECOMMENDED_DISK_SPACE_KUBEFLOW_GB
fi

DISK_SPACE=$(df -k . | awk -F ' ' '{print $4}' | sed -n '2 p')
DISK_SPACE_GB=$(($DISK_SPACE / 1024 / 1024))

# TODO: Set required depending on the deployment, ray, etc.

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
RECOMMENDED_CPUS_KUBEFLOW=12
RECOMMENDED_CPUS_KFP=8
EXTRA_RAY_CPUS=4

if [[ $DEPLOYMENT_OPTION == *"kfp"* ]]; then
    RECOMMENDED_CPUS=$RECOMMENDED_CPUS_KFP
else
    RECOMMENDED_CPUS=$RECOMMENDED_CPUS_KUBEFLOW
fi

if [ "$INSTALL_RAY" = true ]; then
    RECOMMENDED_CPUS=$(($RECOMMENDED_CPUS + $EXTRA_RAY_CPUS))
fi

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
    echo "The recommended is >= ${RECOMMENDED_CPUS} CPU cores for this deployment configuration. You have ${CPU_COUNT} cores."
    while true; do
        read -p "Do you want to continue with the installation? (y/n): " yn
        case $yn in
            [Yy]* ) break;;
            [Nn]* ) exit 1;;
            "" ) echo "Please enter a response.";;
            * ) echo "Please answer yes or no.";;
        esac
    done
fi

# INSTALL TOOLS
if [[ "$(uname)" == "Darwin" ]]; then
  bash "$SCRIPT_DIR/scripts/install_tools_mac.sh"  # Using default bash because /bin/bash is an old version (3)
else
  /bin/bash "$SCRIPT_DIR/scripts/install_tools.sh"
fi

# CREATE CLUSTER
function fail {
    printf "If the previous error is caused because the cluster already exists, you can deleted it with the following command: kind delete cluster --name $CLUSTER_NAME \n" "$1" >&2
    exit "${2-1}" ## Return a code specified by $2, or 1 by default.
}

# Check if the kind cluster already exists
if kind get clusters | grep -q "^$CLUSTER_NAME$"; then
  echo
  echo "Kind cluster with name \"$CLUSTER_NAME\" already exists. It can be deleted with the following command: kind delete cluster --name $CLUSTER_NAME"
  while true; do
    read -p "Do you want to continue the installation on the existing cluster? (y/n): " choice
    case "$choice" in
        y|Y ) echo "Using existing kind cluster..."; break;;
        n|N ) exit 0 ;;
        * ) echo "Invalid response. Please enter y or n." ;;
        "" ) echo "Please enter a response." ;;
    esac
  done
else
    echo "Creating kind cluster..."
    if [[ "$SETUP_GPU_CLUSTER" = false ]]; then
        /bin/bash "$SCRIPT_DIR/scripts/create_cluster.sh"
    else
        /bin/bash "$SCRIPT_DIR/scripts/create_gpu_cluster.sh"
    fi
fi

kubectl cluster-info --context kind-$CLUSTER_NAME

# DEPLOY LOCAL DOCKER REGISTRY
if [ "$INSTALL_LOCAL_REGISTRY" = true ]; then
  /bin/bash "$SCRIPT_DIR/scripts/install_local_registry.sh"
fi

# DEPLOY STACK
kubectl config use-context kind-$CLUSTER_NAME

# Build the kustomization and store the output in the temporary file
tmp_file=$(mktemp)
DEPLOYMENT_ROOT="$SCRIPT_DIR/deployment/envs/$DEPLOYMENT_OPTION"
echo "Deployment root set to: $DEPLOYMENT_ROOT"
echo
echo "Building manifests..."
kustomize build $DEPLOYMENT_ROOT > "$tmp_file"
echo "Manifests built successfully."
echo
echo "Applying resources..."
while true; do
  if kubectl apply -f "$tmp_file"; then
      echo "Resources successfully applied."
      rm "$tmp_file"
      break
  else
      echo
      echo "Retrying to apply resources."
      echo "Be patient, this might take a while... (Errors are expected until all resources are available!)"
      echo
      echo "Help:"
      echo "  If the errors persists, please check the pods status with: kubectl get pods --all-namespaces"
      echo "  All pods should be either in Running state, or ContainerCreating if they are still starting up."
      echo "  Check specific pod errors with: kubectl describe pod -n [NAMESPACE] [POD_NAME]"
      echo "  For further help, see the Troubleshooting section in setup.md"
      echo

      sleep 10
  fi
done

# Install Helm and GPU pods
if [[ "$SETUP_GPU_CLUSTER" = true || "$INSTALL_RAY" = true ]]; then
    echo "Installing Helm"
    /bin/bash "$SCRIPT_DIR/scripts/install_helm.sh"
    if [[ "$SETUP_GPU_CLUSTER" = true ]]; then
        echo "Installing NVIDIA GPU operator"
        /bin/bash "$SCRIPT_DIR/scripts/install_gpu_operator.sh" 
        echo "Installing NVIDIA Nvshare"
        /bin/bash "$SCRIPT_DIR/scripts/install_gpu_nvshare.sh"
    fi
fi

# DEPLOY RAY
if [ "$INSTALL_RAY" = true ]; then
    if [[ "$SETUP_GPU_RAY" = false ]]; then
        echo "Installing CPU Ray"
        /bin/bash "$SCRIPT_DIR/scripts/install_ray.sh" 
    else
        echo "Installing CPU+GPU Ray"
        /bin/bash "$SCRIPT_DIR/scripts/install_gpu_ray.sh"
    fi
fi

echo
echo "Installation completed!"
echo

# TESTS
if [ "$RUN_TESTS" = "true" ]; then
  /bin/bash "$SCRIPT_DIR/scripts/run_tests.sh"
fi

exit 0
