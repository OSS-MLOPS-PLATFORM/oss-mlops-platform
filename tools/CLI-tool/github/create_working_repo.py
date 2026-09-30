import os
import subprocess
import typer

from github_client import GitHubClient

# Define the Typer app
app = typer.Typer()


# Use Typer to define repo_name as an argument
@app.command()
def main(repo_name: str, org_name: str):
    """
    Main function to fetch repo details and fork it.
    """
    client = GitHubClient()
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


def fork_repo(client: GitHubClient, repo_name: str, org_name: str):
    """Fork the repository using GitHub CLI."""
    working_repo_name = get_working_repo_name(repo_name)

    while client.get_repo(working_repo_name, org_name):
        typer.echo(
            f"The repository name {working_repo_name} is already present in the organization! Please provide a different one."
        )
        working_repo_name = get_working_repo_name(repo_name)

    client.fork_repo(repo_name, org_name, working_repo_name)

    try:
        os.chdir(working_repo_name)
        subprocess.run(
            ["git", "checkout", "-b", "staging", "origin/staging"], check=True
        )
        subprocess.run(
            ["git", "checkout", "-b", "production", "origin/production"], check=True
        )
        subprocess.run(["git", "checkout", "development"], check=True)
        os.chdir("../")
    except FileNotFoundError:
        print(f"{working_repo_name} does not exist")
        exit(1)


if __name__ == "__main__":
    app()
