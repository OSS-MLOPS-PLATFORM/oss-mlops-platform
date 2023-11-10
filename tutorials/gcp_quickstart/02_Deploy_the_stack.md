<h1>Deployment</h1>

[TOC]

## Prerequisites

- [curl](https://curl.se/)
- [docker](https://docs.docker.com/engine/install/ubuntu/)
- [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/)
- [kind](https://kind.sigs.k8s.io/docs/user/quick-start/#installation)

## 2. Deploy the stack

Deploy all the components of the platform with:

```bash
while ! kustomize build deployment | kubectl apply -f -; do echo "Retrying to apply resources"; sleep 10; done
```

