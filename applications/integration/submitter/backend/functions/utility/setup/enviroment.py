from functions.utility.requests.enviroment import get_directory, get_python_version, get_workspace, get_folders_and_files, get_venvs
from functions.utility.storage.files import get_secret_dict
from functions.utility.storage.objects import set_object, check_object, get_object
from functions.utility.storage.metadata import general_object_metadata

def get_enviroment_data( 
    secrets_path: str,
    enviroment: str,
    target: str,
    type: str
) -> any:
    available_secrets = get_secret_dict(
        secrets_path = secrets_path
    )
 
    enviroment_data = {}
    if enviroment in available_secrets:
        enviroment_secrets = available_secrets[enviroment]
        if target in enviroment_secrets:
            platform_secrets = enviroment_secrets[target]

            if type == 'propeties':  
                print('Get directory')
                default_directory = get_directory(
                    platform_secrets = platform_secrets
                )
                enviroment_data['default-directory'] = default_directory
                print('Get python version')
                python_version = get_python_version(
                    platform_secrets = platform_secrets
                )
                enviroment_data['python-version'] = python_version

            if type == 'status': 
                print('Get workspace')
                current_workspace = get_workspace(
                    platform_secrets = platform_secrets
                )

                # Maybe add later 
                # the ability to 
                # check application 
                # and scratch folders

                # Change later to 
                # handle projappl and scratch
                print('Get folders and files')
                current_folders_and_files = get_folders_and_files(
                    platform_secrets = platform_secrets
                )
                
                current_folders = current_folders_and_files[0]
                current_files = current_folders_and_files[1]
                print('Get venvs')
                current_venvs = get_venvs(
                    platform_secrets = platform_secrets,
                    current_folders = current_folders
                )

                user = list(current_workspace['users'].keys())[0]
                
                current_workspace['users'][user]['folders'] = current_folders
                current_workspace['users'][user]['files'] = current_files
                current_workspace['users'][user]['venvs'] = current_venvs

                enviroment_data['current-workspace'] = current_workspace
            
    return enviroment_data

def store_enviroment_data( 
    storage_client: any,
    storage_name: str,
    secrets_path: str,
    enviroment: str,
    target: str
):
    # Can cause 
    # concurrency issues
    enviroment_properties_name = target + '-properties' 
    enviroment_properties_object = check_object(
        storage_client = storage_client,
        bucket_name = storage_name,
        object_name = enviroment,
        path_replacers = {
            'name': enviroment_properties_name
        },
        path_names = []
    )
    
    if len(enviroment_properties_object['general-meta']) == 0:
        enviroment_properties = get_enviroment_data(
            secrets_path = secrets_path,
            enviroment = enviroment,
            target = target,
            type = 'propeties'
        )
        # Concurrency source
        set_object(
            storage_client = storage_client,
            bucket_name = storage_name,
            object_name = enviroment,
            path_replacers = {
                'name': enviroment_properties_name
            },
            path_names = [],
            overwrite = False,
            object_data = enviroment_properties,
            object_metadata = general_object_metadata()
        )

    enviroment_status = get_enviroment_data(
        secrets_path = secrets_path,
        enviroment = enviroment,
        target = target,
        type = 'status'
    )

    enviroment_status_name = target + '-status' 
    enviroment_status_objects = get_object(
        storage_client = storage_client,
        bucket_name = storage_name,
        object_name = enviroment,
        path_replacers = {
            'name': enviroment_status_name
        },
        path_names = []
    ) 

    enviroment_status_metadata = {}
    if enviroment_status_objects is None:
        enviroment_status_metadata = general_object_metadata()
    else:
        enviroment_status_metadata = enviroment_status_objects['custom-meta']
        enviroment_status_metadata['version'] = enviroment_status_metadata['version'] + 1
    # Concurrency source
    set_object(
        storage_client = storage_client,
        bucket_name = storage_name,
        object_name = enviroment,
        path_replacers = {
            'name': enviroment_status_name
        },
        path_names = [],
        overwrite = True,
        object_data = enviroment_status,
        object_metadata = enviroment_status_metadata
    )