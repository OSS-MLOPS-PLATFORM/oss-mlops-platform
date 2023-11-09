# Sklearn inference service

This directory contains an example of an inference service (kserve) using a sklearn model.

See [sklearn-iris-model.yaml](sklearn-iris-model.yaml).

## Deploy the model inference service

```bash
# tutorials/resources/try-kserve
kubectl apply -f sklearn-iris-model.yaml
```

Check that the inference service was deployed correctly:

```bash
$ kubectl get inferenceservice -n kubeflow-user-example-com

NAME           URL                                                READY   PREV   LATEST   PREVROLLEDOUTREVISION   LATESTREADYREVISION                    AGE
sklearn-iris   http://sklearn-iris.kserve-inference.example.com   True           100                              sklearn-iris-predictor-default-00001   48m
```

> It might take a few minutes to become "READY".

## Try a prediction request

First, configure the domain name

```bash
kubectl patch cm config-domain --patch '{"data":{"example.com":""}}' -n knative-serving
```


Determine the name of the ingress gateway to the inference service:


```bash
INGRESS_GATEWAY_SERVICE=$(kubectl get svc --namespace istio-system --selector="app=istio-ingressgateway" --output jsonpath='{.items[0].metadata.name}')

echo $INGRESS_GATEWAY_SERVICE
```

Port Forward to the ingress gateway service:

```bash
kubectl port-forward --namespace istio-system svc/${INGRESS_GATEWAY_SERVICE} 8080:80
```

Start another terminal and set the following variables

```bash

export MODEL_NAME=sklearn-iris
export INGRESS_HOST=localhost
export INGRESS_PORT=8080
export SERVICE_HOSTNAME=$(kubectl -n kubeflow-user-example-com get inferenceservice $MODEL_NAME -o jsonpath='{.status.url}' | cut -d "/" -f 3)

echo $SERVICE_HOSTNAME
```

To send a prediction to your model, you need an authentication token. You can get this token from your
browser after login in to Kubeflow, you should be able to find it in the cookies (developer mode). Or you can also get the token
programmatically like in the [`predict.py`](predict.py) script.

```bash
SESSION=<your-token>
```

Send a prediction request:

```bash
# tutorials/resources/try-kserve
curl -v --cookie "authservice_session=${SESSION}" -H "Host: ${SERVICE_HOSTNAME}" http://localhost:8080/v1/models/$MODEL_NAME:predict -d @./iris-input.json
```