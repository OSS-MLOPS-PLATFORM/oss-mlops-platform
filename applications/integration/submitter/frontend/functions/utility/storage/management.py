from functions.utility.general import set_formatted_user

def set_storage_names(
    configuration: any
) -> any:
    # We assume api model order: 
    # object storage
    # relational storage
    # nosql storage
    storage_names = []
    ice_id = configuration['ice-id']
    user = configuration['user']
    storage_parameters = configuration['enviroments']['storage']
    if not len(storage_parameters['object-store']) == 0:
        bucket_prefix = storage_parameters['object-store']['bucket-prefix']
        storage_names.append(bucket_prefix + '-submitter-' + ice_id + '-' + set_formatted_user(user = user))
        storage_names.append(bucket_prefix + '-pipeline-' + ice_id + '-' + set_formatted_user(user = user))
    return storage_names

def modify_storage_configuration(
    configuration: any
) -> any:
    configuration['storage-names'] = set_storage_names(
        configuration = configuration
    )
    return configuration