from functions.platforms.celery import get_celery_instance
from functions.utility.storage.artifacts import get_job_status, get_job_sacct, get_job_seff, get_job_files
from functions.utility.storage.objects import get_clients
from functions.platforms.celery import get_celery_instance

tasks_celery = get_celery_instance()

@tasks_celery.task( 
    bind = False, 
    max_retries = 0,
    soft_time_limit = 120,
    time_limit = 240,
    rate_limit = '2/m',
    name = 'tasks.fetch-job-status'
)
def fetch_job_status(  
    configuration,
    request 
):
    # Doesn't need lock, 
    # since fetching data
    try:
        print('Fetching job status per frontend request')
        storage_clients = get_clients(
            configuration = configuration
        )

        storage_names = configuration['storage-names']
        
        return get_job_status( 
            storage_client = storage_clients[0],
            storage_name = storage_names[0], 
            request = request
        )
    except Exception as e:
        print('Fetch job status error: ' + str(e))
        return {'job-status': {}} 

@tasks_celery.task( 
    bind = False, 
    max_retries = 0,
    soft_time_limit = 120,
    time_limit = 240,
    rate_limit = '2/m',
    name = 'tasks.fetch-job-sacct'
)
def fetch_job_sacct(
    configuration,
    request
):
    # Doesn't need lock, 
    # since fetching data
    try:
        print('Fetching job sacct per frontend request')
        storage_clients = get_clients(
            configuration = configuration
        )

        storage_names = configuration['storage-names']
        
        return get_job_sacct(
            storage_client = storage_clients[0],
            storage_name = storage_names[0],
            request = request
        )
    except Exception as e:
        print('Fetch job sacct error: ' + str(e))
        return {'job-sacct': {}}

@tasks_celery.task( 
    bind = False, 
    max_retries = 0,
    soft_time_limit = 120,
    time_limit = 240,
    rate_limit = '1/m',
    name = 'tasks.fetch-job-seff'
)
def fetch_job_seff(
    configuration,
    request
):
    # Doesn't need lock, 
    # since fetching data
    try:
        print('Fetching job seff per frontend request')
        storage_clients = get_clients(
            configuration = configuration
        )

        storage_names = configuration['storage-names']
        
        return get_job_seff(
            storage_client = storage_clients[0],
            storage_name = storage_names[0],
            request = request
        )
    except Exception as e:
        print('Fetch job seff error: ' + str(e))
        return {'job-seff': {}}

@tasks_celery.task( 
    bind = False, 
    max_retries = 0,
    soft_time_limit = 120,
    time_limit = 240,
    rate_limit = '1/m',
    name = 'tasks.fetch-job-files'
)
def fetch_job_files(
    configuration,
    request
):
    # Doesn't need lock, 
    # since fetching data
    try:
        print('Fetching job files per frontend request')
        storage_clients = get_clients(
            configuration = configuration
        )

        storage_names = configuration['storage-names']
        
        return get_job_files(
            storage_client = storage_clients[0],
            storage_names = storage_names,
            request = request
        )
    except Exception as e:
        print('Fetch job files error: ' + str(e))
        return {'job-files': {}}