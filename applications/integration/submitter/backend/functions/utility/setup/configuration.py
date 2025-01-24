import time

from functions.utility.storage.objects import set_object
from functions.utility.jobs.data import get_submitter_jobs
from functions.utility.requests.configuration import create_new_venv, install_venv_packages
from functions.utility.requests.files import send_file
from functions.utility.storage.files import get_secret_dict
from functions.utility.storage.time import store_job_time
from functions.utility.storage.objects import get_clients
from functions.platforms.celery import get_signature_id, await_task
from functions.utility.setup.checks import check_enviroment, format_enviroment_data
 
def modify_enviroment(    
    storage_client: any,
    storage_names: str,
    available_secrets: any,
    missing_configuration: any
) -> bool:  
    configured = False

    if 'directory' in missing_configuration:
        # Refactor later 
        # to handle these
        return False
    
    if 'python' in missing_configuration:
        # Refactor later 
        # to handle these
        return False
    
    if 'files' in missing_configuration:
        print('Sending files')
        wanted_files = missing_configuration['files']
        for file_info in wanted_files:
            configured = send_file(
                storage_client = storage_client,
                storage_names = storage_names,
                available_secrets = available_secrets,
                file_info = file_info
            )

    # Refactor later 
    # to handle this
    if 'venv-modules' in missing_configuration:
        # Create a new venv 
        # with the wanted modules
        pass
    
    if 'venv' in missing_configuration:
        # Refactor later
        print('Creating venv')
        platform_secrets = available_secrets['hpc']['mahti']

        wanted_name = missing_configuration['venv']['name']
        wanted_modules = missing_configuration['venv']['configuration-modules']

        configured = create_new_venv(
            platform_secrets = platform_secrets,
            modules = wanted_modules,
            venv_name = wanted_name
        )
    
        missing_configuration['venv-packages'] = {
            'name': wanted_name,
            'configuration-modules': wanted_modules,
            'packages': missing_configuration['venv']['packages']
        }
        
    if 'venv-packages' in missing_configuration:
        # Refactor later
        print('Installing packages')
        platform_secrets = available_secrets['hpc']['mahti']

        used_name = missing_configuration['venv-packages']['name']
        used_modules = missing_configuration['venv-packages']['configuration-modules']
        missing_packages = missing_configuration['venv-packages']['packages']
        
        configured = install_venv_packages(
            platform_secrets = platform_secrets,
            modules = used_modules,
            venv_name = used_name,
            wanted_packages = missing_packages
        )
    return configured
 
def configure_enviroment(
    configuration: any,
    celery_client: any
):
    # Can have 
    # concurrency issues

    storage_clients = get_clients(
        configuration = configuration
    )
    storage_names = configuration['storage-names']
    secrets_path = configuration['enviroments']['secrets-path']

    job_objects = get_submitter_jobs(
        storage_client = storage_clients[0],
        storage_name = storage_names[0]
    )

    available_secrets = get_secret_dict(
        secrets_path = secrets_path
    )
    
    enviroment_manager_id = ''
    if not len(job_objects) == 0:
        enviroments = {}
        updated_enviroment = False
        for job_key, job_object in job_objects.items():
            job_object_data = job_object['data']
            job_object_metadata = job_object['metadata'] 
            # A job should only be configured if: 
            # its started, 
            # is not ready 
            # is not cancelled 
            if job_object_data['start'] and not job_object_data['ready'] and not job_object_data['cancel']:
                print('Configuring job with key: ' + str(job_key))
                begin_job_configuration_time = time.time()
                job_target = job_object_data['target']
                job_target_split = job_target.split('/')
                job_enviroment = job_target_split[0]
                job_platform = job_target_split[1]

                if not job_platform in enviroments:
                    print('Checking enviroment data')
                    enviroments[job_platform] = format_enviroment_data(
                        storage_client = storage_clients[0],
                        storage_name = storage_names[0],
                        enviroment = job_enviroment,
                        platform = job_platform
                    )
                
                if updated_enviroment:
                    task_data = await_task(
                        celery_client = celery_client,
                        task_id = enviroment_manager_id,
                        timeout = 500
                    )
                    
                    updated_enviroment = False
                    if 0 < len(task_data):
                        if task_data['result']: 
                            enviroments[job_platform] = format_enviroment_data(
                                storage_client = storage_clients[0],
                                storage_name = storage_names[0],
                                enviroment = job_enviroment,
                                platform = job_platform
                            )
                            print('Enviroment information updated')

                missing_configuration = check_enviroment(
                    enviroment_data = enviroments[job_platform],
                    job_data = job_object_data
                )

                modification = False
                if len(missing_configuration) == 0:
                    print('Enviroment configuration ready for the job')
                    job_object_data['ready'] = True
                    modification = True
                else:
                    if job_object_data['start']:
                        print('Configuring enviroment for the job')
                        success = modify_enviroment(
                            storage_client = storage_clients[0],
                            storage_names = storage_names,
                            available_secrets = available_secrets,
                            missing_configuration = missing_configuration
                        )
                        if success: 
                            job_object_data['ready'] = True
                            modification = True
                            enviroment_manager_id = get_signature_id(
                                task_name = 'tasks.enviroment-handler',
                                task_kwargs = {
                                    'configuration': configuration
                                }
                            )
                            updated_enviroment = True

                if modification:
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

                    print('Storing configuration time')
                    end_job_configuration_time = time.time()
                    
                    store_job_time(
                        storage_client = storage_clients[0],
                        storage_name = submitter_bucket,
                        job_key = job_key,
                        time_input = {
                            'begin-configuration': begin_job_configuration_time,
                            'end-configuration': end_job_configuration_time,
                        }
                    )                    