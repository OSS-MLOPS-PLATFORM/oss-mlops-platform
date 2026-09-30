# TO BE DELETED SEE NEWER GUIDE AT https://github.com/OSS-MLOPS-PLATFORM/oss-mlops-platform/blob/main/tools/CLI-tool/Installations%2C%20setups%20and%20usage.md

# Starting a run on local ML-OPS Platform

## Step 0: Cloning the main repo, setting up Docker and creating a SSH connection to GitHub

Clone the main repository to your local folder:

```
git clone https://github.com/OSS-MLOPS-PLATFORM/oss-mlops-platform.git
```
For Windows machines you need a WSL environment with (default Ubuntu) and it's unix commandline.

https://learn.microsoft.com/en-us/windows/wsl/install

You also need Docker working on your machine.

https://www.docker.com/products/docker-desktop/

Your WSL setup might need GitHub authentication credentials setup. (Instructions for Mac users are included there aswell.)

https://docs.github.com/en/get-started/getting-started-with-git/caching-your-github-credentials-in-git?platform=linux

Macs need the `Homebrew` installed for the platform installer.

https://brew.sh/

*Note: This following SSH step might be unneccessary.* 

You need to have SSH key added to GitHub for multiple steps. USE ONE WITHOUT THE PASSPHRASE. 

https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent

For Linux, follow the same steps as with WSL. If you have a different package manager to apt, install the packages through your favorite package manager.

## Step 1: Installing local ML-OPS platform

Run the setup script in the main repository's folder:

```
./setup.sh
```
For local installation you want the **stand alone kfp and kserve** and tell the installer **NO to the docker registry and Ray questions** also use the recommended Kubernetes version. 

**The installation will take time and some of the pods can get stuck.** You can delete them and they are spun up again in a working manner hopefully.

### Some problem solving with the local cluster:

Checking the status of the pods:

```
kubectl get pods --all-namespaces
```

Deleting a pod incase of it getting stuck in a crash loop or an error:
```
kubectl delete pod -n <namespace> <pod_name>
```
Once you get all the pods running they should start up correctly each time you start the cluster again.

The guides for this are scattered in here https://github.com/OSS-MLOPS-PLATFORM/oss-mlops-platform/tree/main/tutorials/local_deployment but they predate the installer which is prefered to be used.

The run might fail at deploy-model step due to wine-quality inference service being already running. This can be solved by deleting the service:

```
kubectl delete inferenceservice wine-quality -n kserve-inference
```

## Step 2 Portforwarding the Kubeflow ports

Every time you start up the cluster you have to portforward the ports from inside the containers so they can be accessed from for example your browser.

Forward the ports:
```
kubectl -n mlflow port-forward svc/mlflow 5000:5000
```

```
kubectl port-forward svc/ml-pipeline-ui -n kubeflow 8080:80
```

After this step you should be able to connect to the Kubeflow interface from http://localhost:8080/

The default email address is `user@example.com` and the default password is `12341234`.

At this point you can test the cluster with the pipeline in a notebook for the stand alone kfp installation. Separate installation of Jupyter Notebook environment work for running the notebook. Jupyter Notebook installation guide: https://jupyter.org/install

Notebook location:
https://github.com/OSS-MLOPS-PLATFORM/oss-mlops-platform/blob/main/tutorials/demo_notebooks/demo_pipeline_standalone_kfp/demo-pipeline.ipynb

## Step 3 Creating the repositories and setting up the CI/CD pipeline with the tool

### Base requirements for the tool

- WSL (if using Windows, MacOS can skip)
    - MacOS already has a Unix compliant terminal
- Linux (default Ubuntu) on the WSL
- (Setup python env)
    - Not required but good practise and skips warnings
- Clone a version of oss-mlops-platform repo 
    - Try not to clone it into the root folder but some project folder instead
    - In Windows you want to do this on the Unix

```
git clone https://github.com/OSS-MLOPS-PLATFORM/oss-mlops-platform.git
```
**N.B.! LINK IS TO THE TOOL PROJECT REPO !**

### Steps for using the tooling

1. Install `gh` (version 2.45 and up on the Unix terminal)

```
sudo apt update
```

```
sudo apt install gh
```

2. Install `pip` on to the Unix terminal
    - https://linuxconfig.org/install-pip-on-linux

```
sudo apt install python3-pip
```

3. Create GitHub token (classic, all premissions)
    - https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#creating-a-personal-access-token-classic
4. Authenticate to GitHub with the GitHub Token
    - Choose options: GitHub.com -> HTTPS -> yes -> Token

```
gh auth login
```

5. Set Git user globals (if not set already)
    - "Your Name" NOT Your Name, use the quotation marks

```
git config --global --list
```

```
git config --global user.name "Your Name"
```

```
git config --global user.email "your.email@example.com"
```

6. Run the tool on the Unix terminal
    - Navigate to the same level where the oss-mlops-project folder is on
        - You need to be outside of git controlled folder because the tool creates local folder structures into the folder where the tool is run
    - By default choose the option 4 for both config and working repos
    - Please use a naming convetion for config repo and working repos
        - It's for YOUR convenience and for others'
        - f.ex. `confJames` and `workJames`
    - N.B.! Currently the tool will require quite a few empty inputs with ENTER presses

```
oss-mlops-platform/tools/CLI-tool/create_gitrepo_devops_for_ml_work.sh
``` 

## Step 4 Installing GitHub Actions runner

You also need a local-hosted GitHub Actions runner which is provided by GitHub. The runner is bound to a single GitHub organization or a single repository. It can be changed later, see note at the end of this step.

1. Navigate to your working repo's `Settings` in GitHub web page.
2. Open the `Actions` dropdown menu from the left side of the page under Code and automation.
3. Select the `Runners`
4. Click on the green button that says `New self-hosted runner`
5. Select the appropriate runner image 
   - For Windows select Linux x64 and use the WSL Linux command line
6. Copy and run the commands one by one
7. Afterwards you should have a self-hosted GitHub Actions runner waiting for jobs.

You can restart the runner after the next computer restart by navigating to the runner's `actions-runner/` folder and running:

```
./run.sh
```

**Note about reconfiguring the runner**

If you need to change the repository runners is connected to, you need to either locate to he repository/organization the runner is connected to in GitHub site and remove it (GitHub will give you the script for it) OR delete the *hidden* `.runner` file in the `actions-runner/` folder and redo the step with the new token. *Also do note the runner OS version, don't be like me and try to use the Windows version on Linux.*

## Step 5 Starting the run on local ML-OPS platform

If everything is in order then by pushing to your working repository GitHub should order the runner on your computer to start the run on your computer's Kubeflow setup.
