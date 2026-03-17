import time

from functions.utility.requests.artifacts import store_sacct, store_seff
from functions.utility.requests.files import store_file 

def store_objects(
    storage_client: any,
    storage_names: any,
    target_secrets: any,
    job_key: str,
    job_id: str,
    storable_files: any 
) -> bool:
    print('Get sacct')
    stored = store_sacct(
        storage_client = storage_client,
        storage_name = storage_names[0],
        target_secrets = target_secrets,
        job_id = job_id,
        job_key = job_key
    )
    
    time.sleep(20)
    print('Get files')
    for file_info in storable_files:
        formatted_info = file_info
        formatted_source = formatted_info['source']
        formatted_target = formatted_info['target']
        if '(id)' in formatted_source:
            formatted_source = formatted_source.replace('(id)', job_id)
            formatted_info['source'] = formatted_source
        if '(key)' in formatted_target:
            formatted_target = formatted_target.replace('(key)', job_key)
            formatted_info['target'] = formatted_target
        stored = store_file(
            storage_client = storage_client,
            storage_names = storage_names,
            target_secrets = target_secrets,
            file_info = formatted_info
        )

    time.sleep(20)
    print('Get seff')
    stored = store_seff(
        storage_client = storage_client,
        storage_name = storage_names[0],
        target_secrets = target_secrets,
        job_id = job_id,
        job_key = job_key
    )

    return stored
