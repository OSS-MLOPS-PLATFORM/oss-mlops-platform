def push_repo():
    main_branch = subprocess.run(["git", "branch", "--show-current"], capture_output=True, text=True, check=True)
    main_branch = main_branch.stdout.strip()
    print("Current branch:", main_branch)
    subprocess.run(f'echo Readme > README.md', shell=True)
    subprocess.run(["git", 'add', '.'], check=True)
    subprocess.run(["git", 'commit', '-m', '"Initial commit"'], check=True)
    subprocess.run(["git", 'push', 'origin', main_branch], check=True)


def create_branches():
    results = subprocess.run("git branch -a", shell=True, capture_output=True, text=True)
    existing_branches = results.stdout.splitlines()

    branches_to_create = ["development", "staging", "production"]
    for branch in branches_to_create:
        if branch not in existing_branches:
            subprocess.run(f'git checkout -b {branch}', shell=True)
            current_branch = subprocess.run(["git", "branch", "--show-current"], capture_output=True, text=True, check=True)

            print("Current branch:", current_branch.stdout)
            subprocess.run(f'git push --set-upstream origin {branch}', shell=True)
            print(f"Branch '{branch}' created successfully.")


def copy_files():
    try:
        result = subprocess.run("git checkout development", capture_output=True, shell=True)
        if "did not match any file(s) known to git" in result.stderr.decode():
            subprocess.run("git checkout -b development", shell=True)
        subprocess.run("cp -r ../oss-mlops-platform/tools/CLI-tool/files/development/.[!.]* ../oss-mlops-platform/tools/CLI-tool/files/development/* .", shell=True)
        subprocess.run("cp -r ../oss-mlops-platform/tools/CLI-tool/files/common/.[!.]* ../oss-mlops-platform/tools/CLI-tool/files/common/* .", shell=True)
        subprocess.run("git add .", shell=True)
        subprocess.run("git commit -m 'Add branch specific files'", shell=True)
        subprocess.run("git push --set-upstream origin development", shell=True)
    except FileNotFoundError:
        typer.echo("Failed to create branch 'development'. Exiting...")
        sys.exit(1)

    try:
        result = subprocess.run("git checkout production", capture_output=True, shell=True)
        if "did not match any file(s) known to git" in result.stderr.decode():
            subprocess.run("git checkout  main", shell=True)
            subprocess.run("git checkout -b production", shell=True)

        subprocess.run("cp -r ../oss-mlops-platform/tools/CLI-tool/files/production/.[!.]* ../oss-mlops-platform/tools/CLI-tool/files/production/* .", shell=True)
        subprocess.run("cp -r ../oss-mlops-platform/tools/CLI-tool/files/common/.[!.]* ../oss-mlops-platform/tools/CLI-tool/files/common/* .", shell=True)
        subprocess.run("git add .", shell=True)
        subprocess.run("git commit -m 'Add production files'", shell=True)
        subprocess.run("git push --set-upstream origin production", shell=True)

    except FileNotFoundError:
        typer.echo("Failed to create branch 'production'. Exiting...")
        sys.exit(1)

    try:
        result = subprocess.run("git checkout staging", capture_output=True, shell=True)
        if "did not match any file(s) known to git" in result.stderr.decode():
            subprocess.run("git checkout  main", shell=True)
            subprocess.run("git checkout -b staging", shell=True)

        subprocess.run("cp -r ../oss-mlops-platform/tools/CLI-tool/files/staging/.[!.]* ../oss-mlops-platform/tools/CLI-tool/files/staging/* .", shell=True)
        subprocess.run("cp -r ../oss-mlops-platform/tools/CLI-tool/files/common/.[!.]* ../oss-mlops-platform/tools/CLI-tool/files/common/* .", shell=True)
        subprocess.run("git add .", shell=True)
        subprocess.run("git commit -m 'Add staging files'", shell=True)
        subprocess.run("git push --set-upstream origin staging", shell=True)

    except FileNotFoundError:
        typer.echo("Failed to create branch 'staging'. Exiting...")
        sys.exit(1)

def delete_extra_branch():
    output = subprocess.run("git remote show origin", text=True,shell=True, capture_output=True)
    existing_branches = output.stdout.splitlines()
    branch_to_be_delete = ""
    for branch in existing_branches:
        if "HEAD" in branch:
            branch_to_be_delete = branch.split()[2]
    if branch_to_be_delete:
        subprocess.run(["git", "push", "origin", "--delete", branch_to_be_delete], capture_output=True, text=True,shell=True)
        