# Configuring Ingress with Google Auth

In this part, we set up ingress to enable access to deployed resources from the Internet,
using [Google Auth](https://developers.google.com/identity/protocols/oauth2/javascript-implicit-flow)
as external authentication provider. Skip this step if this is not required.

> In this example we set up an ingress for MLflow. You can modify and/or repeat the process for any of the other application (Kubeflow, Grafana, etc.).

## About `cert-manager`

We need a [`cert-manager`](https://cert-manager.io/docs/). It should have already been installed
as part of Kubeflow installation, and you should be able to **skip this step**. If not, please follow the
instructions below to install the `cert-manager`.

`cert-manager` introduces a few resources:

* Issuers [docs](https://cert-manager.io/docs/concepts/issuer/)
* Certificate [docs](https://cert-manager.io/docs/concepts/certificate/)
* CertificateRequests [docs](https://cert-manager.io/docs/concepts/certificaterequest/)
* Orders and Challenges [docs](https://cert-manager.io/docs/concepts/acme-orders-challenges/)

Check [official installation docs](https://cert-manager.io/docs/installation/) for installation instructions.

For example, [install with `kubectl`](https://cert-manager.io/docs/installation/kubectl/#steps):

```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.8.0/cert-manager.yaml
```

## 1. Ingress Controller

Deploy [NGINX Ingress controller](https://github.com/kubernetes/ingress-nginx) using [`deploy.yaml`](https://github.com/kubernetes/ingress-nginx/blob/main/deploy/static/provider/cloud/deploy.yaml):

```bash
kubectl create ns ingress-nginx
kubectl -n ingress-nginx apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/cloud/deploy.yaml
kubectl -n ingress-nginx get pods
kubectl -n ingress-nginx get svc
```

We should be able to see NGINX Ingress Controller IP in `svc` description. Open the
address in your browser, and you should see a `404 Not Found` page indicating the ingress
controller is running.

## 2. Setup cloud DNS

Ask DNS admin to set the external IP of the cloud load balancer as a record for suitable
domain. For example, you might want to expose services at `https://*.mlopsplatformv2.iml4e.com`.

## 3. Create `ClusterIssuer`

Create a `ClusterIssuer` that allows issuing certificates in any namespace:

```yaml
# cert-issuer-nginx-ingress.yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-cluster-issuer
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: your-email@example.com
    privateKeySecretRef:
      name: letsencrypt-cluster-issuer-key
    solvers:
    - http01:
       ingress:
         class: nginx
```

Apply the resource:

```bash
kubectl apply -f cert-issuer-nginx-ingress.yaml
```

Check the issuer is created:

```bash
kubectl describe clusterissuer letsencrypt-cluster-issuer
```

## 4. Use Google Auth external authentication provider

For GCP, the registration steps are:

* Navigate to "APIs & Services" page by searching "APIs & Services" in the search bar of Google Cloud console.
* In the left pane, choose "OAuth consent screen" tab. Fill in "Product name shown to users" and hit save.
* In the center pane, choose "Credentials" tab.
* Open the "New credentials" drop down
* Choose "OAuth client ID"
* Choose "Web application"
* Application name is freeform, choose something appropriate
* Authorized JavaScript origins is the FQDN in the Ingress rule, like `https://mlflow.mlopsplatformv2.iml4e.com`
* Authorized redirect URIs is the location of oauth2/callback ex: `https://mlflow.mlopsplatformv2.iml4e.com/oauth2/callback`
* In future whenever you had a new hostname you need to define it here
* Choose "Create"
* Take note of the Client ID and Client Secret and replace it in kubernetes secret

It's recommended to refresh sessions on a short interval (1h) with cookie-refresh setting which
validates that the account is still authorized.

### 5. Install [`oauth2-proxy`](https://github.com/oauth2-proxy/oauth2-proxy)

Create cookie secret:

```bash
python -c "import secrets; print(secrets.token_urlsafe(), end='')"
```

Create secret `oauth2-proxy` in `kube-system` namespace, including the client ID, client secret, and the cookie secret:

```bash
kubectl create secret -n kube-system generic oauth2-proxy \
  --from-literal=OAUTH2_PROXY_CLIENT_ID=<Client ID> \
  --from-literal=OAUTH2_PROXY_CLIENT_SECRET=<Client Secret> \
  --from-literal=OAUTH2_PROXY_COOKIE_SECRET=<Cookie Secret>
```

Create folder `oauth2-proxy` and a file `deployment.yaml`:

```yaml
# oauth2-proxy/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    app: oauth2-proxy
  name: oauth2-proxy
  namespace: kube-system
spec:
  replicas: 1
  selector:
    matchLabels:
      app: oauth2-proxy
  template:
    metadata:
      labels:
        app: oauth2-proxy
    spec:
      containers:
      - args:
        - --provider=google
        - --email-domain=iml4e.com
        - --upstream=file:///dev/null
        - --http-address=0.0.0.0:4180
        - --cookie-refresh=1h
        env:
        - name: OAUTH2_PROXY_CLIENT_ID
          valueFrom:
            secretKeyRef:
              name: oauth2-proxy
              key: OAUTH2_PROXY_CLIENT_ID
        - name: OAUTH2_PROXY_CLIENT_SECRET
          valueFrom:
            secretKeyRef:
              name: oauth2-proxy
              key: OAUTH2_PROXY_CLIENT_SECRET
        - name: OAUTH2_PROXY_COOKIE_SECRET
          valueFrom:
            secretKeyRef:
              name: oauth2-proxy
              key: OAUTH2_PROXY_COOKIE_SECRET
        image: quay.io/oauth2-proxy/oauth2-proxy:latest
        imagePullPolicy: Always
        name: oauth2-proxy
        ports:
        - containerPort: 4180
          protocol: TCP
```

Create a Service for `oauth2-proxy`:

```yaml
# oauth2-proxy/service.yaml
apiVersion: v1
kind: Service
metadata:
  labels:
    app: oauth2-proxy
  name: oauth2-proxy
  namespace: kube-system
spec:
  ports:
  - name: http
    port: 4180
    protocol: TCP
    targetPort: 4180
  selector:
    app: oauth2-proxy
```

Apply the resources:

```bash
kubectl apply -f oauth2-proxy
```

## 6. Create an ingress

Add `ingress.yaml` for your service using the following template. This example is for MLflow:

```yaml
# mlflow/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  annotations:
    kubernetes.io/ingress.class: "nginx"
    nginx.ingress.kubernetes.io/auth-url: "https://$host/oauth2/auth"
    nginx.ingress.kubernetes.io/auth-signin: "https://$host/oauth2/start?rd=$escaped_request_uri"
    cert-manager.io/cluster-issuer: letsencrypt-cluster-issuer
  name: mlflow-ingress
  namespace: mlflow
spec:
  tls:
  - hosts:
    - mlflow.mlopsplatformv2.iml4e.com
    secretName: mlflow-ingress-cert
  rules:
  - host: mlflow.mlopsplatformv2.iml4e.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service: 
            name: mlflow
            port: 
              number: 5000

---
kind: Service
apiVersion: v1
metadata:
  name: oauth2-proxy
  namespace: mlflow
spec:
  type: ExternalName
  externalName: oauth2-proxy.kube-system

---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  annotations:
    kubernetes.io/ingress.class: "nginx"
  name: mlflow-oauth-ingress
  namespace: mlflow
spec:
  tls:
  - hosts:
    - mlflow.mlopsplatformv2.iml4e.com
    secretName: mlflow-ingress-cert
  rules:
  - host: mlflow.mlopsplatformv2.iml4e.com
    http:
      paths:
      - path: /oauth2
        pathType: Prefix
        backend:
          service:
            name: oauth2-proxy
            port:
              number: 4180
```

Modify `metadata.name`, `metadata.namespace`, `spec.tls.hosts`, `spec.tls.secretName`, and `spec.rules`
as suitable for your application. `cert-manager` will store the created certificate in secret `mlflow-ingress-cert`.

Apply the resources.

Open the address (in the above example, `mlflow.mlopsplatformv2.iml4e.com`) and you should
be able to see the login page.


