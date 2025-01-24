# How to increase Docker Disk Memory

We will go through the necessery configuration on how to make docker utilize a larger disk partition in local and cloud Ubuntu 22.04 enviroments. We assume you have not yet created the cluster. The premilinary configuration is the following:

1. Update the enviroment with
```
sudo apt update
sudo apt upgrade # press enter, when you get a list
```
1. [Install Docker](https://docs.docker.com/engine/install/ubuntu/) 
2. [Remove sudo Docker](https://docs.docker.com/engine/install/linux-postinstall/)

The next steps depend on the enviroment

## CPouta

1. [Create and mount atleast 500GB volume into a VM](https://docs.csc.fi/cloud/pouta/persistent-volumes/)
2. Check current root directory:
```
docker info
```
3. Create a folder in volume
```
cd /media/volume
mkdir docker
```
4. Get its path
```
cd docker
pwd
```
5. Check the docker daemon.json
```
cat /etc/docker/daemon.json
```
6. Shutdown docker
```
sudo systemctl stop docker
sudo systemctl stop docker.socket
sudo systemctl stop containerd
```
7. Edit to have data-root: '/media/volume/docker':
```
sudo nano /etc/docker/daemon.json
```
8. Confirm path:
```
cat /etc/docker/daemon.json
```
9.  Move docker data: 
```
sudo rsync -axPS /var/lib/docker/ /media/volume/docker
```
10. Restart docker
```
sudo systemctl start docker
```
11. Check docker info
```
docker info
```
12. Try running a container
13. If no failures happen, check file system utilization with
```
df -h
```