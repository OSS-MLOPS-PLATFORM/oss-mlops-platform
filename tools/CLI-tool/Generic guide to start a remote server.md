# Generic Setup Guide for Deploying the Platform to a Remote Computer

This is just a generic setup guide or checklist to ensure that you can have the platform up and running on a remote computer for your own use cases.

1. **Computing Power**: Your vendors should have multiple options for computing power. Please choose one that has a minimum of 8 CPUs and 16GB Memory. This is only applicable for the Standalone KFP and Kserve. Depending on your use case, you may need more than this; this is only the minimum requirement.

2. **Network Security**: Depending on the vendor, you most likely need to set up your own network security barrier (allow certain port forwarding/port access). You will need to at least open a port for SSH connection (usually it's port 22). Consult your vendor's user manual for more details on how to set it up.

3. **Security Configuration**: Set up the security so that it will allow a certain network range to be able to SSH tunnel into the remote computer.

4. **Keypair Security**: The vendor's service will need to be secure in some form or another, usually in the form of public and private key pairs. You will need to save this key somewhere on your local computer to be able to access the remote server.

5. **Key Permission**: You may need to modify the key that you receive in step 4's permission to start using it for security reasons. This totally depends on the software and the OS that you are using.

6. **Remote Computer Setup**: Now you can start to create your remote computer if you haven't already. Ensure that the remote computer uses your network security and recognizes your key.

7. **Floating IPs**: Associate your remote computer with floating IPs (your service should also provide this usually). This is required for the SSH connection between your local computer and the remote one. Please note it down somewhere.

8. **SSH Connection**: With all of that setup, now you can connect to your remote computer via SSH tunnel or any software of your choice. When connecting, include port forwarding so you can access the Kubeflow UI from your local browser:
   ```bash
   ssh -L 8080:localhost:8080 <username>@<floating_ip> -i <your_key>.pem
   ```

9. **System Update & Docker**: Once inside the remote computer, update the system and install Docker before running the setup script:
   ```bash
   sudo apt update && sudo apt upgrade -y
   sudo apt install docker.io -y
   ```

10. **GitHub Project**: Once you are in, you can clone the GitHub project and continue the rest of the installation as shown in the [Installation guide](https://github.com/OSS-MLOPS-PLATFORM/oss-mlops-platform/blob/main/tools/CLI-tool/Installations%2C%20setups%20and%20usage.md#installations-setups-and-usage).

11. **CI/CD Secrets**: After the platform is running, configure your CI/CD pipeline to connect to the remote server automatically. Store the SSH credentials as secrets — never commit them to the repository.

    - **GitHub**: Go to your repository → **Settings → Secrets and variables → Actions** → add the following secrets:

      | Secret Name | Value |
      |---|---|
      | `REMOTE_CLUSTER_SSH_IP` | Your floating IP |
      | `REMOTE_CLUSTER_SSH_USERNAME` | Your VM username (e.g. `ubuntu`) |
      | `REMOTE_CLUSTER_SSH_PRIVATE_KEY` | Full contents of your `.pem` / `.cer` key file |

    - **GitLab**: Go to your repository → **Settings → CI/CD → Variables** → add the same variables. Set `REMOTE_CLUSTER_SSH_PRIVATE_KEY` as type **File** (GitLab writes the key to a temporary file and passes the path to the pipeline).