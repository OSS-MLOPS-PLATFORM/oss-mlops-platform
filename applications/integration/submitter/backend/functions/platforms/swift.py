import swiftclient as sc

def is_swift_client(
    storage_client: any
) -> any:
    return isinstance(storage_client, sc.Connection)

def swift_setup_client(
    pre_auth_url: str,
    pre_auth_token: str,
    user_domain_name: str,
    project_domain_name: str,
    project_name: str,
    auth_version: str
) -> any:
    swift_client = sc.Connection(
        preauthurl = pre_auth_url,
        preauthtoken = pre_auth_token,
        os_options = {
            'user_domain_name': user_domain_name,
            'project_domain_name': project_domain_name,
            'project_name': project_name
        },
        auth_version = auth_version
    )
    return swift_client

def swift_create_bucket(
    swift_client: any,
    bucket_name: str
) -> bool:
    try:
        swift_client.put_container(
            container = bucket_name
        )
        return True
    except Exception as e:
        return False

def swift_check_bucket(
    swift_client: any,
    bucket_name:str
) -> any:
    try:
        bucket_info = swift_client.get_container(
            container = bucket_name
        )
        bucket_metadata = bucket_info[0]
        list_of_objects = bucket_info[1]
        return {'metadata': bucket_metadata, 'objects': list_of_objects}
    except Exception as e:
        return {} 

def swift_delete_bucket(
    swift_client: any,
    bucket_name: str
) -> bool:
    try:
        swift_client.delete_container(
            container = bucket_name
        )
        return True
    except Exception as e:
        return False

def swift_list_buckets(
    swift_client: any
) -> any:
    try:
        account_buckets = swift_client.get_account()[1]
        return account_buckets
    except Exception as e:
        return {}

def swift_create_object(
    swift_client: any,
    bucket_name: str, 
    object_path: str, 
    object_data: any,
    object_metadata: any
) -> bool: 
    # This should be updated 
    # to handle 5 GB objects
    # It also should handle 
    # metadata
    try:
        swift_client.put_object(
            container = bucket_name,
            obj = object_path,
            contents = object_data,
            headers = object_metadata
        )
        return True
    except Exception as e:
        return False

def swift_check_object(
    swift_client: any,
    bucket_name: str, 
    object_path: str
) -> any: 
    try:
        object_metadata = swift_client.head_object(
            container = bucket_name,
            obj = object_path
        )       
        return object_metadata
    except Exception as e:
        return {} 

def swift_get_object(
    swift_client:any,
    bucket_name: str,
    object_path: str
) -> any:
    try:
        response = swift_client.get_object(
            container = bucket_name,
            obj = object_path 
        )
        object_info = response[0]
        object_data = response[1]
        return {'data': object_data, 'info': object_info}
    except Exception as e:
        return {}     
   
def swift_remove_object(
    swift_client: any,
    bucket_name: str, 
    object_path: str
) -> bool: 
    try:
        swift_client.delete_object(
            container = bucket_name, 
            obj = object_path
        )
        return True
    except Exception as e:
        return False

def swift_update_object(
    swift_client: any,
    bucket_name: str, 
    object_path: str, 
    object_data: any,
    object_metadata: any
) -> bool:  
    remove = swift_remove_object(
        swift_client = swift_client, 
        bucket_name = bucket_name, 
        object_path = object_path
    )
    if not remove:
        return False
    create = swift_create_object(
        swift_client = swift_client, 
        bucket_name = bucket_name, 
        object_path = object_path, 
        object_data = object_data,
        object_metadata = object_metadata
    )
    return create
# 
def swift_create_or_update_object(
    swift_client: any,
    bucket_name: str, 
    object_path: str, 
    object_data: any,
    object_metadata: any
) -> any:
    bucket_info = swift_check_bucket(
        swift_client = swift_client, 
        bucket_name = bucket_name
    )
    
    if len(bucket_info) == 0:
        creation_status = swift_create_bucket(
            swift_client = swift_client, 
            bucket_name = bucket_name
        )
        if not creation_status:
            return False
    
    object_info = swift_check_object(
        swift_client = swift_client, 
        bucket_name = bucket_name, 
        object_path = object_path
    )
    
    if len(object_info) == 0:
        return swift_create_object(
            swift_client = swift_client, 
            bucket_name = bucket_name, 
            object_path = object_path, 
            object_data = object_data,
            object_metadata = object_metadata
        )
    else:
        return swift_update_object(
            swift_client = swift_client, 
            bucket_name = bucket_name, 
            object_path = object_path, 
            object_data = object_data,
            object_metadata = object_metadata
        )