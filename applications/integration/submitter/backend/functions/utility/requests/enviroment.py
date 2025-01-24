from functions.platforms.ssh import run_remote_commands
from functions.platforms.venv import format_python_version, format_venv_packages
from functions.platforms.linux import format_pwd_directory, format_folders_and_files
from functions.platforms.csc import format_supercomputer_workspace

def get_directory(
    platform_secrets: any  
) -> str:
    resulted_prints = run_remote_commands(
        platform_secrets = platform_secrets,
        commands = [
            'pwd',
        ]
    )
    directory = None
    if 0 < len(resulted_prints):
        directory = format_pwd_directory(
            resulted_print = resulted_prints[0]
        )
    return directory

def get_python_version(
    platform_secrets: any 
) -> str:
    resulted_prints = run_remote_commands(
        platform_secrets = platform_secrets,
        commands = [
            'python3 -V'
        ]
    )
    python_version = None
    if 0 < len(resulted_prints):
        python_version = format_python_version(
            resulted_print = resulted_prints[0]
        )  
    return python_version

def get_workspace(
    platform_secrets: any   
) -> any:
    resulted_prints = run_remote_commands(
        platform_secrets = platform_secrets,
        commands = [
            'source /appl/profile/zz-csc-env.sh && csc-workspaces'
        ]
    )
    workspace = None
    if 0 < len(resulted_prints):
        workspace = format_supercomputer_workspace(
            resulted_print = resulted_prints[0]
        )
    return workspace

def get_folders_and_files(
    platform_secrets: any
) -> any:
    # Change later to 
    # handle projappl 
    # and scratch
    resulted_prints = run_remote_commands(
        platform_secrets = platform_secrets,
        commands = [
            'ls'
        ]
    )
    folders = None
    files = None
    
    if 0 < len(resulted_prints):
        folders, files = format_folders_and_files(
            resulted_print = resulted_prints[0]
        )
    return [folders, files]

def get_venv_packages(
    platform_secrets: any,
    module_name: str,
    venv_name: str
) -> any:
    template_command = 'source /appl/profile/zz-csc-env.sh && module load (module) && source (venv)/bin/activate && pip list && deactivate'
    modified_command = template_command.replace('(module)', module_name)
    modified_command = modified_command.replace('(venv)', venv_name)
    
    resulted_prints = run_remote_commands(
        platform_secrets = platform_secrets,
        commands = [
            modified_command
        ]
    )
    
    packages = None
    if 0 < len(resulted_prints):
        packages = format_venv_packages(
            resulted_print = resulted_prints[0]
        )

    return packages

def get_venvs(
    platform_secrets: any,
    current_folders: any
) -> any:
    directory_venvs = {}
    for folder in current_folders:
        if 'venv' in folder:
            # Refactor later to 
            # handle multiple modules
            venv_packages = get_venv_packages(
                platform_secrets = platform_secrets,
                module_name = 'pytorch',
                venv_name = folder
            )
            directory_venvs[folder] = {
                'configuration-modules': [
                    'pytorch'
                ],
                'packages': venv_packages
            }
    return directory_venvs