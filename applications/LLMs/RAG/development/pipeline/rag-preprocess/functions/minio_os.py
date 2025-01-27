
import io
import pickle
from minio import Minio

def is_minio_client(
    storage_client: any
) -> bool:
    return isinstance(storage_client, Minio)

def minio_setup_client(
    endpoint: str,
    username: str,
    password: str
) -> any:
    minio_client = Minio(
        endpoint = endpoint, 
        access_key = username, 
        secret_key = password,
        secure = False
    )
    return minio_client

def minio_pickle_data(
    data: any
) -> any:
    pickled_data = pickle.dumps(data)
    length = len(pickled_data)
    buffer = io.BytesIO()
    buffer.write(pickled_data)
    buffer.seek(0)
    return buffer, length

def minio_unpickle_data(
    pickled: any
) -> any:
    return pickle.loads(pickled)

def minio_create_bucket(
    minio_client: any,
    bucket_name: str
) -> bool: 
    try:
        minio_client.make_bucket(
            bucket_name = bucket_name
        )
        return True
    except Exception as e:
        print('MinIO bucket creation error')
        print(e)
        return False
    
def minio_check_bucket(
    minio_client: any,
    bucket_name:str
) -> bool:
    try:
        status = minio_client.bucket_exists(
            bucket_name = bucket_name
        )
        return status
    except Exception as e:
        print('MinIO bucket checking error')
        print(e)
        return False 
       
def minio_delete_bucket(
    minio_client: any,
    bucket_name:str
) -> bool:
    try:
        minio_client.remove_bucket(
            bucket_name = bucket_name
        )
        return True
    except Exception as e:
        print('MinIO bucket deletion error')
        print(e)
        return False

def minio_create_object(
    minio_client: any,
    bucket_name: str, 
    object_path: str, 
    data: any,
    metadata: dict
) -> bool: 
    # Be aware that MinIO objects have a size limit of 1GB, 
    # which might result to large header error    
    
    try:
        buffer, length = minio_pickle_data(
            data = data
        )

        minio_client.put_object(
            bucket_name = bucket_name,
            object_name = object_path,
            data = buffer,
            length = length,
            metadata = metadata
        )
        return True
    except Exception as e:
        print('MinIO object creation error')
        print(e)
        return False

def minio_check_object(
    minio_client: any,
    bucket_name: str, 
    object_path: str
) -> any: 
    try:
        object_info = minio_client.stat_object(
            bucket_name = bucket_name,
            object_name = object_path
        )      
        return object_info
    except Exception as e:
        return {}

def minio_delete_object(
    minio_client: any,
    bucket_name: str, 
    object_path: str
) -> bool: 
    try:
        minio_client.remove_object(
            bucket_name = bucket_name, 
            object_name = object_path
        )
        return True
    except Exception as e:
        print('MinIO object deletion error')
        print(e)
        return False

def minio_update_object(
    minio_client: any,
    bucket_name: str, 
    object_path: str, 
    data: any,
    metadata: dict
) -> bool:  
    remove = minio_delete_object(
        minio_client = minio_client,
        bucket_name = bucket_name,
        object_path = object_path
    )
    if remove:
        return minio_create_object(
            minio_client = minio_client, 
            bucket_name = bucket_name, 
            object_path = object_path, 
            data = data,
            metadata = metadata
        )
    return False

def minio_create_or_update_object(
    minio_client: any,
    bucket_name: str, 
    object_path: str, 
    data: any, 
    metadata: dict
) -> bool:
    bucket_status = minio_check_bucket(
        minio_client = minio_client,
        bucket_name = bucket_name
    )
    if not bucket_status:
        creation_status = minio_create_bucket(
            minio_client = minio_client,
            bucket_name = bucket_name
        )
        if not creation_status:
            return False
    object_status = minio_check_object(
        minio_client = minio_client,
        bucket_name = bucket_name, 
        object_path = object_path
    )
    if not object_status:
        return minio_create_object(
            minio_client = minio_client,
            bucket_name = bucket_name, 
            object_path = object_path, 
            data = data, 
            metadata = metadata
        )
    else:
        return minio_update_object(
            minio_client = minio_client,
            bucket_name = bucket_name, 
            object_path = object_path, 
            data = data, 
            metadata = metadata
        )

def minio_get_object_list(
    minio_client: any,
    bucket_name: str,
    path_prefix: str
) -> any:
    try:
        objects = minio_client.list_objects(
            bucket_name = bucket_name, 
            prefix = path_prefix, 
            recursive = True
        )
        return objects
    except Exception as e:
        return None  
    
def minio_get_object_data_and_metadata(
    minio_client: any,
    bucket_name: str, 
    object_path: str
) -> any:
    try:
        given_object_data = minio_client.get_object(
            bucket_name = bucket_name, 
            object_name = object_path
        )
        
        given_data = minio_unpickle_data(
            pickled = given_object_data.data
        )
        
        given_object_info = minio_client.stat_object(
            bucket_name = bucket_name, 
            object_name = object_path
        )
        
        given_metadata = given_object_info.metadata
        
        return {'data': given_data, 'metadata': given_metadata}
    except Exception as e:
        print('MinIO object fetching error')
        print(e)
        return None
