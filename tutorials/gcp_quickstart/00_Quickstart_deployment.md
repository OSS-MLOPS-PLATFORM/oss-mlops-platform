<h1>Quickstart Deployment</h1>

This deployment will deploy all the components of the platform inside the cluster (in-cluster).

The [step 1](01_Create_GCP_resources.md) in specific to GCP.
However, the [step 2](02_Deploy_the_stack.md) is the same for any cloud provider,
as long as you have a Kubernetes cluster, as all the components are deployed in-cluster.

> For production environments, it is recommended to use manged services for the databases and artifact storage.
> For a production-ready deployment, please follow the [gcp_deployment](../gcp_deployment) guide.