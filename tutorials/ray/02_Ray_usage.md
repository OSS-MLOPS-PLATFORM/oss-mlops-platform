# Ray Setup

## TOC
  - [1. Connect to Ray and run a job (via Kubeflow)](#3-connect-to-ray-and-run-a-job-via-kubeflow)
    - [1.1 Forward the port of Istio’s Ingress-Gateway](#31-forward-the-port-of-istios-ingress-gateway)
    - [1.2 Create a JupyterLab via Kubeflow Central Dashboard](#32-create-a-jupyterlab-via-kubeflow-central-dashboard)
    - [1.3 Run a Ray job](#33-run-a-ray-job)
  - [2. Access Ray dashboard](#4-access-ray-dashboard)
  - [3. Connect to Ray cluster (via local machine)](#5-connect-to-ray-cluster-from-local-machine)

## 1. Connect to Ray and run a job (via Kubeflow)

### 1.1 Forward the port of Istio’s Ingress-Gateway

```bash
kubectl port-forward svc/istio-ingressgateway -n istio-system 8080:80
```

Go to http://localhost:8080/ and you should see the Kubeflow dashboard.

### 1.2 Create a JupyterLab via Kubeflow Central Dashboard

- Click “Notebooks” icon in the left panel.
- Click “New Notebook”
- Select `kubeflownotebookswg/jupyter-scipy:v1.8.0-rc.0` as OCI image.
- Click “Launch”
- Click “CONNECT” to connect into the JupyterLab instance.

### 1.3 Run a Ray job

Open a terminal in the JupyterLab:

```bash
python --version 
# Python 3.8.10

# Install Ray 2.2.0
pip install -U ray[default]==2.2.0

# Downgrade pydantic to a version < 2.0.0 compatible with Ray 2.2.0
pip install "pydantic<2"
```

Open a new Python notebook and run the following code:

```python
# cell 1
import ray

# ray://${RAYCLUSTER_HEAD_SVC}.${NAMESPACE}.svc.cluster.local:${RAY_CLIENT_PORT}
ray.init(address="ray://raycluster-kuberay-head-svc.default.svc.cluster.local:10001")
```

```python
# cell 2
print(ray.cluster_resources())
```

```python
# cell 3

# Try Ray task
@ray.remote
def f(x):
    return x * x

futures = [f.remote(i) for i in range(4)]
print(ray.get(futures)) # [0, 1, 4, 9]
```

```python
# cell 4

# Try Ray actor
@ray.remote
class Counter(object):
    def __init__(self):
        self.n = 0

    def increment(self):
        self.n += 1

    def read(self):
        return self.n

counters = [Counter.remote() for i in range(4)]
[c.increment.remote() for c in counters]
futures = [c.read.remote() for c in counters]
print(ray.get(futures)) # [1, 1, 1, 1]
```

## 2. Access Ray dashboard

```bash
kubectl port-forward raycluster-kuberay-head-862db 8265:8265 -n default
```
Go to http://localhost:8265/ and you should see the Ray dashboard.

## 3. Connect to Ray cluster from local machine

> The version of the Ray client must match the version of the Ray cluster (2.2.0).

```bash
conda create -n ray-env python=3.8.10
conda activate ray-env
pip install ray==2.2.0
pip install "pydantic<2"
```

Run a port forwarding to the Ray head service:

```bash
kubectl port-forward svc/raycluster-kuberay-head-svc 10001:10001 -n default
```

```python
import ray

ray.init(address="ray://localhost:10001")
print(ray.cluster_resources())
```