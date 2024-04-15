# Ray Train

Ray Train is a scalable machine learning library for distributed training and fine-tuning.

Ray Train allows you to scale model training code from a single machine to a cluster of machines in the cloud, and abstracts away the complexities of distributed computing. Whether you have large models or large datasets, Ray Train is the simplest solution for distributed training.

Ray Train provides support for many frameworks:

| PyTorch Ecosystem          | More Frameworks |
|----------------------------|-----------------|
| PyTorch                    | TensorFlow      |
| PyTorch Lightning          | Keras           |
| Hugging Face Transformers  | Horovod         |
| Hugging Face Accelerate    | XGBoost         |
| DeepSpeed                  | LightGBM        |

## Ray Cluster Setup

To be able to run this examples, the default ray cluster values aren't enough, as it needs more memory and a shared volume/filesystem.

To deploy (or redeploy) the cluster with the correct values, you can use the following commands:

```bash
# delete the existing cluster (if already deployed)
helm uninstall raycluster
# deploy the cluster with the new values
helm install raycluster kuberay/ray-cluster -f tutorials/ray/ray_train/values.yaml --version 1.0.0 --set image.tag=2.7.0
```

After that, you might still need to change the permissions of the shared volume `nfs` used for the training:

```bash
# get the name of the Ray head pod
$ kubectl get pods -n default | grep ray-head
raycluster-kuberay-head-gdrz6   1/1     Running   0     94m

# Change the permission of the shared nfs volume
$ kubectl exec -it raycluster-kuberay-head-gdrz6 -- sudo chmod -R 777 /home/ray/nfs
```

For more information about Ray Train and the pytorch distributed training example, please check the original [getting-started-pytorch](https://docs.ray.io/en/latest/train/getting-started-pytorch.html) documentation.

## Example 1: Pytorch distributed training

This example shows how to use Ray Train to scale PyTorch training from a single machine to a cluster of machines in the cloud.

- [pytorch_distributed_training.ipynb](pytorch_distributed_training.ipynb) (notebook)
- [pytorch_distributed_training.py](pytorch_distributed_training.py) (script)

## Example 2: Pytorch training e2e

In this example, we use Ray data for distributed data loading, processing and streaming.

The batches of data are fed in a streaming fashion from the preprocessing workers into the training workers as needed during training.
Thus, allowing us to:
- scale the training to large datasets that do not fit into memory
- scale the preprocessing to multiple machines so that it does not become a bottleneck

> Note: This example can't be run from your local machine, it needs to be run from the cluster head node.

### 1. Install dependencies

You need to install the dependencies on the cluster head and worker nodes. There are different ways to do this, for example:

Connect to the cluster head node and install the dependencies:

```bash
# find the pod name of the ray head node
$ kubectl get pods -n default | grep ray-head

raycluster-kuberay-head-gdrz6   1/1     Running   5 (87m ago)   4d22h

# connect to the pod
$ kubectl exec -it raycluster-kuberay-head-gdrz6 -- bash

# install the dependencies
ray@raycluster-kuberay-head-gdrz6:~$ pip install torch torchvision
```

Connect to the cluster worker group and install the dependencies:

```bash
# find the pod name of the ray worker node
$ kubectl get pods -n default | grep ray-worker

raycluster-kuberay-worker-workergroup-v2hkd     1/1     Running   4 (89m ago)   4d22h

# connect to the pod
$ kubectl exec -it raycluster-kuberay-worker-workergroup-v2hkd -- bash

# install the dependencies
ray@raycluster-kuberay-worker-workergroup-v2hkd:~$ pip install torch torchvision
```

### 3. Upload the script to the cluster

You can upload the script to the cluster using the `kubectl cp` command:

```bash
# upload the script to the cluster
kubectl cp pytorch_training_e2e.py raycluster-kuberay-head-gdrz6:/home/ray/
```

### 4. Run the script

Connect to the cluster head node and run the script:

```bash
# connect to the pod
$ kubectl exec -it raycluster-kuberay-head-gdrz6 -- bash

# run the script
ray@raycluster-kuberay-head-gdrz6:~$ python pytorch_training_e2e.py --data-size-gb=1 --num-epochs=2 --num-workers=1 --smoke-test
```
