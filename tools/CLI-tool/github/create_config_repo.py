import typer
import glob
import subprocess
import sys
import os
import shutil
import yaml

from github_client import GitHubClient

# Define the Typer app
app = typer.Typer()


# Use Typer to define repo_name as an argument
@app.command()
def main(repo_name: str, org_name: str):
    """
    Main function to create a GitHub repository, set up structure, and configure secrets.
    """
    client = GitHubClient()

    print(f"Working with repository: {repo_name}")

    print("Creating a new repository...")
    create_repo(client, repo_name, org_name)

    print("Pushing the repository to GitHub...")
    push_repo()

    print("Creating branches...")
    create_branches()

    print("Adding branch specific files...")
    copy_files()

    print("Setting up the default branch...")
    set_default_branch(client, repo_name, org_name)

    print("Setting up the configuration...")
    set_config(client, org_name)


def create_repo(client: GitHubClient, repo_name, org_name):
    """Create a new GitHub repository."""
    client.create_repo(repo_name, org_name)
    os.chdir(repo_name)


def push_repo():
    """Push the repository to GitHub."""
    main_branch = subprocess.run(
        ["git", "branch", "--show-current"], capture_output=True, text=True, check=True
    ).stdout.strip()
    print("Current branch:", main_branch)
    subprocess.run(f"echo Readme > README.md", shell=True)
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", '"Initial commit"'], check=True)
    subprocess.run(["git", "push", "origin", main_branch], check=True)


def create_branches(branches_to_create=None):
    """Create branches if they don't already exist."""
    if branches_to_create is None:
        branches_to_create = ["development", "staging", "production"]

    results = subprocess.run(
        "git branch -a", shell=True, capture_output=True, text=True
    )
    existing_branches = results.stdout.splitlines()

    for branch in branches_to_create:
        if f"remotes/origin/{branch}" not in existing_branches:
            subprocess.run(["git", "checkout", "-b", branch], check=True)
            subprocess.run(
                ["git", "push", "--set-upstream", "origin", branch], check=True
            )
            print(f"Branch '{branch}' created successfully.")


def copy_files():
    """Copy branch-specific files."""
    script_dir = os.path.dirname(os.path.realpath(__file__))
    files_dir = os.path.join(script_dir, "..", "files")
    
    # Define the file to clean up (relative path since we are in the repo root)
    gitlab_ci_file = '.gitlab-ci.yml'

    # --- DEVELOPMENT BRANCH ---
    subprocess.run(["git", "checkout", "development"], check=True)
    shutil.copytree(os.path.join(files_dir, "development"), ".", dirs_exist_ok=True)
    shutil.copytree(os.path.join(files_dir, "common"), ".", dirs_exist_ok=True)
    
    # 🧹 Clean up redundant template file
    if os.path.exists(gitlab_ci_file):
        os.remove(gitlab_ci_file)
        print("🧹 Removed redundant .gitlab-ci.yml file on the development branch.")

    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "Add branch specific files"], check=True)
    subprocess.run(["git", "push"], check=True)

    # --- PRODUCTION BRANCH ---
    subprocess.run(["git", "checkout", "production"], check=True)
    shutil.copytree(os.path.join(files_dir, "production"), ".", dirs_exist_ok=True)
    shutil.copytree(os.path.join(files_dir, "common"), ".", dirs_exist_ok=True)
    
    # 🧹 Clean up redundant template file
    if os.path.exists(gitlab_ci_file):
        os.remove(gitlab_ci_file)
        print("🧹 Removed redundant .gitlab-ci.yml file on the production branch.")

    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "Add production files"], check=True)
    subprocess.run(["git", "push"], check=True)

    # --- STAGING BRANCH ---
    subprocess.run(["git", "checkout", "staging"], check=True)
    shutil.copytree(os.path.join(files_dir, "staging"), ".", dirs_exist_ok=True)
    shutil.copytree(os.path.join(files_dir, "common"), ".", dirs_exist_ok=True)
    
    # 🧹 Clean up redundant template file
    if os.path.exists(gitlab_ci_file):
        os.remove(gitlab_ci_file)
        print("🧹 Removed redundant .gitlab-ci.yml file on the staging branch.")

    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "Add staging files"], check=True)
    subprocess.run(["git", "push"], check=True)


def set_default_branch(client: GitHubClient, repo_name, org_name):
    """Set the default branch to development."""
    client.set_default_branch(repo_name, org_name, "development")
    typer.echo("Default branch set to 'development'.")


def set_config(client: GitHubClient, org_name: str):
    """Create a config file for GitHub secrets"""

    while True:
        try:
            choice = int(
                input(
                    "Choose an option (1: Interactively create config, 2: Copy an existing config.yaml, 3: Default everything (DEBUG)): "
                )
            )
            if choice >= 1 and choice <= 3:
                break
            else:
                print("Invalid choice. Please select 1, 2 or 3.")
        except ValueError:
            print("Invalid input. Please enter a number (1, 2 or 3).")

    config = None

    if choice == 1:
        print("Specify Kubeflow endpoint (default: http://localhost:8080):")
        kep = input().strip()
        if not kep:
            kep = "http://localhost:8080"

        print("Specify Kubeflow username (default: user@example.com):")
        kun = input().strip()
        if not kun:
            kun = "user@example.com"

        print("Specify Kubeflow password (default: 12341234):")
        kpw = input().strip()
        if not kpw:
            kpw = "12341234"

        print("Add remote cluster private key file path (default: ./ssh_key):")
        remote_key_path = input().strip()
        if not remote_key_path:
            remote_key_path = "./ssh_key"

        print("Specify remote cluster IP:")
        remote_ip = input().strip()
        print("Add remote cluster username:")
        remote_username = input().strip()

        config = {
            "KUBEFLOW_ENDPOINT": kep,
            "KUBEFLOW_USERNAME": kun,
            "KUBEFLOW_PASSWORD": kpw,
            "REMOTE_CLUSTER_SSH_PRIVATE_KEY_PATH": remote_key_path,
            "REMOTE_CLUSTER_SSH_IP": remote_ip,
            "REMOTE_CLUSTER_SSH_USERNAME": remote_username,
        }

        with open("config.yaml", "w") as f:
            yaml.dump(config, f, sort_keys=False)
        print("Configuration saved to 'config.yaml'.")

    elif choice == 2:
        while True:
            try:
                choice = int(
                    input(
                        "Choose an option (1: Give a config file PATH, 2: Give a config file NAME): "
                    )
                )
                if choice in [1, 2]:
                    break
                else:
                    print("Invalid choice. Please select 1 or 2.")
            except ValueError:
                print("Invalid input. Please enter a number (1 or 2).")

        yaml_files = []
        if choice == 1:
            config_dir = input(
                "input the PATH of config .yaml file that you want to use: "
            )

            if os.path.exists(config_dir):
                yaml_files.append(config_dir)
            else:
                print(f"{config_dir} doesn't exist")
                sys.exit(1)

        elif choice == 2:
            home_directory = os.path.expanduser("~")
            config_name = input(
                "input the NAME of config .yaml file that you want to use: "
            )
            if ".yaml" in config_name:
                config_name = config_name[:-5]

            yaml_files = glob.glob(
                f"{home_directory}/**/{config_name}.yaml",
                recursive=True,
                include_hidden=True,
            )
            if not yaml_files:
                print(f"{config_name} doesn't exist")
                sys.exit(1)

        if len(yaml_files) == 1:
            config_file = yaml_files[0]
            print(f"{config_file}")

        elif len(yaml_files) > 1:
            config_file_path_index = 1
            for config_path in yaml_files:
                print(f"[{config_file_path_index}] {config_path}")
                config_file_path_index = config_file_path_index + 1
            while True:
                try:
                    chosen_config_file_path = int(
                        input(
                            "you have multiple configs with the same name in different folders please choose which one you want to use: "
                        )
                    )
                    if chosen_config_file_path in range(1, config_file_path_index + 1):
                        config_file = yaml_files[chosen_config_file_path - 1]
                        break
                    else:
                        print(
                            f"invalid input please choose from 1 to {config_file_path_index - 1}"
                        )
                except ValueError:
                    print(
                        f"Invalid input please choose a number from 1 to {config_file_path_index - 1}"
                    )

        try:
            with open(config_file, "r") as yamlfile:
                config = yaml.safe_load(yamlfile)
        except FileNotFoundError:
            print(f"Error: The specified file does not exist at path: {config_file}")
            exit(1)
    elif choice == 3:
        # Just make everything default for trial runs
        config = {
            "KUBEFLOW_ENDPOINT": "http://localhost:8080",
            "KUBEFLOW_USERNAME": "user@example.com",
            "KUBEFLOW_PASSWORD": "12341234",
            "REMOTE_CLUSTER_SSH_PRIVATE_KEY_PATH": "",
            "REMOTE_CLUSTER_SSH_IP": "",
            "REMOTE_CLUSTER_SSH_USERNAME": "",
        }

    if not config or ("KUBEFLOW_ENDPOINT" not in config):
        exit("Error: The config seems to be malformed!")

    for key, value in config.items():
        print(f"Setting up CI value {key}...")
        if key == "REMOTE_CLUSTER_SSH_PRIVATE_KEY_PATH":
            if value and os.path.isfile(value):
                with open(value) as file:
                    client.set_secret(
                        "REMOTE_CLUSTER_SSH_PRIVATE_KEY", file.read(), org_name
                    )
            else:
                print(
                    f"SSH key path {value} does not point to a valid SSH key! Skipping..."
                )
        else:
            client.set_secret(key, value, org_name)


if __name__ == "__main__":
    app()