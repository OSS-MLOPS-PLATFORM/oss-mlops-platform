import os

from functions.platforms.ssh import run_remote_commands
from functions.platforms.slurm import format_slurm_sacct, format_slurm_seff, format_slurm_squeue
from functions.utility.storage.objects import set_object
from functions.utility.storage.metadata import general_object_metadata

def set_artifact_path(
    object: str, 
    job_id: str
):
    artifact_folder = 'artifacts'
    os.makedirs(artifact_folder, exist_ok=True)
    file_paths = {
        'squeue': artifact_folder + '/squeue.txt',
        'sacct': artifact_folder + '/sacct_(id).txt',
        'seff': artifact_folder + '/seff_(id).txt'
    }
    object_path = file_paths[object]
    if not job_id is None:
        object_path = object_path.replace('(id)', job_id)
    return object_path

def get_squeue(
    platform_secrets: any
) -> any:
    template_command = 'squeue --me'
    resulted_prints = run_remote_commands(
        platform_secrets = platform_secrets,
        commands = [
            template_command
        ]
    )
    job_dict = None
    if 0 < len(resulted_prints):
        file_path = set_artifact_path(
            object = 'squeue',
            job_id = None
        )
        job_dict = format_slurm_squeue(
            file_path = file_path,
            resulted_print = resulted_prints[0]
        )
    return job_dict

def get_sacct(
    platform_secrets: any,
    job_id: str
) -> any:
    template_command = 'sacct -o '

    metadata_fields = [
        'JobID',
        'JobName',
        'Account',
        'Partition',
        'ReqCPUS',
        'AllocCPUs',
        'ReqNodes',
        'AllocNodes',
        'State'
    ]

    resource_fields = [
        'AveCPU',
        'AveCPUFreq',
        'AveDiskRead',
        'AveDiskWrite'
    ]

    time_fields = [
        'Timelimit',
        'Submit',
        'Start',
        'Elapsed',
        'Planned',
        'End',
        'PlannedCPU',
        'CPUTime',
        'TotalCPU'
    ]

    used_fields = metadata_fields + resource_fields + time_fields

    i = 0 
    for field in used_fields:
        if len(used_fields) == i + 1:
            template_command += field
            break
        template_command += field + ','
        i += 1 

    template_command += ' -j '
    modified_command = template_command + job_id
    
    resulted_prints = run_remote_commands(
        platform_secrets = platform_secrets,
        commands = [
            modified_command
        ]
    )
    sacct = None
    if 0 < len(resulted_prints):
        file_path = set_artifact_path(
            object = 'sacct',
            job_id = job_id
        )
        sacct = format_slurm_sacct(
            file_path = file_path,
            resulted_print = resulted_prints[0]
        )
    return sacct

def get_seff(
    platform_secrets: any,
    job_id: str
) -> any:
    template_command = 'seff '
    modified_command = template_command + job_id
    
    resulted_prints = run_remote_commands(
        platform_secrets = platform_secrets,
        commands = [
            modified_command
        ]
    )
    seff = None
    if 0 < len(resulted_prints):
        file_path = set_artifact_path(
            object = 'seff',
            job_id = job_id
        )
        seff = format_slurm_seff(
            file_path = file_path,
            resulted_print = resulted_prints[0]
        )
    return seff

def store_sacct(
    storage_client: any,
    storage_name: str,
    target_secrets: any,
    job_key: str,
    job_id: str
) -> bool:
    sacct_data = get_sacct( 
        platform_secrets = target_secrets,
        job_id = job_id
    )

    stored = False
    if not sacct_data is None:
        set_object(
            storage_client = storage_client,
            bucket_name = storage_name,
            object_name = 'job-sacct',
            path_replacers = {
                'name': job_key
            },
            path_names = [],
            overwrite = True,
            object_data = sacct_data,
            object_metadata = general_object_metadata()
        )
        stored = True
    return stored

def store_seff(
    storage_client: any,
    storage_name: str,
    target_secrets: any,
    job_key: str,
    job_id: str
) -> bool:
    seff_data = get_seff(
        platform_secrets = target_secrets,
        job_id = job_id
    )

    stored = False
    if not seff_data is None:
        set_object(
            storage_client = storage_client,
            bucket_name = storage_name,
            object_name = 'job-seff',
            path_replacers = {
                'name': job_key
            },
            path_names = [],
            overwrite = True,
            object_data = seff_data,
            object_metadata = general_object_metadata()
        )
        stored = True
    return stored
