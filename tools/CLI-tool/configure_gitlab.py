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

import typer

app = typer.Typer()

GITLAB_CONFIG_FILE = os.path.expanduser("~/.gitlab-cli-config.json")


@app.command()
def main(
    platform: str = typer.Option("gitlab", help="Choose platform: github or gitlab"),
):
    """
    Checks for GitLab CLI and configures GitLab authentication.
    """
    print("Checking GitLab CLI installation...")
    check_glab_installed()
    print("Configuring GitLab authentication...")
    configure_gitlab_auth()


def install_glab():
    """Install GitLab CLI based on the OS."""
    if typer.confirm("Do you want to install GitLab CLI (glab)?"):
        if sys.platform == "darwin":
            subprocess.run(["brew", "install", "glab"], check=True)
        elif sys.platform == "linux":
            subprocess.run(
                "command -v sudo >/dev/null && sudo apt install glab || apt install glab",
                shell=True,
                check=True,
            )
        else:
            typer.echo("Unsupported OS. Please install GitLab CLI manually.")
            sys.exit(1)
    else:
        typer.echo("GitLab CLI (glab) is required. Exiting...")
        sys.exit(1)


def check_glab_installed():
    """Check if GitLab CLI is installed and install it if not."""
    try:
        result = subprocess.run(["glab", "--version"], capture_output=True, text=True)
        if result.returncode != 0:
            typer.echo("GitLab CLI (glab) is not installed.")
            install_glab()
    except (FileNotFoundError, subprocess.CalledProcessError):
        typer.echo("GitLab CLI (glab) is not installed.")
        install_glab()

def configure_gitlab_auth():
    """Configure authentication for a GitLab instance using `glab auth`."""
    instance_url = typer.prompt(
        "Enter your GitLab instance URL (e.g., https://gitlab.example.com)",
        default="https://gitlab.com",
    )
    hostname = instance_url.replace("https://", "").replace("http://", "").rstrip("/")

    try:
        # Check if already logged in
        subprocess.run(
            ["glab", "auth", "status", "--hostname", hostname],
            check=True,
            capture_output=True,
            text=True,
        )
        typer.echo(f"✓ Already logged in to {hostname}.")
        if not typer.confirm("Do you want to re-authenticate?"):
            config = {"instance_url": instance_url}
            with open(GITLAB_CONFIG_FILE, "w") as f:
                json.dump(config, f)
            typer.echo(f"Configuration file updated at {GITLAB_CONFIG_FILE}")
            return
    except subprocess.CalledProcessError:
        # Not logged in, so proceed to login
        pass

    typer.echo("Proceeding with GitLab authentication...")
    try:
        # `glab auth login` is interactive
        subprocess.run(["glab", "auth", "login", "--hostname", hostname], check=True)

        # Verify login status
        subprocess.run(
            ["glab", "auth", "status", "--hostname", hostname],
            check=True,
            capture_output=True,
        )
        typer.echo(f"Successfully authenticated with {hostname}")

        config = {"instance_url": instance_url}
        with open(GITLAB_CONFIG_FILE, "w") as f:
            json.dump(config, f)
        typer.echo(f"Configuration saved to {GITLAB_CONFIG_FILE}")

    except (subprocess.CalledProcessError, KeyboardInterrupt):
        typer.echo("\nAuthentication process failed or was cancelled. Please try again.")
        sys.exit(1)


if __name__ == "__main__":
    app()