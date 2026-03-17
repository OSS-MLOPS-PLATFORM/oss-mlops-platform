from functions.utility.storage.management import setup_storage_clients,check_object_metadata, create_or_update_object, get_object_content, get_bucket_info, get_container_info

def set_object_path(
    object_name: str,
    path_replacers: any,
    path_names: any
):
    object_paths = {
        'root': 'name',
        'jobs': 'JOBS/name',
        'enviroments': 'ENVIROMENTS/name',
        'hpc': 'ENVIROMENTS/HPC/name',
        'artifacts': 'ARTIFACTS/name',
        'job-sacct': 'ARTIFACTS/SACCT/name',
        'job-seff': 'ARTIFACTS/SEFF/name',
        'job-logs': 'ARTIFACTS/LOGS/name',
        'job-time': 'ARTIFACTS/TIMES/name',
        'tasks': 'ARTIFACTS/TASKS/name'
    }

    i = 0
    path_split = object_paths[object_name].split('/')
    for name in path_split:
        if name in path_replacers:
            replacer = path_replacers[name]
            if 0 < len(replacer):
                path_split[i] = replacer
        i = i + 1
    
    if not len(path_names) == 0:
        path_split.extend(path_names)

    object_path = '/'.join(path_split)
    print('Used object path: ' + str(object_path))
    return object_path

def get_clients(
    configuration: any
) -> any:
    return setup_storage_clients(
        configuration = configuration
    ) 

def check_object(
    storage_client: any,
    bucket_name: str,
    object_name: str,
    path_replacers: any,
    path_names: any
) -> bool:
    object_path = set_object_path(
        object_name = object_name,
        path_replacers = path_replacers,
        path_names = path_names
    )
    # Consider making these 
    # functions object storage agnostic
    object_metadata = check_object_metadata(
        storage_client = storage_client,
        bucket_name = bucket_name,
        object_path = object_path
    )
    object_metadata['path'] = object_path
    return object_metadata

def get_object(
    storage_client: any,
    bucket_name: str,
    object_name: str,
    path_replacers: any,
    path_names: any
) -> any:
    checked_object = check_object(
        storage_client = storage_client,
        bucket_name = bucket_name,
        object_name = object_name,
        path_replacers = path_replacers,
        path_names = path_names
    )

    object_data = None
    if not len(checked_object['general-meta']) == 0:
        # Consider making these 
        # functions object storage agnostic
        object_data = get_object_content(
            storage_client = storage_client,
            bucket_name = bucket_name,
            object_path = checked_object['path']
        )

    return object_data

def set_object(
    storage_client: any,
    bucket_name: str,
    object_name: str,
    path_replacers: any,
    path_names: any,
    overwrite: bool,
    object_data: any,
    object_metadata: any
):
    checked_object = check_object(
        storage_client = storage_client,
        bucket_name = bucket_name,
        object_name = object_name,
        path_replacers = path_replacers,
        path_names = path_names
    )
    # These might need a 
    # way to handle the case
    # that token has gotten old
    perform = True
    if not len(checked_object['general-meta']) == 0 and not overwrite:
        perform = False
    
    if perform:
        # Consider making these 
        # functions object storage agnostic
        create_or_update_object(
            storage_client = storage_client,
            bucket_name = bucket_name,
            object_path = checked_object['path'],
            object_data = object_data,
            object_metadata = object_metadata
        )

def check_bucket(
    storage_client: any,
    bucket_name: str
) -> any:
    return get_bucket_info(
        storage_client = storage_client,
        bucket_name = bucket_name
    )

def check_buckets(
    storage_client: any
) -> any:
    return get_container_info( 
        storage_client = storage_client
    )