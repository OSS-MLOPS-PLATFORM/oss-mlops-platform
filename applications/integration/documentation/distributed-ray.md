# How to create a distributed Ray cluster

We will go through how to connect separated Ray workers either run in containers or SLURM into the same Ray head node run either in Docker compose or Kubernetes. We assume that you have local computers/cloud virtual machines with Docker installed or access to supercomputer with suitable Ray configuration.

## Local Docker Compose

If you have either multiple laptops or workstations, it is recommeded to install [docker desktop](https://docs.docker.com/desktop/) regardless of distribution. 

**GPU in Containers**

A plus especially with windows machines with NVIDIA GPUs is that docker desktop provides GPU compatability by default, which isn't the case with linux. If you have Linux machine with GPUs, please see [this guide](tutorials/integration/gpu-support.md). When you have managed to setup docker desktop and run hello world, you can check GPU containers with [this yaml](applications/LLMs/inference/compose/gpu-test.yaml).

**Container Networking**

When Ray is run in a single machine, we can create Ray workers and give them the head worker address using the following command:

```
bash -c "ray start --address=ray-head:6379 --block"
```

The main problem of connecting separated Ray workers is that how exactly can container, virtual machine and system isolated applications connect to each other in a secure manner. The default way to do this is just creating SSH connections between the separated computers. Check the following


```
sudo systemctl status ssh
cat /etc/ssh/sshd_config
```

If these exists, but ssh server is inactive, run 


```
sudo systemctl start ssh
```

and modify the sshd_config to have the following:


```
sudo nano /etc/ssh/sshd_config

PubkeyAuthentication yes
AllowTcpForwarding yes
GatewayPorts yes
```

to make these changes, run 

```
sudo systemctl restart ssh
```

Now, generate a private key for ray worker computers:

```
ssh-keygen -f ~/.ssh/ray_worker_key
```


but this will quickly get manually cumbersome with system differences. Thus, we need to have a way that enables easy access to a remote addess with the ability to block any other addresses from connecting to it.