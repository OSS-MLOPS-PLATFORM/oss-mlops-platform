import time

from functions.platforms.ssh import run_remote_commands
from functions.platforms.venv import format_package_installation, check_venv_creation, check_venv_package_installation

def add_modules(
    template_command: str,
    modules: any
) -> str:
    modified_command = template_command
    if 0 < len(modules):
        index = 0
        for module in modules:
            if index < len(modules):
                modified_command += ' && '
            modified_command += 'module load ' + module
            index += 1
    return modified_command

def create_new_venv(
    platform_secrets: any,
    modules: str,
    venv_name: str
) -> bool:
    # Refactor later to 
    # handle missing modules
    # We assume that it has 
    # been checked that there 
    # is no venv with the 
    # same name
    template_command_1 = 'source /appl/profile/zz-csc-env.sh'
    modified_command_1 = add_modules(
        template_command = template_command_1,
        modules = modules
    )
    
    template_command_2 = ' && python3 -m venv --system-site-packages (venv)'
    template_command_3 = ' && source (venv)/bin/activate && pip install --upgrade pip && deactivate'
    modified_command_2 = template_command_2.replace('(venv)', venv_name)
    modified_command_3 = template_command_3.replace('(venv)', venv_name)
    modified_command = modified_command_1 + modified_command_2 + modified_command_3
    
    resulted_prints = run_remote_commands(
        platform_secrets = platform_secrets,
        commands = [
            modified_command
        ]
    )
    
    venv_created = True
    if 0 < len(resulted_prints):
        venv_created = check_venv_creation(
            resulted_prints = resulted_prints
        )
    return venv_created

def install_venv_packages(
    platform_secrets: any,
    modules: str,
    venv_name: str,
    wanted_packages: any
) -> bool:
    template_command_1 = 'source /appl/profile/zz-csc-env.sh'
    modified_command_1 = add_modules(
        template_command = template_command_1,
        modules = modules
    )
    template_command_2 = ' && source (venv)/bin/activate && pip install '
    modified_command_2 = template_command_2.replace('(venv)', venv_name)
    modified_command = modified_command_1 + modified_command_2
    
    formatted_commands = format_package_installation(
        wanted_packages = wanted_packages
    )

    success = True
    index = 0
    for formatted_command in formatted_commands:
        install_command = modified_command + formatted_command + '&& deactivate'
        resulted_prints = run_remote_commands(
            platform_secrets = platform_secrets,
            commands = [
                install_command
            ]
        )
        
        if 0 < len(resulted_prints):
            success = check_venv_package_installation(
                resulted_prints = resulted_prints
            )
            index += 1

        if index < len(formatted_commands):
            time.sleep(2)
    return success