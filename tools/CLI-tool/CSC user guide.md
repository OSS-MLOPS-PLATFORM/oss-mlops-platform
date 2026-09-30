# SET UP GUIDE FOR CSC USER:

## I) CSC setup

1. Set up your account in [CSC](https://my.csc.fi/welcome) using HAKA Login (this might takes up to 30 minutes, so no worries if it doesn't allow you in instantly)
2. Create a new project, you should see a button to create new project either in your dashboard pane or in your project pane (this also might takes a while)
3. Once you had your own project you should be able to access it in your project pane
4. When you are in your project, scroll down and there should be a tab call "Services"
5. Add service and choose cPouta as the service to run
6. Login in to cPouta using haka (this also will takes a while)

## II) cPouta setup

### a) Security Group Setup
1. Once you are in cPouta navigate to Security Groups: Network -> Security Groups
2. Create a new security group (DO NOT MODIFY THE DEFAULT SECURITY GROUP IF YOU DON'T KNOW WHAT YOU ARE DOING)
3. Once the new security group had been created you can modify the rule by press on Manage Rules
4. Create a new rule by press on "Add Rule"
5. Choose SSH as rule and leave the rest as it is.

For more information on what does all this step means please consult the [user guide make by CSC](https://docs.csc.fi/cloud/pouta/launch-vm-from-web-gui/#setting-up-ssh-keys)

### b) Key Pairs Setup
1. Navigate to Key Pairs: Compute -> Key Pairs
2. Either import SSH key pair that you had made or create a new key pair by press on Create Key Pair
3. Name your key pair, try to name it in lower case, no space, and no special characters. Key type is SSH Key

**Important:** The key will be save automatically to your computer once you press "Create Key Pair". This will be the only way to access the computer so don't lose it. Type file should be ".pem" for window and linux, for mac it will be ".cer"

Again for more information please consult the [CSC user guide](https://docs.csc.fi/cloud/pouta/launch-vm-from-web-gui/#setting-up-ssh-keys)

### c) Instances setup
1. Navigate to Instances: Compute -> Instances
2. Launch your instance:
    - 2.1. Name your Instance whatever you want
    - 2.2. Flavour choose standard xxlarge as the minium
    - 2.3. Keep the number instance as 1
    - 2.4. Instance Boot Source, choose Boot from Image 
    - 2.5. Image name is "Ubuntu-24.04 (3.5GB)"
    - 2.6. In the "Access & Security" tab check:
        - 2.6.1. if "Key Pair" is the key pair name that you had create previously
        - 2.6.2. Choose both of the security groups
    - 2.7. Launch your Instances by press "Launch"
3. Once your instances is running (see if under Power State it write "Running"), Associate your machine with a floating IP:
    - 3.1. Under "Actions" next to "Create Snapshot" press on the down arrow
    - 3.2. Choose "Associate Floating IP"
    - 3.4. Press on the "+" icon and choose Allocate IP, you don't need to change any settings here
    - Write your IP down somewhere but if you forgot to you can just check in your network tab under "Floating IPs"

Again for more information please consult the [CSC user guide](https://docs.csc.fi/cloud/pouta/launch-vm-from-web-gui/#setting-up-ssh-keys)

## III) Connecting to cPouta machine from your local machine

### For Window user

1. You should install [Window Subsystem for Linux (WSL)](https://learn.microsoft.com/en-us/windows/wsl/install)
2. Move your key pairs that you have save in your computer from the earlier step into your linux environment under `home/<yourusername>/`

The rest of the setup will then be universal!

1. Locate and navigate your key path in your system
2. Change the permission by using the command: `chmod 400 <your_key_name>.pem` or `chmod 400 <your_key_name>.cer` on mac
3. SSH into your Virtual machine with port forwarding so you can access Kubeflow from your local browser:
   ```bash
   ssh -L 8080:localhost:8080 ubuntu@<your_IP> -i <your_key_name>.pem
   ```
   > **Note:** Do not use `sudo` before `ssh` on your local machine. The username is `ubuntu`, not your personal username — see [CSC user guide](https://docs.csc.fi/cloud/pouta/connecting-to-vm/) for explanation.
4. Once inside you should do `sudo apt update` and `sudo apt upgrade`
5. Then you should install docker LTS using the command `sudo apt install docker.io`
6. Check if you had install docker successfully by using `docker version`
7. Clone the Github repo into to the VM
8. go into the Github repo by using `cd`

**\---------This part is for the version of the project where there is error in the setup script\---------**

9. `cd` into scripts
10. Open `install_tools.sh` using either nano or vim
11. Replace the script with the script from this [link](https://github.com/OSS-MLOPS-PLATFORM/oss-mlops-platform/blob/main/scripts/install_tools.sh)

**\---------End\---------**

12. Follow the rest of the tutorial in [Installation guide](https://github.com/OSS-MLOPS-PLATFORM/oss-mlops-platform/blob/main/tools/CLI-tool/Installations%2C%20setups%20and%20usage.md#installations-setups-and-usage)

## IV) Setting Up CI/CD Secrets

After Kubeflow is running on the remote VM, you need to configure your CI/CD pipeline to connect to it automatically. The SSH credentials are stored as secrets — **never commit them to the repository**.

You will need:
- Your VM's **Floating IP**
- Your **SSH private key** (the `.pem` or `.cer` file downloaded earlier)
- SSH username: `ubuntu`

### a) GitHub Secrets

1. Go to your working repository on GitHub.
2. Navigate to **Settings → Secrets and variables → Actions**.
3. Click **New repository secret** and add the following:

   | Secret Name | Value |
   |---|---|
   | `REMOTE_CLUSTER_SSH_IP` | Your VM's Floating IP (e.g. `86.50.x.x`) |
   | `REMOTE_CLUSTER_SSH_USERNAME` | `ubuntu` |
   | `REMOTE_CLUSTER_SSH_PRIVATE_KEY` | Full contents of your `.pem` / `.cer` key file |

   To get the key file contents:
   ```bash
   cat <your_key_name>.pem
   ```
   Copy everything including the `-----BEGIN RSA PRIVATE KEY-----` and `-----END RSA PRIVATE KEY-----` lines.

### b) GitLab Variables

1. Go to your working repository on GitLab.
2. Navigate to **Settings → CI/CD** and expand the **Variables** section.
3. Click **Add variable** and add the following:

   | Variable Name | Value | Type |
   |---|---|---|
   | `REMOTE_CLUSTER_SSH_IP` | Your VM's Floating IP (e.g. `86.50.x.x`) | Variable |
   | `REMOTE_CLUSTER_SSH_USERNAME` | `ubuntu` | Variable |
   | `REMOTE_CLUSTER_SSH_PRIVATE_KEY` | Full contents of your `.pem` / `.cer` key file | **File** |

   > ⚠️ Set `REMOTE_CLUSTER_SSH_PRIVATE_KEY` as type **File**, not Variable. GitLab writes the key contents to a temporary file and passes the file path to the pipeline — the CI script handles both cases automatically.

   > Make sure **Protect variable** is unchecked if you want the variable available on non-protected branches (e.g. `staging`).

Once secrets are configured, any push to the `staging` or `production` branch will trigger the CI/CD pipeline, which SSHs into your CSC VM and submits the Kubeflow pipeline automatically.