# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "typer",
# ]
# ///
import json
import os
import subprocess
import sys
import time

import typer
from gitlab_client import GitLabClient

# Define the Typer app
app = typer.Typer()

GITLAB_CONFIG_FILE = os.path.expanduser("~/.gitlab-cli-config.json")


# Use Typer to define repo_name as an argument
@app.command()
def main(repo_name: str, org_name: str):
    """
    Main function to fetch repo details and fork it.
    """
    if not os.path.exists(GITLAB_CONFIG_FILE):
        typer.echo(
            "GitLab configuration not found. Please run 'configure_gitlab.py' first."
        )
        sys.exit(1)

    with open(GITLAB_CONFIG_FILE, "r") as f:
        config = json.load(f)

    client = GitLabClient(config["instance_url"])

    fork_repo(client, repo_name, org_name)


def get_working_repo_name(config_repo_name: str):
    if config_repo_name.startswith("Config-"):
        as_split = config_repo_name.split("-")
        as_split[0] = "Working"
        default_working_repo_name = "-".join(as_split)
        return typer.prompt(
            "Enter unique name for your working repository:",
            type=str,
            default=default_working_repo_name,
        )
    return typer.prompt("Enter unique name for your working repository:", type=str)


def fork_repo(client: GitLabClient, repo_name: str, org_name: str):
    """Fork the repository using the GitLabClient."""
    project_to_fork = client.get_project(f"{org_name}/{repo_name}")
    if not project_to_fork:
        typer.echo(f"Project '{org_name}/{repo_name}' not found.")
        sys.exit(1)

    group_to_fork_into = client.get_group_id(org_name)
    if not group_to_fork_into:
        typer.echo(f"Group '{org_name}' not found.")
        sys.exit(1)

    working_repo_name = get_working_repo_name(repo_name)

    while client.get_project(f"{org_name}/{working_repo_name}"):
        typer.echo(
            f"The repository name {working_repo_name} is already present in the organization! Please provide a different one."
        )
        working_repo_name = get_working_repo_name(repo_name)

    try:
        forked_project = client.fork_project(
            project_to_fork["id"], group_to_fork_into, working_repo_name
        )
        typer.echo(f"Forking repository {repo_name} to {working_repo_name}...")

        # Wait for the fork to complete
        while True:
            project = client.get_project(f"{org_name}/{working_repo_name}")
            if project and project.get("import_status") == "finished":
                break
            time.sleep(2)

        typer.echo(f"Cloning repository {working_repo_name}")
        subprocess.run(["glab", "repo", "clone", forked_project["path_with_namespace"]], check=True)

        os.chdir(working_repo_name)
        subprocess.run(["git", "remote", "set-url", "origin", forked_project["http_url_to_repo"]], check=True)
        subprocess.run(
            ["git", "checkout", "-b", "staging", "origin/staging"], check=True
        )
        subprocess.run(
            ["git", "checkout", "-b", "production", "origin/production"], check=True
        )
        subprocess.run(["git", "checkout", "development"], check=True)
        os.chdir("../")

    except Exception as e:
        typer.echo(f"Failed to fork repository: {e}")
        sys.exit(1)


if __name__ == "__main__":
    app()


