import subprocess

import typer


class GitHubClient:
    def __init__(self):
        pass

    def create_repo(self, repo_name, org_name):
        """Create a new GitHub repository."""
        try:
            subprocess.run(
                [
                    "gh",
                    "repo",
                    "create",
                    f"{org_name}/{repo_name}",
                    "--public",
                    "--description",
                    "Upstream repository",
                    "--clone",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            typer.echo(f"Repository '{repo_name}' created successfully.")
        except subprocess.CalledProcessError as e:
            if "already exists" in e.stderr:
                typer.echo("Repository already exists.")
            else:
                typer.echo(f"Error creating repository: {e.stderr}")
                raise

    def get_repo(self, repo_name, org_name):
        """Get a repository by its name and organization."""
        result = subprocess.run(
            ["gh", "repo", "view", f"{org_name}/{repo_name}"],
            capture_output=True,
            text=True,
        )
        return result.returncode == 0

    def fork_repo(self, repo_name, org_name, fork_name):
        """Fork a repository into an organization."""
        try:
            subprocess.run(
                [
                    "gh",
                    "repo",
                    "fork",
                    f"{org_name}/{repo_name}",
                    f"--org={org_name}",
                    f"--fork-name={fork_name}",
                    "--clone=true",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
        except subprocess.CalledProcessError as e:
            typer.echo(f"Error forking repository: {e.stderr}")
            raise

    def set_secret(self, secret_name, secret_value, org_name):
        """Set a secret at the organization level."""
        # Note: fixup secret value in case of empty secret (default IP, ETC...)
        if len(secret_value) == 0:
            secret_value = '""'
        try:
            subprocess.run(
                [
                    "gh",
                    "secret",
                    "set",
                    secret_name,
                    "-b",
                    secret_value,
                    f"--org={org_name}",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
        except subprocess.CalledProcessError as e:
            typer.echo(f"Error setting secret: {e.stderr}")
            raise

    def set_default_branch(self, repo_name, org_name, branch_name):
        """Set the default branch for a repository."""
        try:
            subprocess.run(
                [
                    "gh",
                    "repo",
                    "edit",
                    f"{org_name}/{repo_name}",
                    f"--default-branch={branch_name}",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
        except subprocess.CalledProcessError as e:
            typer.echo(f"Error setting default branch: {e.stderr}")
            raise
