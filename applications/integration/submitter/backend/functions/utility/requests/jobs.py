from functions.platforms.ssh import run_remote_commands
from functions.platforms.slurm import format_slurm_sbatch

def send_job(
    platform_secrets: any,
    folder_path: str,
    file_name: str
) -> str:
    template_command_1 = 'source /appl/profile/zz-csc-env.sh'
    template_command_2 = ' && cd ' + folder_path  
    template_command_3 = ' && sbatch ' + file_name
    modified_command = template_command_1 + template_command_2 + template_command_3
    
    resulted_prints = run_remote_commands( 
        platform_secrets = platform_secrets,
        commands = [
            modified_command
        ]
    )
    
    job_id = None
    if 0 < len(resulted_prints):
        job_id = format_slurm_sbatch(
            resulted_print = resulted_prints[0]
        )
    return job_id

def halt_job(
    platform_secrets: any,
    job_id: str
) -> bool:
    template_command = 'scancel '
    modified_command = template_command + job_id
    
    resulted_prints = run_remote_commands(
        platform_secrets = platform_secrets,
        commands = [
            modified_command
        ]
    )
    
    cancelled = False
    if 0 == len(resulted_prints[0]):
        cancelled = True
    return cancelled