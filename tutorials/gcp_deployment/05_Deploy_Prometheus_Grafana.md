# Monitoring with Prometheus & Grafana

In this section, we deploy Prometheus and Grafana on the cluster for monitoring.

## Deploy Prometheus


Create monitoring namespace:

```bash
kubectl create namespace monitoring
```

Check that your overlay is correct by rendering the Kubernetes resources:

```bash
kubectl kustomize deployment/monitoring/prometheus
```

Create the stack:

```bash
kubectl apply -k deployment/monitoring/prometheus
```

### Access the dashboard (Prometheus)

After deployment, the Prometheus **Dashboard** can be access with `kubectl port-forward`.

```bash
kubectl port-forward svc/prometheus-service 8080 -n monitoring
```

Then, it should be reachable at [http://127.0.0.1:8080](http://127.0.0.1:8080).

### Prometheus configuration

The Prometheus [configuration file](https://prometheus.io/docs/prometheus/latest/configuration/configuration/) with all the scrape configs, jobs and alerting rules is defined inside the config map
[`prometheus-config-map.yaml`](../../deployment/monitoring/prometheus/prometheus-config-map.yaml)

> In Prometheus terms, the config for collecting metrics from a collection of endpoints is called a `job`.

To add additional targets for metric scraping you have two options:

- **Option 1** - Use prometheus annotations
    
  This is probably the simplest way, as you don't need to learn the Prometheus specific configuration language.
  You only need to add the following metadata annotation to the .yaml definition of a pod or service.
  Prometheus will find it and automatically add it as a target.

  ```yaml
  metadata:
    annotations:
      prometheus.io/scrape: "true"
      prometheus.io/path: /metrics
      prometheus.io/port: "9090"
  ```
- **Option 2** - Customize the prometheus configuration

  Customize the scraping [configuration file](../../deployment/monitoring/prometheus/prometheus-config-map-ori.yaml) by adding new jobs and targets.
  Please, refer to the [official documentation](https://prometheus.io/docs/prometheus/latest/configuration/configuration/)
  for detailed instructions.

# Deploy Grafana

Check that your overlay is correct by rendering the Kubernetes resources:

```bash
kubectl kustomize deployment/monitoring/grafana
```

Create the stack:

```bash
kubectl apply -k deployment/monitoring/grafana
```

### Access the dashboard (Grafana)

To access Grafana dashboard locally, forward a local port with

```bash
kubectl port-forward svc/grafana 3000:3000 --namespace monitoring
```

Now it should be reachable at [http://localhost:3000](http://localhost:5000).

When logging in for the first time, the user and password are:

- User: `admin`
- Password: `admin`
