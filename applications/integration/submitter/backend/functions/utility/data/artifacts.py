import time

from functions.utility.jobs.data import get_submitter_jobs
from functions.utility.storage.files import get_secret_dict
from functions.utility.storage.time import get_job_time
from functions.utility.data.storing import store_objects
from functions.utility.storage.objects import set_object
from functions.utility.storage.time import store_job_time

def collect_artifacts(  
    storage_client: any,
    storage_names: any,
    secrets_path: str 
): 
    job_objects = get_submitter_jobs(
        storage_client = storage_client,
        storage_name = storage_names[0]
    )

    available_secrets = get_secret_dict(
        secrets_path = secrets_path
    )

    if not len(job_objects) == 0:
        for job_key, job_object in job_objects.items():
            job_object_data = job_object['data']
            job_object_metadata = job_object['metadata']
            # Jobs artifacts 
            # should be collected if 
            # it was stopped 
            # and not already stored
            if job_object_data['stopped'] and not job_object_data['stored']:
                print('Collecting artifacts for job with key: ' + str(job_key))
                job_time = get_job_time(
                    storage_client = storage_client,
                    storage_name = storage_names[0],
                    job_key = job_key
                )
                begin_job_storage_time = job_time['data']['begin-store']
                end_job_storage_time = time.time()
                timeout = (end_job_storage_time-begin_job_storage_time)
                print('Store artifacts timeout: ' + str(timeout))
                if 120 < timeout:
                    job_target_split = job_object_data['target'].split('/')
                    job_enviroment = job_target_split[0]
                    job_platform = job_target_split[1]
                    platform_secrets = available_secrets[job_enviroment][job_platform]
                    job_id = job_object_data['id']
                    job_storable_files = job_object_data['files']['store']

                    stored = store_objects(
                        storage_client = storage_client,
                        storage_names = storage_names,
                        target_secrets = platform_secrets,
                        job_key = job_key,
                        job_id = job_id,
                        storable_files = job_storable_files
                    )

                    if stored:
                        submitter_bucket = storage_names[0]
                        job_object_data['stored'] = True
                        job_object_metadata['version'] = job_object_metadata['version'] + 1
                        
                        set_object(
                            storage_client = storage_client,
                            bucket_name = submitter_bucket,
                            object_name = 'jobs',
                            path_replacers = {
                                'name': job_key
                            },
                            path_names = [],
                            overwrite = True,
                            object_data = job_object_data,
                            object_metadata = job_object_metadata
                        )
                        
                        end_job_storage_time = time.time()

                        store_job_time(
                            storage_client = storage_client,
                            storage_name = submitter_bucket,
                            job_key = job_key,
                            time_input = {
                                'end-store': end_job_storage_time
                            }
                        )