import os

from functions.platforms.ssh import run_remote_commands, download_file, upload_file
from functions.platforms.slurm import format_slurm_logs
from functions.utility.storage.files import create_file, get_stored_file_path, get_file_data
from functions.utility.storage.metadata import general_object_metadata
from functions.platforms.ssh import upload_file, run_remote_commands
from functions.utility.storage.objects import get_object, set_object

def send_file(
    storage_client: any,
    storage_names: str,
    available_secrets: any,
    file_info: any
) -> bool:
    # We assume that sources are 
    # always platform/storage/path 
    # format with | specifying 
    # dict keys.Thus, 
    # submitter/secrets|integratio|cpouta-mahti|key 
    # uses the path and 
    # allas/pipeline/code/slurm/ray-cluster.sh
    # here the name is used as the name 
    # in the target

    file_source = file_info['source']
    file_target = file_info['target']

    source_split = file_source.split('/') 
    file_sent = False
    if source_split[0] == 'local':
        if source_split[1] == 'submitter':
            if 'secrets' in source_split[2]:
                dict_keys = source_split[2].split('|')[1:]
                relative_local_path = available_secrets[dict_keys[0]][dict_keys[1]][dict_keys[2]]
                absolute_local_path = os.path.expanduser(relative_local_path)
                target_split = file_target.split('/')
                absolute_remote_path = '/' + '/'.join(target_split[2:])
                platform_secrets = available_secrets[target_split[0]][target_split[1]]
                
                file_sent = upload_file(
                    platform_secrets = platform_secrets,
                    absolute_local_path = absolute_local_path,
                    absolute_remote_path = absolute_remote_path
                )
                # We assume that all 
                # credentials are in 
                # personal directory
                file_permission_command = 'chmod 600 ' + target_split[-1]
                # Consider creating checking later
                resulted_prints = run_remote_commands(
                    platform_secrets = platform_secrets,
                    commands = [
                        file_permission_command
                    ]
                )
   
    if source_split[0] == 'storage':
        if source_split[1] == 'allas':
            if source_split[2] == 'pipeline':
                pipeline_bucket = storage_names[1]
                complete_path = source_split[3:]
                
                file_object = get_object(
                    storage_client = storage_client,
                    bucket_name = pipeline_bucket,
                    object_name = 'root',
                    path_replacers = {
                        'name': complete_path[0]
                    },
                    path_names = complete_path[1:]
                )

                file_data = file_object['data']
                relative_local_path = create_file(
                    file_name = complete_path[-1],
                    file_data = file_data
                )
                
                absolute_local_path = os.path.abspath(relative_local_path)
                target_split = file_target.split('/')
                absolute_remote_path = '/' + '/'.join(target_split[2:])
                
                platform_secrets = available_secrets[target_split[0]][target_split[1]]
                
                file_sent = upload_file(
                    platform_secrets = platform_secrets,
                    absolute_local_path = absolute_local_path,
                    absolute_remote_path = absolute_remote_path
                )
    return file_sent

def store_file( 
    storage_client: any,
    storage_names: any,
    target_secrets: any,
    file_info: any
) -> bool:
    
    file_source = file_info['source']
    file_target = file_info['target']

    source_split = file_source.split('/') 
    target_split = file_target.split('/')
    
    remote_absolute_path = '/' + '/'.join(source_split[2:])
    local_relative_path = get_stored_file_path(
        file_name = source_split[-1]
    )
    local_absolute_path = os.path.abspath(local_relative_path)

    file_stored = False

    downloaded = download_file(
        platform_secrets = target_secrets,
        absolute_remote_path = remote_absolute_path,
        absolute_local_path = local_absolute_path
    )
    if downloaded:
        if target_split[0] == 'storage':
            if target_split[1] == 'allas':
                if target_split[2] == 'pipeline':
                    pipeline_bucket = storage_names[1]
                    # Might need sanitazation
                    object_path = target_split[3:]

                    file_data = None
                    if 'slurm-' in source_split[-1]:
                        file_data = format_slurm_logs( 
                            file_path = local_absolute_path
                        )
                    else:
                        file_data = get_file_data(
                            file_name = source_split[-1]
                        )

                    set_object(
                        storage_client = storage_client,
                        bucket_name = pipeline_bucket,
                        object_name = 'root',
                        path_replacers = {
                            'name': object_path[0]
                        },
                        path_names = object_path[1:],
                        overwrite = True,
                        object_data = file_data,
                        object_metadata = general_object_metadata()
                    )
                    file_stored = True
    return file_stored    