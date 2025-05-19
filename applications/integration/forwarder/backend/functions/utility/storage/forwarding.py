
from functions.utility.storage.objects import set_object_path, check_bucket, get_object, set_object
from functions.utility.storage.management import get_user_bucket_name, get_new_status_key

def store_created_forwarding(
    storage_client: any,
    storage_name: str,
    forwarding_request: any,
    bucket_parameters: any
) -> any:
    forwarder_bucket_info = check_bucket(
        storage_client = storage_client,
        bucket_name = storage_name
    )

    forwarder_bucket_objects = forwarder_bucket_info['objects']
     
    created_import_data = {}
    created_import_metadata = {}

    created_export_data = {}
    created_export_metadata = {}
    if 0 < len(forwarder_bucket_objects): 
        # Maybe refactor later
        if 'FORWARDS/status-template' in forwarder_bucket_objects:
            forwarding_status_object = get_object(
                storage_client = storage_client,
                bucket_name = storage_name,
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

    submitter_bucket_name = get_user_bucket_name(
        target = 'submitter',
        bucket_parameters = bucket_parameters
    )
    
    forwarding_keys = '0,0'
    if 0 < len(created_import_data):
        import_path_prefix = set_object_path(
            object_name = 'imports',
            path_replacers = {
                'name': submitter_bucket_name
            },
            path_names = []
        )
        # Concurrency source
        import_key = get_new_status_key(
            path_prefix = import_path_prefix,
            bucket_objects = forwarder_bucket_objects
        )

        set_object(
            storage_client = storage_client,
            bucket_name = storage_name,
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

        forwarding_keys_split = forwarding_keys.split(',')
        forwarding_keys_split[0] = import_key
        forwarding_keys = ','.join(forwarding_keys_split)

    if 0 < len(created_export_data):
        export_path_prefix = set_object_path(
            object_name = 'exports', 
            path_replacers = {
                'name': submitter_bucket_name
            },
            path_names = []
        )
        
        export_key = get_new_status_key(
            path_prefix = export_path_prefix,
            bucket_objects = forwarder_bucket_objects
        )

        set_object(
            storage_client = storage_client,
            bucket_name = storage_name,
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

        forwarding_keys_split = forwarding_keys.split(',')
        forwarding_keys_split[1] = export_key 
        forwarding_keys = ','.join(forwarding_keys_split)
    return {'keys': forwarding_keys}

def store_stopped_forwarding(
    storage_client: any,
    storage_name: str,
    forwarding_cancel: any,
    bucket_parameters: any
):
    submitter_bucket_name = get_user_bucket_name(
        target = 'submitter',
        bucket_parameters = bucket_parameters
    )
    # Concurrency source
    forwarding_status_object = get_object(
        storage_client = storage_client,
        bucket_name = storage_name,
        object_name = forwarding_cancel['forwarding-type'],
        path_replacers = {
            'name': submitter_bucket_name
        },
        path_names = [
            forwarding_cancel['key']
        ]
    )

    if len(forwarding_status_object) == 0:
        return {'status': 'fail'}

    forwarding_status_data = forwarding_status_object['data']
    forwarding_status_metadata = forwarding_status_object['custom-meta']

    if forwarding_status_data['cancel']:
        return {'status': 'checked'}
    
    forwarding_status_data['cancel'] = True
    forwarding_status_metadata['version'] = forwarding_status_metadata['version'] + 1
    
    # Concurrency source
    set_object(
        storage_client = storage_client,
        bucket_name = storage_name,
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
    
    return {'status': 'success'}