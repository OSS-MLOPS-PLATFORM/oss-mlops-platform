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

## Pytorch distributed training

### Ray Cluster Setup

To be able to run the example, the default ray cluster values aren't enough, as it needs more memory and a shared volume/filesystem.

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
$ kubectl get pods -n default | grep ray-head                                                                                                                                                  ✔  ray   kind-kind-ep ⎈  FI  
raycluster-kuberay-head-gdrz6   1/1     Running   0     94m

# Change the permission of the shared nfs volume
$ kubectl exec -it raycluster-kuberay-head-gdrz6 -- sudo chmod -R 777 /home/ray/nfs
```

For more information about Ray Train and the pytorch distributed training example, please check the original [getting-started-pytorch](https://docs.ray.io/en/latest/train/getting-started-pytorch.html) documentation.