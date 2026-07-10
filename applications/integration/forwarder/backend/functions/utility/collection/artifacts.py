from functions.utility.storage.objects import set_object_path, check_buckets, check_bucket, get_object, set_object
from functions.utility.collection.indexing import get_index, update_index

def gather_artifacts(
    storage_client: any, 
    storage_name: str,
    type: str
):
    container_buckets = check_buckets(
        storage_client = storage_client
    )

    accepted_types = [
        'sacct', 
        'seff'
    ]

    unseen_artifacts = {} 
    if 0 < len(container_buckets):
        if type in accepted_types:
            for bucket_name, bucket_info in container_buckets.items():
                bucket_name_split = bucket_name.split('-')
                if bucket_name_split[1] == 'submitter':
                    if 0 < bucket_info['amount']:
                        print('Checking the ' + str(type) + ' of bucket ' + str(bucket_name))
                        submitter_bucket_info = check_bucket(
                            storage_client = storage_client,
                            bucket_name = bucket_name
                        )

                        submitter_bucket_objects = submitter_bucket_info['objects']
                        path_prefix = set_object_path(
                            object_name = 'root',
                            path_replacers = {
                                'name': 'ARTIFACTS'
                            },
                            path_names = [
                                type.upper()
                            ]
                        ) 

                        index_data, index_metadata = get_index(
                            storage_client = storage_client,
                            storage_name = storage_name,
                            object_name = 'artifacts',
                            path_replacers = {
                                'name': type.upper()
                            },
                            path_names = [
                                bucket_name
                            ]
                        )
                        
                        key_list = index_data['keys'] 
                        old_list_length = len(key_list)
                        for object_path in submitter_bucket_objects:
                            if path_prefix in object_path:
                                # We will assume that the used 
                                # index will utilize list to check 
                                # for checked out cases. We also 
                                # assume that there is a garbage 
                                # collector that handles the 
                                # reduction of objects and in turn 
                                # the checked set
                                artifact_path_split = object_path.split('/')
                                artifact_key = artifact_path_split[-1]
                                if artifact_key in key_list:
                                    continue
                                
                                print('Unseen artifact with key: ' + str(artifact_key))
                                
                                if not bucket_name in unseen_artifacts:
                                    unseen_artifacts[bucket_name] = {}

                                used_object_name = 'job-' + type

                                artifact_object = get_object(
                                    storage_client = storage_client,
                                    bucket_name = bucket_name,
                                    object_name = used_object_name,
                                    path_replacers = {
                                        'name': artifact_key
                                    },
                                    path_names = []
                                )

                                artifact_data = artifact_object['data'] 

                                unseen_artifacts[bucket_name][artifact_key] = artifact_data
                                key_list.append(artifact_key)
                        
                        update_index(
                            storage_client = storage_client,
                            storage_name = storage_name,
                            object_name = 'artifacts',
                            path_replacers = {
                                'name': type.upper()
                            },
                            path_names = [
                                bucket_name
                            ],
                            index_data = index_data,
                            index_metadata = index_metadata,
                            old_length = old_list_length,
                            key_list = key_list 
                        )
                        
    return unseen_artifacts