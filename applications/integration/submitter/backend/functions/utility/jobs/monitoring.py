import time

from functions.utility.storage.objects import set_object
from functions.utility.jobs.data import get_submitter_jobs
from functions.utility.storage.files import get_secret_dict
from functions.utility.requests.jobs import  halt_job
from functions.utility.jobs.data import get_supercomputer_jobs    
from functions.utility.storage.time import store_job_time
from functions.platforms.celery import await_signature
from functions.utility.storage.objects import get_clients
 
def stop_job(
    platform_secrets: any,
    job_id: str
) -> bool:
    return halt_job(
        platform_secrets = platform_secrets,
        job_id = job_id
    )

def monitor_jobs(  
    configuration: any, 
    celery_client: any
):
    storage_clients = get_clients(
        configuration = configuration
    )
    storage_names = configuration['storage-names']
    secrets_path = configuration['enviroments']['secrets-path']
    
    task_data = await_signature( 
        celery_client = celery_client,
        task_name = 'tasks.job-handler', 
        task_kwargs = {
            'configuration': configuration
        },
        timeout = 500
    )  
    
    if 0 < len(task_data):
        if task_data['result']:
            job_objects = get_submitter_jobs(
                storage_client = storage_clients[0],
                storage_name = storage_names[0]
            )

            available_secrets = get_secret_dict(
                secrets_path = secrets_path
            )

            if not len(job_objects) == 0:
                platform_jobs = {}
                for job_key, job_object in job_objects.items():
                    job_object_data = job_object['data']
                    job_object_metadata = job_object['metadata']

                    if job_object_data['submit'] and not job_object_data['stopped']:
                        job_target_split = job_object_data['target'].split('/')
                        job_enviroment = job_target_split[0]
                        job_platform = job_target_split[1]
                        job_id = job_object_data['id']
                        platform_secrets = available_secrets[job_enviroment][job_platform]
                        print('Monitoring job with key ' + str(job_key) + ' and id ' + str(job_id))
                        current_jobs = {}
                        if not job_platform in platform_jobs:
                            print('Checking jobs in ' + str(job_platform))
                            current_jobs = get_supercomputer_jobs(
                                platform_secrets = platform_secrets
                            )
                            platform_jobs[job_platform] = {
                                'time': time.time(),
                                'data': current_jobs
                            }
                        else:
                            previous_time = platform_jobs[job_platform]['time']
                            current_time = time.time()
                            timeout = (current_time-previous_time)
                            print('Supercomputer job check timeout: ' + str(timeout))
                            if 20 < timeout:
                                current_jobs = get_supercomputer_jobs(
                                    platform_secrets = platform_secrets
                                )
                                platform_jobs[job_platform] = {
                                    'time': time.time(),
                                    'data': current_jobs
                                }
                            else:
                                current_jobs = platform_jobs[job_platform]['data']
                        
                        job_modified = False
                        end_job_run_time = 0
                        end_cancel_time = 0
                        
                        if not job_id in current_jobs:
                            # Squeue only shows 
                            # active jobs. Thus, 
                            # jobs that are not 
                            # seen are either 
                            # complete or failed. 
                            # This can be seen 
                            # in sacct, which means 
                            # the only relevant 
                            # states are pending, 
                            # running and stopped
                            print('Job completed itself')
                            job_object_data['stopped'] = True
                            end_job_run_time = time.time()
                            job_modified = True
                        else: 
                            print('Job is running')
                            job_info = current_jobs[job_id]
                            job_state = job_info['state']
                            if not job_object_data['pending'] and job_state == 'pending':
                                job_object_data[job_state] = True
                                job_modified = True

                            if not job_object_data['running'] and job_state == 'running':
                                job_object_data[job_state] = True
                                job_modified = True

                            if job_object_data['cancel']:
                                cancelled = stop_job(
                                    platform_secrets = platform_secrets,
                                    job_id = job_id
                                )
                                print('Job cancelled: ' + str(cancelled))
                                job_object_data['stopped'] = True
                                end_job_run_time = time.time()
                                end_cancel_time = time.time()
                                job_modified = True

                        if job_modified:
                            submitter_bucket = storage_names[0]
                            job_object_metadata['version'] = job_object_metadata['version'] + 1
                            
                            set_object(
                                storage_client = storage_clients[0],
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

                            begin_job_store_time = time.time()
                            if job_object_data['stopped']:
                                store_job_time(
                                    storage_client = storage_clients[0],
                                    storage_name = submitter_bucket,
                                    job_key = job_key,
                                    time_input = {
                                        'end-run': end_job_run_time,
                                        'end-cancel': end_cancel_time,
                                        'begin-store': begin_job_store_time
                                    }
                                )