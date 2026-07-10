# How to create a distributed Ray cluster

We will go through how to connect separated Ray workers either run in containers or SLURM into the same Ray head node run either in Docker compose or Kubernetes. We assume that you have local computers/cloud virtual machines with Docker installed or access to supercomputer with suitable Ray configuration.

## Local Docker Compose

If you have either multiple laptops or workstations, it is recommeded to install [docker desktop](https://docs.docker.com/desktop/) regardless of distribution. 

**GPU in Containers**

A plus especially with windows machines with NVIDIA GPUs is that docker desktop provides GPU compatability by default, which isn't the case with linux. If you have Linux machine with GPUs, please see [this guide](gpu-setup.md). When you have managed to setup docker desktop and run hello world, you can check GPU containers with [this yaml](applications/LLMs/inference/compose/gpu-test.yaml).

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

## Kubernetes Networking

The only problem left is setting up easier access to UIs, applications and databases run by the OSS MLOps platform. The default way to do this is to create a local forward with SSH and port forward the service using the following list:

```
# Kubeflow
ssh -L 8080:localhost:8080 cpouta
kubectl port-forward svc/istio-ingressgateway 8080:80 -n istio-system
http://localhost:8080 (address is user@example.com and password 12341234)

# Kubeflow minio
ssh -L 9000:localhost:9000 cpouta
kubectl port-forward svc/minio-service 9000:9000 -n kubeflow
http://localhost:9000 (user is minio and password minio123)

# MLflow
ssh -L 5000:localhost:5000 cpouta
kubectl port-forward svc/mlflow 5000:5000 -n mlflow 
http://localhost:5000

# MLflow MinIO
ssh -L 9001:localhost:9001 cpouta
kubectl port-forward svc/mlflow-minio-service 9001:9001 -n mlflow
http://localhost:9001 (user and password is minioadmin)

# Prometheus
ssh -L 8090:localhost:8090 cpouta
kubectl port-forward svc/prometheus-service 8090:8080 -n monitoring
http://localhost:8090

# Grafana
ssh -L 5050:localhost:5050 cpouta
kubectl port-forward svc/grafana 5050:3000 -n monitoring
http://localhost:5050 (user and password is admin)

# Forwarder frontend
ssh -L 6500:localhost:6500 cpouta
kubectl port-forward svc/fastapi-service 6500:6500 -n forwarder
http://localhost:6500/docs

# Forwarder monitor
ssh -L 6501:localhost:6501 cpouta
kubectl port-forward svc/flower-service 6501:6501 -n forwarder
http://localhost:6501 (username is flower123 and password is flower456)

# Mongo frontend
ssh -L 7200:localhost:7200 cpouta
kubectl port-forward svc/express-service 7200:7200 -n storage
http://localhost:7200 (user is mongo123 and password is mongo456)

# Mongo backend
ssh -L 27017:localhost:27017 cpouta
kubectl port-forward svc/mongo-service 27017:27017 -n storage
http://localhost:27017

# Qdrant
ssh -L 7201:localhost:7201 cpouta
kubectl port-forward svc/qdrant-service 7201:7201 -n storage
http://localhost:7201 (API key is qdrant_key)

# Neo4j 
ssh -L 7474:localhost:7474 cpouta
kubectl port-forward svc/neo4j-service 7474:7474 -n storage
http://localhost:27017 (user is neo4j and password is password)

# Neo4j bolt
ssh -L 7687:localhost:7687 cpouta
kubectl port-forward svc/neo4j-service 7687:7687 -n storage
http://localhost:7687
```

Unfortunelly this requires quite a lot of manual actions, which we can remove using KinD extra mappings, Istio gateways and virtual services. To begin we need to reserve ports for HTTP based dashboards and TCP based API connections. 

Dashboard connections can be handeled using host based routing in a single port, while TCP connections require unique ports. In all these cases we need to understand the difference between Docker ports, nodeports and gateway ports. The docker, nodeport, and gateway list is:


| Target     | Docker port | Nodeport | Gateway port | 
| ---        | ---         | ---      | ---          |
| Dashboards | 5000        | 30950    | 100          |
| Mongo      | 6000        | 31000    | 200          |
| MinIO      | 6001        | 31001    | 201          |
| Qdrant     | 6002        | 31002    | 202          |
| Neo4j      | 6003        | 31003    | 203          |
| Redis      | 6004        | 31004    | 204          |
| PostgreSQL | 6005        | 31005    | 205          |

Here is the etc/hosts for the dashboards:

```
vm_floating_ip kubeflow.oss
vm_floating_ip minio.kubeflow.oss
vm_floating_ip mlflow.oss
vm_floating_ip minio.mlflow.oss
vm_floating_ip prometheus.oss
vm_floating_ip grafana.oss
vm_floating_ip mongo.oss
vm_floating_ip qdrant.oss
vm_floating_ip neo4j.oss
vm_floating_ip minio.oss
vm_floating_ip forwarder.frontend.oss
vm_floating_ip forwarder.monitor.oss
vm_floating_ip kiali.oss
vm_floating_ip ray.main.oss
vm_floating_ip ray.local-1.oss
vm_floating_ip ray.local-2.oss
vm_floating_ip ray.local-3.oss
vm_floating_ip ray.puhti.oss
vm_floating_ip ray.mahti.oss
vm_floating_ip ray.lumi.oss
```

We now need to configure the KinD cluster itself to open and connect ports. This can be done with [extra port mappings](https://kind.sigs.k8s.io/docs/user/configuration/#extra-port-mappings), where address and port in the host computer are opened into docker and into Kubernetes nodeport (range 30000-32767) with the following:

```
extraPortMappings:
- containerPort: 80
  hostPort: 80
  protocol: TCP
- containerPort: 443
  hostPort: 443
  protocol: TCP
- containerPort: 30950 # Kubernetes nodeport
  hostPort: 5000 # Docker port
  protocol: TCP # dashboard
- containerPort: 31000
  hostPort: 6000 
  protocol: TCP
- containerPort: 31001
  hostPort: 6001
  protocol: TCP
- containerPort: 31002
  hostPort: 6002
  protocol: TCP
- containerPort: 31003
  hostPort: 6003
  protocol: TCP
- containerPort: 31004
  hostPort: 6004
  protocol: TCP
- containerPort: 31005
  hostPort: 6005
  protocol: TCP
```

We can add these configurations by modifying [create_cluster.sh](../../../scripts/create_cluster.sh) and [create_gpu_cluster.sh](../../../scripts/create_gpu_cluster.sh). When the cluster is running, we first need t modify istio enviroment variables with the following:

```
kubectl get deployment istiod -n istio-system -o yaml > istiod.yaml
nano istiod.yaml
```

In these file we need to change ENABLE_DEBUG_ON_HTTP to True to enable easier debugging with Kiali. When you have found the variable and changed it, you can apply it with:


```
kubectl apply -f istiod.yaml
```

We can then deploy Kiali with:

```
cd applications/integration/networking
kubectl apply -k kiali
```

You can check that it is running with:

```
kubectl get pods -n istio-system
```

When Kiali is running, you can check its dashboard with:

```
ssh -L 20001:localhost:20001 cpouta
kubectl port-forward svc/kiali 20001:20001 -n istio-system
```

If you have problems either with Istio or Kiali, check their logs with:


```
kubectl logs (pod name) -n istio-system
```

We now need t osetup correct gateways and virtual services, which we can check with:

```
kubectl get gateways -A
kubectl get virtualservices -A
```

With this information, we decide that we want to use the existing istio-ingressgateway, which we need to modify with:

```
kubectl get svc istio-ingressgateway -n istio-system -o yaml
nano istio-ingressgateway
```

There we need to have the following:

```
ports:
- name: status-port
  nodePort: 31802
  port: 15021
  protocol: TCP
  targetPort: 15021
- name: http2
  nodePort: 31949
  port: 80
  protocol: TCP
  targetPort: 8080
- name: https
  nodePort: 31000
  port: 443
  protocol: TCP
  targetPort: 8443
- name: dashboard-http
  nodePort: 30950 # nodeport
  port: 100 # gateway port
  protocol: TCP
  targetPort: 9000 # 
- name: mongo-tcp
  nodePort: 31000
  port: 200
  protocol: TCP
  targetPort: 9001 
- name: minio-tcp
  nodePort: 31001
  port: 201
  protocol: TCP
  targetPort: 9002 
- name: qdrant-tcp
  nodePort: 31002
  port: 202
  protocol: TCP
  targetPort: 9003
- name: neo4j-tcp
  nodePort: 31004
  port: 204
  protocol: TCP
  targetPort: 9004
- name: redis-tcp
  nodePort: 31005
  port: 205 
  protocol: TCP
  targetPort: 9005
- name: postgres-tcp
  nodePort: 31006
  port: 206 
  protocol: TCP
  targetPort: 9006
selector:
  app: istio-ingressgateway
  istio: ingressgateway
sessionAffinity: None
type: NodePort
```

After adding these, apply it with:


```
kubectl apply -f istio-ingressgateway.yaml
```

Now, we can create the necessary [gateways](https://istio.io/latest/docs/reference/config/networking/gateway/) and [virtual services](https://istio.io/latest/docs/reference/config/networking/virtual-service/). The gateway for HTTP UI dashboards is


```
apiVersion: networking.istio.io/v1beta1
kind: Gateway
metadata:
  name: dashboard-gateway
spec:
  selector:
    app: istio-ingressgateway
    istio: ingressgateway
  servers:
  - port:
      name: http
      number: 100
      protocol: HTTP
    hosts:
    - "kubeflow.oss"
    - "minio.kubeflow.oss"
    - "mlflow.oss"
    - "minio.mlflow.oss"
    - "prometheus.oss"
    - "grafana.oss"
    - "mongo.oss"
    - "qdrant.oss"
    - "neo4j.oss"
    - "minio.oss"
    - "forwarder.frontend.oss"
    - "forwarder.monitor.oss"
    - "kiali.oss"
    - "ray.main.oss"
    - "ray.local-1.oss"
    - "ray.local-2.oss"
    - "ray.local-3.oss"
    - "ray.puhti.oss"
    - "ray.mahti.oss"
    - "ray.lumi.oss"
```

The virtual service template for dashboard UIs is:

```
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: (name)-virtualservice
spec:
  hosts:
  - "(host)"
  gateways:
  - dashboard-gateway
  http:
  - route:
    - destination:
        host: (service).(namespace).svc.cluster.local
        port:
          number: (port)
```

This results in a table of following virtual services:

| Name               | Host                   | Service              | Namespace  | Port  |
| ---                | ---                    | ---                  | ---        | ---   |
| Kubeflow           | kubeflow.oss           | ml-pipeline-ui       | kubeflow   | 80    |
| Kubeflow MinIO     | minio.kubeflow.oss     | minio-service        | kubeflow   | 9000  |
| MLflow             | mlflow.oss             | mlflow               | mlflow     | 5000  |
| MLflow MinIO       | minio.mlflow.oss       | mlflow-minio-service | mlflow     | 9001  |
| Prometheus         | prometheus.oss         | prometheus-service   | monitoring | 8080  |
| Grafana            | grafana.oss            | grafana              | monitoring | 3000  |
| Mongo              | mongo.oss              | express-service      | storage    | 7200  |
| Qdrant             | qdrant.oss             | qdrant-service       | storage    | 7201  |
| Neo4j              | neo4j.oss              | neo4j-service        | storage    | 7474  |
| Minio              | minio.oss              | minio-service        | storage    | 9101  |
| Forwarder frontend | forwarder.frontend.oss | fastapi-service      | storage    | 6500  |
| Forwarder monitor  | forwarder.monitor.oss  | flower-service       | forwarder  | 6501  |
| Kiali              | kiali.oss              | kiali                | forwarder  | 20001 |
| Ray main           | ray.main.oss           | ray-head-service     | default    | 8280  |
| Ray local 1 dash   | ray.local-1.oss        | ray-local-dash-1     | default    | 8380  |
| Ray local 2 dash   | ray.local-2.oss        | ray-local-dash-2     | default    | 8381  |
| Ray local 3 dash   | ray.local-3.oss        | ray-local-dash-3     | default    | 8382  |
| Ray puhti dash     | ray.puhti.oss          | ray-hpc-dash-1       | default    | 8480  |
| Ray mahti dash     | ray.mahti.oss          | ray-hpc-dash-2       | default    | 8481  |
| Ray lumi dash      | ray.lumi.oss           | ray-hpc-dash-3       | default    | 8482  |


The templares for TCP connections gateway and virtual service pairs are:

```
apiVersion: networking.istio.io/v1beta1
kind: Gateway
metadata:
  name: (name)-gateway
spec:
  selector:
    app: istio-ingressgateway
    istio: ingressgateway
  servers:
  - port:
      name: tcp
      number: (Port-1)
      protocol: TCP
    hosts:
    - '*'
---
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: (name)-virtualservice
spec:
  hosts:
  - "*"
  gateways:
  - (name)-gateway
  http:
  - match:
    - port: (service-port)
    route:
    - destination:
        host: (service-name).(namespace).svc.cluster.local
        port:
          number: (service-port) 
```

This results in the following table:


| Name       | Gateway | Port  | Service              | Namespace | 
| ---        | ---     | ---   | ---                  | ---       |
| Mongo      | 200     | 27017 | mongo-service        | storage   |
| Qdrant     | 201     | 7201  | qdrant-service       | storage   |
| Neo4j      | 202     | 7687  | neo4j-service        | storage   |
| Redis      | 204     | 6379  | redis-service        | storage   |
| MinIO      | 205     | 9100  | minio-service        | storage   |
| PostgreSQL | 206     | 5532  | postgres-service     | storage   |


When you have created these gateways and virtual services, you can test them by curling the port forward or the localhost. The port forward can be created with 

```
kubectl port-forward svc/neo4j-service 7687:7687 -n storage
```

and you can check the opened KinD ports with


```
docker ps
```

In both cases you can curl the connections with:

```
curl -v -H "Host: qdrant.oss" http://localhost:5000 # HTTP
curl -v http://localhost:(port) # TCP
```

You can see connections with Kiali using its graphs:


and more details with istio logs

```
kubectl logs istio-ingressgateway-(id) -n istio-system
```

When you have confirmed that the connections work, you only need to open firewall to the specific ports. For openstack virtual machines this is done with custom TCP rules, where you provide the port and the allowed IP addresses. After checking curl works, modify your /etc/hosts. This creates the following addresses:

```
http://kubeflow.oss:5000

http://minio.kubeflow.oss:5000

http://mlflow.oss:5000

http://minio.mlflow.oss:5000

http://prometheus.oss:5000

http://grafana.oss:5000

http://mongo.oss:5000

http://qdrant.oss:5000

http://neo4j.oss:5000

http://minio.oss:5000

http://forwarder.frontend.oss:5000

http://forwarder.monitor.oss:5000

http://kiali.oss:5000
```

The security rule can be applied using a port range of 6000:6005, giving the following:

```
mongo = vm_floating_ip:6000 

qdrant = vm_floating_ip:6001

neo4j = vm_floating_ip:6002

redis = vm_floating_ip:6003

minio = vm_floating_ip:6004

postgres = vm_floating_ip:6005
```

## Secure Networking

The security of the current setup relys entirely on the firewall that needs to be constantly changed to enable passage for changed ip addresses. To reduce manual work and provide more secure way of connecting separated nodes, we need to setup a way to secure dashboard and TCP connections.