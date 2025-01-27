from math import ceil

from functions.minio_os import minio_check_object, minio_get_object_data_and_metadata, minio_create_or_update_object

def divide_list(
    target_list: any, 
    number: int
):
  size = ceil(len(target_list) / number)
  return list(
    map(lambda x: target_list[x * size:x * size + size],
    list(range(number)))
  )

def get_storage_prefix(
    repository_owner: str, 
    repository_name: str
) -> str:
    return repository_owner + '|' + repository_name + '|'

def get_path_database_and_collection(
    repository_owner: str,
    repository_name: str,
    path: str
) -> str:
    path_split = path.split('/')
    database_name = get_storage_prefix(repository_owner, repository_name) + path_split[-1].split('.')[-1]
    collection_name = ''
    for word in path_split[:-1]:
        collection_name += word[:2] + '|'
    collection_name += path_split[-1].split('.')[0]
    return database_name, collection_name

def get_checked(
    object_client: any,
    storage_parameters: any,
    prefix: str
):
    used_object_bucket = storage_parameters['object-bucket']
    used_object_path = storage_parameters['object-path'] + '-' + prefix
    
    object_exists = minio_check_object(
        minio_client = object_client,
        bucket_name = used_object_bucket, 
        object_path = used_object_path
    )

    data = []
    if object_exists:
        data = minio_get_object_data_and_metadata(
            minio_client = object_client,
            bucket_name = used_object_bucket, 
            object_path = used_object_path
        )['data']
    return data

def store_checked(
    object_client: any,
    storage_parameters: any,
    prefix: str,
    checked: any
):
    used_object_bucket = storage_parameters['object-bucket']
    used_object_path = storage_parameters['object-path'] + '-' + prefix
    
    minio_create_or_update_object(
        minio_client = object_client,
        bucket_name = used_object_bucket, 
        object_path = used_object_path,
        data = checked, 
        metadata = {}
    )