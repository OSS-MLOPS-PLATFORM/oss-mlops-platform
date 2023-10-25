# Setup ingress

In order to access Kubeflow, MLflow, etc. through the network without having to
use `port-forward`, we need to set up NGINX ingress controller and create ingresses for
the different services.

In this tutorial we will see how to get the ingresses working. We will use NGINX to
route to these services.

## 1. Deploy Ingress controller (NGINX)

NGINX is a free, open-source, high-performance HTTP server and reverse proxy.

```bash
# /deployment
mkdir nginx
wget https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml -O nginx/nginx-kind-deployment.yaml
kubectl apply -f nginx/nginx-kind-deployment.yaml
```

The manifests contain kind specific patches to forward the hostPorts to the ingress
controller, set taint tolerations and schedule it to the custom labelled node.

## 2. Create ingresses

We will create ingresses for the following services:

- Kubeflow Dashboard
- MLflow server
- MinIO (MLflow)
- Prometheus
- Grafana


```bash
# mlflow-ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: mlflow-ingress
  namespace: mlflow
  annotations:
    kubernetes.io/ingress.class: nginx
    nginx.ingress.kubernetes.il/add-base-url: "true"
spec:
  rules:
  - host: mlflow-server.local
    http:
      paths:
        - backend:
            service:
              name: mlflow
              port:
                number: 5000
          path: /
          pathType: Prefix
```

```bash
# kubeflow-ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: kubeflow-ingress
  namespace: istio-system
  annotations:
    kubernetes.io/ingress.class: nginx
    nginx.ingress.kubernetes.il/add-base-url: "true"
spec:
  rules:
  - host: kubeflow.local
    http:
      paths:
        - backend:
            service:
              name: istio-ingressgateway
              port:
                number: 80
          path: /
          pathType: Prefix
```

```bash
# minio-ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: mlflow-minio-ingress
  annotations:
    kubernetes.io/ingress.class: nginx
    nginx.ingress.kubernetes.il/add-base-url: "true"
    nginx.ingress.kubernetes.io/ssl-redirect: "false"
spec:
  rules:
  - host: mlflow-minio.local
    http:
      paths:
        - backend:
            service:
              name: mlflow-minio-service
              port:
                number: 9001
          path: /
          pathType: Prefix
```

```bash
# prometheus-ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: prometheus-ingress
  namespace: monitoring
  annotations:
    kubernetes.io/ingress.class: nginx
    nginx.ingress.kubernetes.il/add-base-url: "true"
spec:
    rules:
    - host: prometheus.local
        http:
        paths:
            - backend:
                service:
                name: prometheus-service
                port:
                    number: 8080
            path: /
            pathType: Prefix
```

```bash
# grafana-ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: grafana-ingress
  namespace: monitoring
  annotations:
    kubernetes.io/ingress.class: nginx
    nginx.ingress.kubernetes.il/add-base-url: "true"
spec:
    rules:
    - host: grafana.local
        http:
        paths:
            - backend:
                service:
                name: grafana
                port:
                    number: 3000
            path: /
            pathType: Prefix
```


## 3. Update hosts

Map the cluster IP to the host names in your `/etc/hosts` file.

Open your `/etc/hosts` file. E.g.
```bash
sudo nano /etc/hosts
```

Append the following line with the IP of the cluster and save the changes.

```
0.0.0.0 mlflow-server.local mlflow-minio.local kubeflow.local prometheus.local grafana.local
```

> To access the ingresses from another computer in the local network, replace `0.0.0.0`
> with the real IP of the computer running the cluster. 

Now the ingress is all setup. You should be able to access these services by simple
navigating on your browser to their addresses:

- KFP UI: [http://ml-pipeline-ui.local](http://ml-pipeline-ui.local)
- MLflow UI: [http://mlflow-server.local](http://mlflow-server.local)
- MinIO (MLflow) UI: [http://mlflow-minio.local](http://mlflow-minio.local)
- Prometheus UI: [http://prometheus.local](http://prometheus.local)
- Grafana UI: [http://grafana.local](http://grafana.local)
