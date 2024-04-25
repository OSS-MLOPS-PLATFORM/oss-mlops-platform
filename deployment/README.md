## Deploy the stack

Choose the deployment option that best fits your needs:
1. `kubeflow-monitoring`: Full Kubeflow deployment with all components.
2. `kubeflow`: Full Kubeflow deployment without monitoring components (prometheus, grafana).
3. `standalone-kfp-monitoring`: Standalone KFP deployment.
4. `standalone-kfp`: Standalone KFP deployment without monitoring components (prometheus, grafana).
5. `standalone-kfp-kserve-monitoring`: Standalone KFP and Kserve deployment.
6. `standalone-kfp-kserve`: Standalone KFP and Kserve deployment without monitoring components (prometheus, grafana).

```bash
export DEPLOYMENT_OPTION=kubeflow-monitoring
```

Deploy to your kubernetes cluster with the following command:

```bash
while ! kustomize build "deployment/envs/$DEPLOYMENT_OPTION" | kubectl apply -f -; do echo "Retrying to apply resources"; sleep 10; done
```