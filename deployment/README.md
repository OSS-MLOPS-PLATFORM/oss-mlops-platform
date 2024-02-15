## Deploy the stack

Deploy to your kubernetes cluster with the following command:

```bash
while ! kustomize build deployment | kubectl apply -f -; do echo "Retrying to apply resources"; sleep 10; done
```