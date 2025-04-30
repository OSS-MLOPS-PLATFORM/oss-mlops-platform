# How to create a distributed Ray cluster

We will go through how to connect separated Ray workers either run in containers or SLURM into the same Ray head node run either in Docker compose or Kubernetes. We assume that you have local computers/cloud virtual machines with Docker installed or access to supercomputer with suitable Ray configuration.

## Local Docker Compose

If you have either multiple laptops or workstations, it is recommeded to install [docker desktop](https://docs.docker.com/desktop/) regardless of distribution. 

**GPU in Containers**

A plus especially with windows machines with NVIDIA GPUs is that docker desktop provides GPU compatability by default, which isn't the case with linux. If you have Linux machine with GPUs, please see [this guide](tutorials/integration/gpu-support.md). When you have managed to setup docker desktop and run hello world, you can check GPU containers with [this yaml](applications/LLMs/inference/compose/gpu-test.yaml).

**Container Networking**

When Ray is run in a single machine, we can create Ray workers and give them the head worker address using the following command:

```
bash -c "ray start --address=ray-head:6379 --block"
```

Unfortunately it isn't trivial to connect separated Ray workers under a single ray head without problems. The main problem is that this connection requires Ray head and Ray workers to have exactly the same depedencies, which isn't realistic to setup, when we want to have consistent distributed computing. 

For this reason, we will instead create separated Ray clusters and SSH remote forward the dashboard and head to centralize orhestration under the same Ray cluster. We first need to setup a Ray cluster in using Docker compose that use either only CPUs or additionally GPUs. Be aware that you can find offical Ray docker images with specified python versions and GPU support [here](https://hub.docker.com/r/rayproject/ray). 

Here is the CPU only cluster:

```
networks:
  app_network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.29.0.0/16

services:
  ray-head:
    image: rayproject/ray:2.44.1-py312
    container_name: ray-head
    hostname: ray-head
    restart: no
    ports:
      - '127.0.0.1:6379:6379'
      - '127.0.0.1:8265:8265'
      - '127.0.0.1:8200:8200'
      - '127.0.0.1:10001:10001'
    shm_size: '5gb'
    command: bash -c "ray start --head --port=6379 --dashboard-host=0.0.0.0 --dashboard-port=8265 --metrics-export-port=8200 --ray-client-server-port=10001 --block"
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: '4g'
    networks:
      app_network:
        ipv4_address: 172.29.0.15
  ray-worker:
    image: rayproject/ray:2.44.1-py312
    container_name: ray-worker
    hostname: ray-worker
    depends_on:
      - ray-head
    shm_size: '5gb'
    command: bash -c "ray start --address=ray-head:6379 --block"
    deploy:
      mode: replicated
      replicas: '1'
      resources:
        limits:
         cpus: '1'
         memory: '4g'
    networks:
      - app_network
```

Here is the CPU+GPU(NVIDIA) cluster:

```
networks:
  app_network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.29.0.0/16

services:
  ray-head:
    image: rayproject/ray:2.44.1-py312-gpu
    container_name: ray-head
    hostname: ray-head
    restart: no
    ports:
      - '127.0.0.1:6379:6379'
      - '127.0.0.1:8265:8265'
      - '127.0.0.1:8200:8200'
      - '127.0.0.1:10001:10001'
    shm_size: '5gb'
    command: bash -c "ray start --head --port=6379 --dashboard-host=0.0.0.0 --dashboard-port=8265 --metrics-export-port=8200 --ray-client-server-port=10001 --block"
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
        limits:
          cpus: '1'
          memory: '4g'
    networks:
      app_network:
        ipv4_address: 172.29.0.15
  ray-worker:
    image: rayproject/ray:2.44.1-py312-gpu
    container_name: ray-worker
    hostname: ray-worker
    depends_on:
      - ray-head
    shm_size: '5gb'
    command: bash -c "ray start --address=ray-head:6379 --block"
    deploy:
      mode: replicated
      replicas: '1'
      resources:
        limits:
         cpus: '1'
         memory: '4g'
    networks:
      - app_network
```

When you have activated Docker Compose, run these with


```
docker compose -f cpu-ray-cluster.yaml up 
```

If this creates errors, check configuration, container names and network. When the cluster is running, you can check its dashboard at http://127.0.0.1:8265. We can remote forward it to a computer of our choice, which in our case is a CPouta cloud platform virtual machine (VM). Add the following into your SSH config:


```
Host rf-cpouta
Hostname (your_vm_public_ip)
User (your_vm_user)
IdentityFile ~/.ssh/(your_vm_key).pem
RemoteForward (your_vm_private_ip):8284 127.0.0.1:8265
RemoteForward (your_vm_private_ip):9284 127.0.0.1:10001
```

You might need to create a list to give unique ports if you are planning to add more Ray clusters. These clusters can be easily utilized with the dashboard connection that you can localforward with the following:


```
Host lf-cpouta
Hostname (your_vm_public_ip)
User ubuntu
IdentityFile ~/.ssh/(your_vm_key).pem
LocalForward 127.0.0.1:8284 (your_vm_private_ip):8284
LocalForward 127.0.0.1:8285 (your_vm_private_ip):8285
LocalForward 127.0.0.1:8286 (your_vm_private_ip):8286 
```

Now, if you want to use these in a root Ray cluster, then the easiest option for you is either to setup Docker Compose with a Ray cluster that provides ingress to the Docker Network or use Kubernetes in Docker (KinD) to attach a cluster service to a specific VM address. Here we will do the latter with the OSS MLOps platform. 

The easiest way to handle Ray in Kubernetes is via Helm installation, where we provide specific values. Confirm that your VM has Helm with the following:

```
helm version
```

If this produces and error, you can install helm with the script. When helm is ready, you need to check the available resources for the KinD cluster to configure Ray cluster resource limits. You can check cluster resource use with:


```
kubectl describe nodes
```

By using this information create a YAML file with the following example info:


```
image:
  repository: rayproject/ray
  tag: 2.44.1-py312
  pullPolicy: IfNotPresent

head:
  resources:
    limits:
      cpu: "1"
      memory: "10G"
    requests:
      cpu: "1"
      memory: "10G"
  volumes:
    - name: log-volume
      emptyDir: {}
  volumeMounts:
    - mountPath: /tmp/ray
      name: log-volume
 
worker:
  groupName: worker
  replicas: 1
  minReplicas: 1
  maxReplicas: 1
  resources:
    limits:
      cpu: "1"
      memory: "10G"
    requests:
      cpu: "1"
      memory: "10G"
  volumes:
    - name: log-volume
      emptyDir: {}
  volumeMounts:
    - mountPath: /tmp/ray
      name: log-volume
```

Now, we can create the Ray cluster with the following commands:

```
helm repo add kuberay https://ray-project.github.io/kuberay-helm/
helm repo update
helm install kuberay-operator kuberay/kuberay-operator --version 1.0.0
helm install raycluster kuberay/ray-cluster --version 1.0.0 -f cpu-kuberay-cluster-values.yaml
```

You can check the cluster with:


```
kubectl get pods -n default
```

If there are problems, you can remove the cluster with

```
helm list -A
helm uninstall raycluster
helm uninstall kuberay-operator
```

When the cluster is running, you can see its dashboard with:

```
ssh -L 127.0.0.1:8090:localhost:8265 cpouta
kubectl port-forward svc/raycluster-kuberay-head-svc 8265:8265 -n default
```

Now, in order to use this as the central ray cluster that uses other ray clusters, we need to forward the remote forwarded Ray dashboards and heads using a headless service. These can be created with the following
objects:

```
apiVersion: v1
kind: Endpoints
metadata:
   name: remote-ray-(dash/head)-1 
subsets:
  - addresses:
    - ip: '(your_vm_private_ip)'
    ports: 
      - port: (dash/head_port)
'''
apiVersion: v1
kind: Service
metadata:
   name: remote-ray-(dash/head)-1 
   annotations:
      prometheus.io/scrape: 'true'
      prometheus.io/port: '0'
spec:
   type: ClusterIP
   ports:
   - protocol: TCP
     port: (dash/head_port)
     targetPort: (dash/head_port)
```

You can make connection testing concrete by setting up a CURL pod:

```
apiVersion: v1
kind: Pod
metadata:
  name: curl-pod
spec:
  containers:
  - name: curl-container
    image: curlimages/curl:latest
    command: ['sleep','3600']
```

When the pod is running, go inside it to run CURL with:

```
kubectl apply -f curl.yaml
kubectl get pods
kubectl exec -it curl-pod -- /bin/sh
curl http://remote-ray-1.default.svc.cluster.local:8284
exit
```

The CURL result should provide 200 with CSS. When you have confirmed that the connections work, we can start create code that utilizes the remote Ray cluster in a central Ray cluster. By using the following [docs](https://docs.ray.io/en/latest/cluster/running-applications/job-submission/ray-client.html#ray-client-ref) for using Ray.init to connect to multiple Ray clusters, we can get the resources of all provided clusters with the following example function:


```
def check_clusters(
    cluster_urls: any
) -> any:
  try:
      clusters = {}
      # CPU, OSM, RAM, GPU
      collective = [0,0,0,0]
      for i in range(len(cluster_urls)+1):
          checked_collective = [0,0,0,0]
          checked_resources = {}
          checked_nodes = {}
          if i == 0:
              ray.init()
              checked_collective, checked_resources, checked_nodes = check_cluster(
                  cluster_resources = ray.available_resources(),
                  cluster_nodes = ray.nodes()
              )
          else:
              head_url = 'ray://' + cluster_urls[i-1]
              head_client = ray.init(
                  address = head_url, 
                  allow_multiple = True
              )

              with head_client:
                  checked_collective, checked_resources, checked_nodes = check_cluster(
                      cluster_resources = ray.available_resources(),
                      cluster_nodes = ray.nodes()
                  )
              head_client.disconnect()

          collective = [a + b for a,b in zip(collective, checked_collective)]
          clusters[str(i)] = {
              'resources': checked_resources,
              'nodes': checked_nodes
          }
      
          i += 1
      clusters['collective'] = {
          'CPU': collective[0],
          'OSM': collective[1],
          'RAM': collective[2],
          'GPU': collective[3]
      }
      return clusters
  except Exception as e:
      print('Check resources error')
      print(e)
      return {}
```

We can make the remote clusters install packages using [runtime_env](https://docs.ray.io/en/latest/ray-core/api/doc/ray.runtime_env.RuntimeEnv.html) either in ray.init or remote task.