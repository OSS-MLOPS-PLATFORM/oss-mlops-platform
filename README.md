# OSS MLOps Platform

Welcome to the OSS MLOps Platform, a comprehensive suite designed to streamline your machine learning operations from experimentation to deployment.

![logos.png](resources/img/logos.png)

## Overview of Project Structure

- **Setup Scripts**
  - [`setup.sh`](setup.sh): The primary script to install and configure the platform on your local machine.
  - [`setup.md`](setup.md): Detailed documentation for platform setup and testing procedures.

- **Deployment Resources**
  - [`deployment/`](deployment): Contains Kubernetes deployment manifests and configurations for Infrastructure as Code (IaC) practices.

- **Tutorials and Guides**
  - [`tutorials/`](tutorials): A collection of resources to help you understand and utilize the platform effectively.
    - [`local_deployment/`](tutorials/local_deployment): A comprehensive guide for local deployment, including configuration and testing instructions.
    - [`gcp_quickstart/`](tutorials/gcp_quickstart): A guide for a quickstart deployment of the platform to GCP.
    - [`gcp_deployment/`](tutorials/gcp_deployment): A guide for a production-ready deployment of the platform to GCP.
    - [`demo_notebooks/`](tutorials/demo_notebooks): A set of Jupyter notebooks showcasing example ML pipelines.

- **Testing Suite**
  - [`tests/`](tests): A suite of tests designed to ensure the platform's integrity post-deployment.

## Special Instructions for Mac Users

> **Important Notice for Mac Users:** Ensure Docker Desktop is installed on your machine, not Rancher Desktop, to avoid conflicts during the `kubectl` installation process.

If Rancher Desktop was previously installed, please uninstall it and switch to Docker Desktop. Update your Docker context with the following command:

```bash
docker context use default
```

Additionally, confirm that Xcode is installed correctly to prevent potential issues:

```bash
xcode-select --install
```

## Getting Started with a local setup

To set up the platform locally, execute the [`setup.sh`](setup.sh) script. For a concise setup overview, refer to the [setup guide](setup.md), or for a more detailed approach, consult the [manual setup instructions](tutorials/local_deployment).

## Exploring Demo Examples

Dive into our demo examples to see the platform in action:

- **Jupyter Notebooks (e2e)**:

  - [Demo Wine quality ML pipeline.](tutorials/demo_notebooks/demo_pipeline)

  - [Demo Fairness and energy monitoring pipeline.](tutorials/demo_notebooks/demo_fairness_and_energy_monitoring)


- **Project Use-Cases (e2e)**:

  - [Fashion-MNIST MLOPS pipeline](https://github.com/OSS-MLOPS-PLATFORM/demo-fmnist-mlops-pipeline)

## High-Level Architecture Overview

The following diagram illustrates the architectural design of the MLOps platform:

![MLOps Platform Architecture](resources/img/mlops-platform-diagram.png)

### Key Components

- **Kind**: Simplifies local Kubernetes cluster setup.
- **Kubernetes**: The backbone container orchestrator.
- **MLFlow**: Manages experiment tracking and model registry.
  - **PostgreSQL DB**: Stores metadata for parameters and metrics.
  - **MinIO**: An artifact store for ML models.
- **Kubeflow**: Orchestrates ML workflows.
- **KServe**: Facilitates model deployment and serving.
- **Prometheus & Grafana**: Provides monitoring solutions with advanced visualization capabilities.

## Support & Feedback

Join our Slack [oss-mlops-platform](https://join.slack.com/t/oss-mlops-platform/shared_invite/zt-28m00bllw-0zl2cuKILh6oa2dIwDN_DQ)
workspace for issues, support requests or just discussing feedback.

Alternatively, feel free to use GitHub Issues for bugs, tasks or ideas to be discussed.

Contact people:

Harry Souris - harry.souris@silo.ai

Joaquin Rives - joaquin.rives@silo.ai
