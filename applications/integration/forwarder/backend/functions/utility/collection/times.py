from functions.utility.storage.objects import set_object_path, check_buckets, check_bucket, get_object
from functions.platforms.flower import parse_flower_times
from functions.utility.collection.indexing import get_index, update_index

def gather_bucket_job_times(
    storage_client: any, 
    storage_name: str,
    target_bucket: str
):
    unseen_job_times = {}

    bucket_info = check_bucket(
        storage_client = storage_client,
        bucket_name = target_bucket
    )

    bucket_objects = bucket_info['objects']

    path_prefix = set_object_path(
        object_name = 'root',
        path_replacers = {
            'name': 'ARTIFACTS'
        },
        path_names = [
            'TIMES'
        ]
    )   

    index_data, index_metadata = get_index(
        storage_client = storage_client,
        storage_name = storage_name,
        object_name = 'times',
        path_replacers = {
            'name': 'JOBS'
        },
        path_names = [
            target_bucket
        ]
    )

    key_list = index_data['keys'] 
    old_list_length = len(key_list)
    for object_path in bucket_objects:
        if path_prefix in object_path:
            time_path_split = object_path.split('/')
            time_key = time_path_split[-1]
        
            if time_key == 'time-template':
                continue

            if time_key in key_list:
                continue

            time_object = get_object(
                storage_client = storage_client,
                bucket_name = target_bucket,
                object_name = 'job-time',
                path_replacers = {
                    'name': time_key
                },
                path_names = []
            )

            time_info = time_object['data'] 
            # Results on zeros, unless total-store-seconds is checked 
            if 0 == time_info['total-store-seconds']:
                continue

            print('Unseen job time with key: ' + str(time_key))
             
            unseen_job_times[time_key] = time_info
            key_list.append(time_key)
    
    update_index(
        storage_client = storage_client,
        storage_name = storage_name,
        object_name = 'times',
        path_replacers = {
            'name': 'JOBS'
        },
        path_names = [
            target_bucket
        ],
        index_data = index_data,
        index_metadata = index_metadata,
        old_length = old_list_length,
        key_list = key_list
    )

    return unseen_job_times      

def gather_bucket_pipeline_times(
    storage_client: any, 
    storage_name: str,
    target_bucket: str
):
    unseen_pipeline_times = {}

    bucket_info = check_bucket(
        storage_client = storage_client,
        bucket_name = target_bucket 
    )

    bucket_objects = bucket_info['objects']

    path_prefix = set_object_path(
        object_name = 'root',
        path_replacers = {
            'name': 'TIMES'
        },
        path_names = []
    ) 

    for object_path in bucket_objects:
        if path_prefix in object_path:
            artifact_path_split = object_path.split('/')
            time_group = artifact_path_split[-1]
            
            print('Checking the times of group ' + str(time_group))

            if not time_group in unseen_pipeline_times:
                unseen_pipeline_times[time_group] = {}
            
            index_data, index_metadata = get_index(
                storage_client = storage_client,
                storage_name = storage_name,
                object_name = 'times',
                path_replacers = {
                    'name': 'PIPELINES'
                },
                path_names = [
                    time_group
                ]
            )

            time_object = get_object(
                storage_client = storage_client,
                bucket_name = target_bucket,
                object_name = 'pipeline-times',
                path_replacers = {
                    'name': time_group
                },
                path_names = []
            )

            time_data = time_object['data']
            key_list = index_data['keys'] 
            old_list_length = len(key_list) 

            for time_key, time_info in time_data.items():
                if time_key in key_list or 0 == time_info['total-seconds']:
                    continue
                
                print('Unseen pipeline time with key: ' + str(time_key))

                unseen_pipeline_times[time_group][time_key] = time_info
                key_list.append(time_key)
            
            update_index(
                storage_client = storage_client,
                storage_name = storage_name,
                object_name = 'times',
                path_replacers = {
                    'name': 'PIPELINES'
                },
                path_names = [
                    time_group
                ],
                index_data = index_data,
                index_metadata = index_metadata,
                old_length = old_list_length,
                key_list = key_list
            )
    return unseen_pipeline_times

def gather_bucket_task_times(
    storage_client: any, 
    storage_name: str,
    target_bucket
):
    unseen_task_times = {}

    bucket_info = check_bucket(
        storage_client = storage_client,
        bucket_name = target_bucket 
    )

    bucket_objects = bucket_info['objects']

    path_prefix = set_object_path(
        object_name = 'root',
        path_replacers = {
            'name': 'ARTIFACTS'
        },
        path_names = [
            'TASKS'
        ]
    )

    for object_path in bucket_objects:
        if path_prefix in object_path:
            artifact_path_split = object_path.split('/')
            time_group = artifact_path_split[-1]

            print('Checking tasks of group: ' + str(time_group)) 

            if not time_group in unseen_task_times:
                unseen_task_times[time_group] = {}

            index_data, index_metadata = get_index(
                storage_client = storage_client,
                storage_name = storage_name,
                object_name = 'times',
                path_replacers = {
                    'name': 'TASKS'
                },
                path_names = [
                    time_group
                ]
            )

            task_object = get_object(
                storage_client = storage_client,
                bucket_name = target_bucket,
                object_name = 'tasks',
                path_replacers = {
                    'name': time_group
                },
                path_names = []
            )

            task_data = task_object['data']
            key_list = index_data['keys'] 
            old_list_length = len(key_list) 
            for task_id, task_info in task_data.items():
                time_key = task_id.split('/')[0]
                if time_key in key_list:
                    continue
                
                if not task_info['state'] == 'SUCCESS':
                    break
                
                print('Unseen task times with key: ' + str(time_key))
                unseen_task_times[time_group][time_key] = parse_flower_times(
                    task_info = task_info
                )
                key_list.append(time_key)

            update_index(
                storage_client = storage_client,
                storage_name = storage_name,
                object_name = 'times',
                path_replacers = {
                    'name': 'TASKS'
                },
                path_names = [
                    time_group
                ],
                index_data = index_data,
                index_metadata = index_metadata,
                old_length = old_list_length,
                key_list = key_list
            )

    return unseen_task_times

def gather_times(
    storage_client: any, 
    storage_name: str,
    type: str
):
    container_buckets = check_buckets(
        storage_client = storage_client
    )

    accepted_types = [  
        'job-time', 
        'pipeline-time',
        'task-time'
    ]

    unseen_times = {}
    if 0 < len(container_buckets):
        if type in accepted_types:
            for bucket_name, bucket_info in container_buckets.items():
                bucket_name_split = bucket_name.split('-')
                if 0 < bucket_info['amount']:
                    if type == 'job-time' and bucket_name_split[1] == 'submitter':
                        print('Checking the ' + str(type) + ' of bucket ' + str(bucket_name)) 
                        gathered_unseen_times = gather_bucket_job_times(
                            storage_client = storage_client, 
                            storage_name = storage_name,
                            target_bucket = bucket_name
                        )
                        unseen_times[bucket_name] = gathered_unseen_times
                    if type == 'task-time' and (bucket_name_split[1] == 'submitter' or bucket_name_split[1] == 'forwarder'):
                        print('Checking the ' + str(type) + ' of bucket ' + str(bucket_name))
                        gathered_unseen_times = gather_bucket_task_times(
                            storage_client = storage_client,
                            storage_name = storage_name,
                            target_bucket = bucket_name
                        )
                        unseen_times[bucket_name] = gathered_unseen_times
                    if type == 'pipeline-time' and bucket_name_split[1] == 'pipeline':
                        print('Checking the ' + str(type) + ' of bucket ' + str(bucket_name))
                        gathered_unseen_times = gather_bucket_pipeline_times(
                            storage_client = storage_client,
                            storage_name = storage_name,
                            target_bucket = bucket_name
                        )
                        unseen_times[bucket_name] = gathered_unseen_times
    return unseen_times
