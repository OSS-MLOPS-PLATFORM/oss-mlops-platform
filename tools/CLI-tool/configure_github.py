import typer
import subprocess
import sys


app = typer.Typer()


@app.command()
def main():

    print("Checking GitHub CLI installation...")
    check_gh_installed()

    print("Checking GitHub authentication...")
    check_gh_auth()


def check_gh_installed():
    """Check if GitHub CLI is installed."""
    try:
        result = subprocess.run(["gh", "--version"], capture_output=True, text=True)
        if result.returncode != 0:
            typer.echo("GitHub CLI (gh) is not installed.")
            typer.echo("Do you want to install GitHub CLI? (y/n)")
            choice = input().strip().lower()
            if choice == 'y':
                if sys.platform == "darwin":
                    subprocess.run(["brew", "install", "gh"], check=True)
                elif sys.platform == "linux":
                    subprocess.run(["sudo", "apt", "install", "gh"], check=True)
                else:
                    typer.echo("Unsupported OS. Please install GitHub CLI manually.")
                    sys.exit(1)
            else:
                typer.echo("GitHub CLI (gh) is required. Exiting...")
                sys.exit(1)
    except FileNotFoundError:
        typer.echo("GitHub CLI (gh) is not installed.")
        sys.exit(1)


def check_gh_auth():
    """Check if user is authenticated with GitHub."""
    result = subprocess.run("gh auth status", shell=True, capture_output=True, text=True)

    if "Logged in to github.com" not in result.stdout:
        subprocess.run("gh auth login", shell=True)

if __name__ == "__main__":
    app()