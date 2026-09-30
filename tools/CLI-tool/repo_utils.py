import subprocess
import os
import sys
import glob
import yaml
import typer


def create_branches(branches_to_create=None):
    """Create branches if they don't already exist."""
    if branches_to_create is None:
        branches_to_create = ["development", "staging", "production"]

    results = subprocess.run("git branch -a", shell=True, capture_output=True, text=True)
    existing_branches = results.stdout.splitlines()

    for branch in branches_to_create:
        if branch not in existing_branches:
            subprocess.run(f'git checkout -b {branch}', shell=True)
            current_branch = subprocess.run(["git", "branch", "--show-current"], capture_output=True, text=True, check=True)
            print("Current branch:", current_branch.stdout.strip())
            subprocess.run(f'git push --set-upstream origin {branch}', shell=True)
            print(f"Branch '{branch}' created successfully.")


def copy_files(branch_files_mapping, common_files_path):
    """Copy branch-specific files."""
    for branch, branch_path in branch_files_mapping.items():
        try:
            result = subprocess.run(f"git checkout {branch}", capture_output=True, shell=True)
            if "did not match any file(s) known to git" in result.stderr.decode():
                subprocess.run(f"git checkout -b {branch}", shell=True)

            subprocess.run(f"cp -r {branch_path}/.[!.]* {branch_path}/* .", shell=True)
            subprocess.run(f"cp -r {common_files_path}/.[!.]* {common_files_path}/* .", shell=True)
            subprocess.run("git add .", shell=True)
            subprocess.run(f"git commit -m 'Add {branch} files'", shell=True)
            subprocess.run(f"git push --set-upstream origin {branch}", shell=True)
        except FileNotFoundError:
            typer.echo(f"Failed to create branch '{branch}'. Exiting...")
            sys.exit(1)


def delete_extra_branch():
    """Delete the default branch if it is not needed."""
    output = subprocess.run("git remote show origin", text=True, shell=True, capture_output=True)
    existing_branches = output.stdout.splitlines()
    branch_to_be_deleted = ""
    for branch in existing_branches:
        if "HEAD" in branch:
            branch_to_be_deleted = branch.split()[2]
    if branch_to_be_deleted:
        subprocess.run(["git", "push", "origin", "--delete", branch_to_be_deleted], capture_output=True, text=True, shell=True)

