from functions.utility.storage.objects import get_object, set_object

def get_index(
    storage_client: any,
    storage_name: str,
    object_name: str,
    path_replacers: any,
    path_names: any  
):
    index_object = get_object(
        storage_client = storage_client,
        bucket_name = storage_name,
        object_name = object_name,
        path_replacers = path_replacers,
        path_names = path_names
    )

    index_data = {}
    index_metadata = {}
    if len(index_object) == 0:  
        index_template = get_object(
            storage_client = storage_client,
            bucket_name = storage_name,
            object_name = 'monitor',
            path_replacers = {
                'name': 'index-template'
            },
            path_names = [] 
        )
        index_data = index_template['data']
        index_metadata = index_template['custom-meta']
    else:
        index_data = index_object['data']
        index_metadata = index_object['custom-meta']
    return index_data, index_metadata 

def update_index(
    storage_client: any,
    storage_name: str,
    object_name: str,
    path_replacers: any,
    path_names: any,
    index_data: any,
    index_metadata: any,
    old_length: int,
    key_list: any
):
    if not len(key_list) == old_length: 
        index_data['keys'] = key_list
        index_metadata['version'] = index_metadata['version'] + 1
        set_object(
            storage_client = storage_client,
            bucket_name = storage_name,
            object_name = object_name,
            path_replacers = path_replacers,
            path_names = path_names,
            overwrite = True,
            object_data = index_data,
            object_metadata = index_metadata
        )
    