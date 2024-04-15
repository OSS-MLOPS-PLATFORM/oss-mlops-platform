<h1>Set up a local kubernetes cluster with Kind</h1>

Set up a local kubernetes cluster with [Kind](https://kind.sigs.k8s.io/).

### 1. Install kubectl

```bash
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
kubectl version --client
```

### 2. Install Kind

```bash
curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.14.0/kind-linux-amd64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind
```

### 3. Create a cluster

```bash
export CLUSTER_NAME="mlops-platform"
export HOST_IP="127.0.0.1"  # cluster IP address

cat <<EOF | kind create cluster --name $CLUSTER_NAME --image=kindest/node:v1.24.0 --config=-
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
networking:
  ipFamily: dual
  apiServerAddress: $HOST_IP
nodes:
- role: control-plane
  kubeadmConfigPatches:
  - |
    kind: InitConfiguration
    nodeRegistration:
      kubeletExtraArgs:
        node-labels: "ingress-ready=true"
  extraPortMappings:
  - containerPort: 80
    hostPort: 80
    protocol: TCP
  - containerPort: 443
    hostPort: 443
    protocol: TCP

# uncomment to enable local registry    
#containerdConfigPatches:
#- |-
#  [plugins."io.containerd.grpc.v1.cri".registry.mirrors."${HOST_IP}:5001"]
#    endpoint = ["http://kind-registry:5000"]

EOF
```

The `--config` we passed contains the configuration needed for setting up the ports and enable
the ingress later on.

The default IP address (`127.0.0.1`) is only accessible from the computer the cluster is running on.
If you want to make your cluster accessible from other computer in the local network,
change the `apiServerAddress:` field to the real IP address of the computer.

You can get the IP by running:

```bash
# get computer IP in LAN
ip -o route get to 8.8.8.8 | sed -n 's/.*src \([0-9.]\+\).*/\1/p'

# or alternatively
hostname -I | cut -d' ' -f1

# on macOS (given that you need th IP of the default en0 interface)
ipconfig getifaddr en0
```

> **Note:** If you want to use a local registry, you can uncomment the `containerdConfigPatches` section.