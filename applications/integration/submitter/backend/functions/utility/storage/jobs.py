import time

from functions.utility.general import update_nested_dict
from functions.utility.storage.objects import check_bucket, get_object, set_object
from functions.utility.storage.time import store_job_time
from functions.utility.storage.management import get_new_status_key
 
def store_created_job( 
    storage_client: any,
    storage_name: str,
    job_request: any
):
    # Concurrency source
    submitter_bucket_info = check_bucket(
        storage_client = storage_client,
        bucket_name = storage_name
    )

    submitter_bucket_objects = submitter_bucket_info['objects']

    created_job_data = {}
    created_job_metadata = {}
    if 0 < len(submitter_bucket_objects): 
        if 'JOBS/status-template' in submitter_bucket_objects:
            job_status_object = get_object(
                storage_client = storage_client,
                bucket_name = storage_name,
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
            
            created_job_metadata = job_status_object['custom-meta']
            
    if 0 < len(created_job_data):
        job_path_prefix = 'JOBS'
        # Concurrency source
        job_key = get_new_status_key(
            path_prefix = job_path_prefix,
            bucket_objects = submitter_bucket_objects
        )
        set_object(
            storage_client = storage_client,
            bucket_name = storage_name,
            object_name = 'jobs',
            path_replacers = {
                'name': job_key
            },
            path_names = [],
            overwrite = False,
            object_data = created_job_data,
            object_metadata = created_job_metadata
        )
    
        return {'key': job_key}
    return {'key': '0'}

def store_started_job(
    storage_client: any,
    storage_name: str,
    job_start: any
):
    begin_job_starting_time = time.time()

    job_status_object = get_object(
        storage_client = storage_client,
        bucket_name = storage_name,
        object_name = 'jobs',
        path_replacers = {
            'name': job_start['key']
        },
        path_names = []
    )

    if len(job_status_object) == 0:
        return {'status': 'fail'}

    job_status_data = job_status_object['data']
    job_status_metadata = job_status_object['custom-meta']

    if job_status_data['start']:
        return {'status': 'checked'}

    job_status_data['start'] = True
    job_status_metadata['version'] = job_status_metadata['version'] + 1
    # Concurrency source
    set_object(
        storage_client = storage_client,
        bucket_name = storage_name,
        object_name = 'jobs',
        path_replacers = {
            'name': job_start['key']
        },
        path_names = [],
        overwrite = True,
        object_data = job_status_data,
        object_metadata = job_status_metadata
    )
      
    store_job_time(
        storage_client = storage_client,
        storage_name = storage_name,
        job_key = job_start['key'],
        time_input = {
            'begin-start': begin_job_starting_time
        }
    )
    return {'status': 'success'}

def store_stopped_job(
    storage_client: any,
    storage_name: str,
    job_cancel: any
):
    begin_job_cancelling_time = time.time()

    # Concurrency source
    job_status_object = get_object(
        storage_client = storage_client,
        bucket_name = storage_name,
        object_name = 'jobs',
        path_replacers = {
            'name': job_cancel['key']
        },
        path_names = []
    )

    if len(job_status_object) == 0:
        return {'status': 'fail'}

    job_status_data = job_status_object['data']
    job_status_metadata = job_status_object['custom-meta']

    if job_status_data['stopped']:
        return {'status': 'stopped'}

    if job_status_data['cancel']:
        return {'status': 'checked'}

    job_status_data['cancel'] = True
    job_status_metadata['version'] = job_status_metadata['version'] + 1
    # Concurrency source
    set_object(
        storage_client = storage_client,
        bucket_name = storage_name,
        object_name = 'jobs',
        path_replacers = {
            'name': job_cancel['key']
        },
        path_names = [],
        overwrite = True,
        object_data = job_status_data,
        object_metadata = job_status_metadata
    )

    store_job_time(
        storage_client = storage_client,
        storage_name = storage_name,
        job_key = job_cancel['key'],
        time_input = {
            'begin-cancel': begin_job_cancelling_time
        }
    )
    
    return {'status': 'success'}