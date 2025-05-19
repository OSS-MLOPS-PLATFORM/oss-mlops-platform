import time 

from functions.utility.storage.objects import set_object
from functions.utility.jobs.data import get_submitter_jobs
from functions.utility.storage.files import get_secret_dict
from functions.utility.requests.jobs import send_job 
from functions.utility.storage.time import store_job_time

def run_job(
    platform_secrets: any,
    job_name: str
) -> str:
    job_name_split = job_name.split('/')
    
    job_folder_path = '/'.join(job_name_split[:-1])
    job_file_name = job_name_split[-1]

    job_id = send_job(
        platform_secrets = platform_secrets,
        folder_path = job_folder_path,
        file_name = job_file_name
    )

    return job_id

def submit_jobs( 
    storage_client: any,
    storage_names: str,
    secrets_path: any
):
    # Might have concurrency problems

    # Concurrency source
    job_objects = get_submitter_jobs(
        storage_client = storage_client,
        storage_name = storage_names[0]
    )

    available_secrets = get_secret_dict(
        secrets_path = secrets_path
    )

    # In the future this might 
    # need to be refactored to 
    # handle workflow dependecies
    
    if not len(job_objects) == 0: 
        for job_key, job_object in job_objects.items(): 
            job_object_data = job_object['data']
            job_object_metadata = job_object['metadata']
            # A job should be 
            # submitted if: 
            # its ready
            # not submitted
            # not cancelled
            # not stopped 
            if job_object_data['ready'] and not job_object_data['submit'] and not job_object_data['cancel'] and not job_object_data['stopped']:
                print('Submitting job with key: ' + str(job_key))
                job_target_split = job_object_data['target'].split('/')
                job_enviroment = job_target_split[0]
                job_platform = job_target_split[1]
                platform_secrets = available_secrets[job_enviroment][job_platform]
                print('Run job')
                job_id = run_job(
                    platform_secrets = platform_secrets,
                    job_name = job_object_data['name']
                )
                begin_job_run_time = time.time()
                if not job_id is None: 
                    print('Submitted job aquired id: ' + str(job_id))
                    submitter_bucket = storage_names[0]
                    job_object_data['id'] = job_id
                    job_object_data['submit'] = True
                    job_object_metadata['version'] = job_object_metadata['version'] + 1
                    # Concurrency source
    
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

                    end_job_start_time = time.time()

                    store_job_time(
                        storage_client = storage_client,
                        storage_name = submitter_bucket,
                        job_key = job_key,
                        time_input = {
                            'end-start': end_job_start_time,
                            'begin-run': begin_job_run_time
                        }
                    )