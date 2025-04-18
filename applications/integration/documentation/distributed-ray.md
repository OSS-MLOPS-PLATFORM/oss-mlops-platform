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

For this reason, we will instead create separated Ray clusters and SSH remote forward the dashboard to centralize orhestration under the same Ray cluster. We first need to setup a Ray cluster in using Docker compose that use either only CPUs or additionally GPUs. Be aware that you can find offical Ray docker images with specified python versions and GPU support [here](https://hub.docker.com/r/rayproject/ray). 

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
    shm_size: '5gb'
    command: bash -c "ray start --head --port=6379 --dashboard-host=0.0.0.0 --dashboard-port=8265 --metrics-export-port=8200 --block"
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
    shm_size: '5gb'
    command: bash -c "ray start --head --port=6379 --dashboard-host=0.0.0.0 --dashboard-port=8265 --metrics-export-port=8200 --block"
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
docker compose -f ray-cluster.yaml up 
```

If this creates errors, check configuration, container names and network. When the cluster is running, you can check its dashboard at http://127.0.0.1:8265. We can remote forward it to a computer of our choice, which in our case is a CPouta cloud platform virtual machine (VM). Add the following into your SSH config:


```
Host rf-cpouta
Hostname (your_vm_public_ip)
User (your_vm_user)
IdentityFile ~/.ssh/(your_vm_key).pem
RemoteForward (your_vm_private_ip):8284 127.0.0.1:8265
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
