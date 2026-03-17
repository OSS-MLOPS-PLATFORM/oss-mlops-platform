
from functions.utility.storage.objects import get_object, set_object, check_bucket, set_object_path
from functions.utility.general import update_nested_dict

def store_job_time(
    storage_client: any,
    storage_name: str,
    job_key: str,
    time_input: any
):
    print('store job time for key: ' + str(job_key))
    submitter_bucket_info = check_bucket(
        storage_client = storage_client,
        bucket_name = storage_name
    ) 

    submitter_bucket_objects = submitter_bucket_info['objects']
    
    time_object_path = set_object_path(
        object_name = 'job-time',
        path_replacers = {
            'name': job_key
        },
        path_names = []
    )
    
    if 0 < len(submitter_bucket_objects):
        created_time_data = {}
        created_time_metadata = {}
        if not time_object_path in submitter_bucket_objects:
            job_time_object = get_object(
                storage_client = storage_client,
                bucket_name = storage_name,
                object_name = 'job-time',
                path_replacers = {
                    'name': 'time-template'
                },
                path_names = []
            )
            created_time_data = update_nested_dict(
                target = job_time_object['data'],
                update = time_input
            )
            
            created_time_metadata = job_time_object['custom-meta']
        else:
            job_time_object = get_object(
                storage_client = storage_client,
                bucket_name = storage_name,
                object_name = 'job-time',
                path_replacers = {
                    'name': job_key
                },
                path_names = []
            )
            created_time_data = update_nested_dict(
                target = job_time_object['data'],
                update = time_input
            )

            begin_value = 0
            end_value = 0
            for key, value in created_time_data.items():
                if 'begin' in key:
                    begin_value = value
                    continue
                if 'end' in key:
                    end_value = value
                    continue
                if 'total' in key and value == 0:
                    if 0 < begin_value and 0 < end_value:
                        total_value = end_value-begin_value
                        created_time_data[key] = total_value
                    
            created_time_metadata = job_time_object['custom-meta']
            created_time_metadata['version'] = created_time_metadata['version'] + 1
        
        if 0 < len(created_time_data):
            set_object(
                storage_client = storage_client,
                bucket_name = storage_name,
                object_name = 'job-time',
                path_replacers = {
                    'name': job_key
                },
                path_names = [],
                overwrite = True,
                object_data = created_time_data,
                object_metadata = created_time_metadata
            )

def get_job_time(
    storage_client: any,
    storage_name: str,
    job_key: str
): 
    print('Getting job time for key: ' + str(job_key))
    submitter_bucket_info = check_bucket(
        storage_client = storage_client,
        bucket_name = storage_name
    ) 

    submitter_bucket_objects = submitter_bucket_info['objects']
    
    time_object_path = set_object_path(
        object_name = 'job-time',
        path_replacers = {
            'name': job_key
        },
        path_names = []
    )
    
    job_time = {}
    if 0 < len(submitter_bucket_objects):
        if time_object_path in submitter_bucket_objects:
            job_time_object = get_object(
                storage_client = storage_client,
                bucket_name = storage_name,
                object_name = 'job-time',
                path_replacers = {
                    'name': job_key
                },
                path_names = []
            )
            job_time = {
                'data': job_time_object['data'],
                'metadata': job_time_object['custom-meta']
            }
    return job_time