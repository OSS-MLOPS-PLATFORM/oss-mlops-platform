from functions.utility.general import set_formatted_user, update_nested_dict
from functions.utility.storage.objects import check_bucket, get_object, set_object

def get_submitter_bucket_name(
    configuration: any,
    job_request: any
) -> str:
    object_store_config = configuration['enviroment-parameters']['storage']['object-store']
    bucket_prefix = object_store_config['bucket-prefix']
    ice_id = configuration['ice-id']
    user = set_formatted_user(user = job_request['user'])
    submitter_name = 'submitter-' + ice_id + '-' + user
    bucket_name = bucket_prefix + '-' + submitter_name
    return bucket_name

def get_new_status_key(
    path_prefix: str,
    bucket_objects: any
) -> str:
    largest_key = 0
    for object_path in bucket_objects.keys():
        target_path_split = path_prefix.split('/')
        comparison_path_split = object_path.split('/')
        found = True
        for i in range(0, len(target_path_split)):
            if not target_path_split[i] == comparison_path_split[i]:
                found = False
        if found: 
            if len(target_path_split) + 1 == len(comparison_path_split):
                used_key = comparison_path_split[-1]
                if used_key.isnumeric():
                    used_key = int(used_key)
                    if largest_key < used_key:
                        largest_key = used_key
    new_key = largest_key + 1
    new_key = str(new_key)
    return new_key

def create_job(
    configuration: any,
    job_request: any
) -> any:
    # Only concurrency issue 
    # is with keys
    
    storage_clients = configuration['storage-clients']
    
    submitter_bucket_name = get_submitter_bucket_name(
        configuration = configuration,
        job_request = job_request
    )

    # Concurrency source
    submitter_bucket_info = check_bucket(
        storage_client = storage_clients[0],
        bucket_name = submitter_bucket_name
    )

    submitter_bucket_objects = submitter_bucket_info['objects']

    created_job_data = {}
    created_job_metadata = {}
    if 0 < len(submitter_bucket_objects):
        if 'JOBS/status-template' in submitter_bucket_objects:
            job_status_object = get_object(
                storage_client = storage_clients[0],
                bucket_name = submitter_bucket_name,
                object_name = 'jobs',
                path_replacers = {
                    'name': 'status-template'
                },
                path_names = []
            )
        
            created_job_data = update_nested_dict(
                target = job_status_object['data'],
                update = job_request
            )
            created_job_data['start'] = True
            created_job_metadata = job_status_object['custom-meta']
            
    if 0 < len(created_job_data):
        job_path_prefix = 'JOBS'
        # Concurrency source
        job_key = get_new_status_key(
            path_prefix = job_path_prefix,
            bucket_objects = submitter_bucket_objects
        )
        set_object(
            storage_client = storage_clients[0],
            bucket_name = submitter_bucket_name,
            object_name = 'jobs',
            path_replacers = {
                'name': job_key
            },
            path_names = [],
            overwrite = False,
            object_data = created_job_data,
            object_metadata = created_job_metadata
        )
    
        return {'message': 'created'}
    return {'message': 'not created'}

def stop_job(
    configuration: any,
    job_cancel: any
):
    # Might need sanitazation

    # Can cause concurrency 
    # issues for submitter
    storage_clients = configuration['storage-clients']
    
    submitter_bucket_name = get_submitter_bucket_name(
        configuration = configuration,
        job_request = job_cancel
    )
    # Concurrency source
    job_status_object = get_object(
        storage_client = storage_clients[0],
        bucket_name = submitter_bucket_name,
        object_name = 'jobs',
        path_replacers = {
            'name': job_cancel['key']
        },
        path_names = []
    )

    if len(job_status_object) == 0:
        return {'message': 'fail'}

    job_status_data = job_status_object['data']
    job_status_metadata = job_status_object['custom-meta']

    job_status_data['cancel'] = True
    job_status_metadata['version'] = job_status_metadata['version'] + 1
    # Concurrency source
    set_object(
        storage_client = storage_clients[0],
        bucket_name = submitter_bucket_name,
        object_name = 'jobs',
        path_replacers = {
            'name': job_cancel['key']
        },
        path_names = [],
        overwrite = True,
        object_data = job_status_data,
        object_metadata = job_status_metadata
    )
    
    return {'message': 'success'}

def create_forwarding(
    configuration: any,
    forwarding_request: any
) -> any:
    # Only concurrency issue 
    # is with keys

    # There are import and 
    # export connections.
    # Import connections 
    # are outside the 
    # cluster forwarder 
    # into the cluster.
    # Export connections 
    # are inside the 
    # cluster forwarder 
    # outside the cluster
    storage_clients = configuration['storage-clients']
    storage_names = configuration['storage-names']

    forwarder_bucket_name = storage_names[0]
    # Concurrency source
    forwarder_bucket_info = check_bucket(
        storage_client = storage_clients[0],
        bucket_name = forwarder_bucket_name
    )

    forwarder_bucket_objects = forwarder_bucket_info['objects']
    
    created_import_data = {}
    created_import_metadata = {}

    created_export_data = {}
    created_export_metadata = {}
    if 0 < len(forwarder_bucket_objects):
        if 'FORWARDS/status-template' in forwarder_bucket_objects:
            forwarding_status_object = get_object(
                storage_client = storage_clients[0],
                bucket_name = forwarder_bucket_name,
                object_name = 'forwards',
                path_replacers = {
                    'name': 'status-template'
                },
                path_names = []
            )

            if 0 < len(forwarding_request['imports']):
                created_import_data = forwarding_status_object['data']
                created_import_data['connections'] = forwarding_request['imports']
                created_import_metadata = forwarding_status_object['custom-meta']

            if 0 < len(forwarding_request['exports']):
                created_export_data = forwarding_status_object['data']
                created_export_data['connections'] = forwarding_request['exports']
                created_export_metadata = forwarding_status_object['custom-meta']

    submitter_bucket_name = get_submitter_bucket_name(
        configuration = configuration,
        job_request = forwarding_request
    )
    
    created = False
    if 0 < len(created_import_data):
        import_path_prefix = 'FORWARDS/IMPORTS' + submitter_bucket_name
        # Concurrency source
        import_key = get_new_status_key(
            path_prefix = import_path_prefix,
            bucket_objects = forwarder_bucket_objects
        )
        
        set_object(
            storage_client = storage_clients[0],
            bucket_name = forwarder_bucket_name,
            object_name = 'imports',
            path_replacers = {
                'name': submitter_bucket_name,
            },
            path_names = [
                import_key
            ],
            overwrite = False,
            object_data = created_import_data,
            object_metadata = created_import_metadata
        )
        created = True

    if 0 < len(created_export_data):
        export_path_prefix = 'FORWARDS/EXPORTS' + submitter_bucket_name
        export_key = get_new_status_key(
            path_prefix = export_path_prefix,
            bucket_objects = forwarder_bucket_objects
        )

        set_object(
            storage_client = storage_clients[0],
            bucket_name = forwarder_bucket_name,
            object_name = 'exports',
            path_replacers = {
                'name': submitter_bucket_name,
            },
            path_names = [
                export_key
            ],
            overwrite = False,
            object_data = created_export_data,
            object_metadata = created_export_metadata
        )
        created = True

    if created:
        return {'message': 'created'}
    return {'message': 'not created'}

def stop_forwarding(
    configuration: any,
    forwarding_cancel: any
) -> any:
    # Can cause concurrency 
    # issues with celery workers
     
    # Might need sanitazation

    storage_clients = configuration['storage-clients']
    storage_names = configuration['storage-names']

    forwarder_bucket_name = storage_names[0]

    submitter_bucket_name = get_submitter_bucket_name(
        configuration = configuration,
        job_request = forwarding_cancel
    )
    # Concurrency source
    forwarding_status_object = get_object(
        storage_client = storage_clients[0],
        bucket_name = forwarder_bucket_name,
        object_name = forwarding_cancel['forwarding-type'],
        path_replacers = {
            'name': submitter_bucket_name
        },
        path_names = [
            forwarding_cancel['key']
        ]
    )

    if len(forwarding_status_object) == 0:
        return {'message': 'fail'}

    forwarding_status_data = forwarding_status_object['data']
    forwarding_status_metadata = forwarding_status_object['custom-meta']
    
    forwarding_status_data['cancel'] = True
    forwarding_status_metadata['version'] = forwarding_status_metadata['version'] + 1
    
    # Concurrency source
    set_object(
        storage_client = storage_clients[0],
        bucket_name = forwarder_bucket_name,
        object_name = forwarding_cancel['forwarding-type'],
        path_replacers = {
            'name': submitter_bucket_name
        },
        path_names = [
            forwarding_cancel['key']
        ],
        overwrite = True,
        object_data = forwarding_status_data,
        object_metadata = forwarding_status_metadata
    )
    
    return {'message': 'success'}
