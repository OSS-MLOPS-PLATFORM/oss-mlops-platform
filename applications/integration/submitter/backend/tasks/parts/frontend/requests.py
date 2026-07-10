from functions.utility.storage.objects import get_clients
from functions.platforms.celery import get_celery_instance
from functions.utility.storage.jobs import store_created_job, store_started_job, store_stopped_job
from functions.platforms.redis import get_redis_instance, get_redis_lock, check_redis_lock, release_redis_lock

tasks_celery = get_celery_instance()

@tasks_celery.task(
    bind = False, 
    max_retries = 0,
    soft_time_limit = 120,
    time_limit = 240,
    rate_limit = '1/m',
    name = 'tasks.create-job'
)
def create_job(
    configuration,
    job_request
) -> any:
    # Does need a lock, 
    # since chancing data
    # Only concurrency 
    # issue is with keys
    try:
        print('Creating a job from frontend request')

        redis_client = get_redis_instance()

        lock_name = 'create-job-lock'

        lock_exists = check_redis_lock(
            redis_client = redis_client,
            lock_name = lock_name
        )
        print('Redis lock exists: ' + str(lock_exists))
        if not lock_exists:
            lock_active, redis_lock = get_redis_lock(
                redis_client = redis_client,
                lock_name = lock_name,
                timeout = 200
            )
            print('Redis lock aquired: ' + str(lock_active))
            if lock_active:
                output = {'key': '0'}
                try:
                    storage_clients = get_clients(
                        configuration = configuration
                    )
                    storage_names = configuration['storage-names']
                    
                    output = store_created_job( 
                        storage_client = storage_clients[0],
                        storage_name = storage_names[0],
                        job_request = job_request
                    )
                except Exception as e:
                    print('Store created job run error: ' + str(e))

                lock_released = release_redis_lock(
                    redis_lock = redis_lock
                ) 
                
                print('Redis lock released: ' + str(lock_released))

                return output
            else:
                return {'key': '0'}
        return {'key': '0'}
    except Exception as e:
        print('Create job error: ' + str(e))
        return {'key': '0'}

@tasks_celery.task(
    bind = False, 
    max_retries = 0,
    soft_time_limit = 120,
    time_limit = 240,
    rate_limit = '2/m',
    name = 'tasks.start-job'
)
def start_job(
    configuration,
    job_start
) -> any:
    # Does need a lock, 
    # since chancing data.
    # Only concurrency 
    # issue is with keys

    # Start Job time here
    try:
        print('Starting a job from frontend request')

        redis_client = get_redis_instance()

        lock_name = 'start-job-lock'

        lock_exists = check_redis_lock(
            redis_client = redis_client,
            lock_name = lock_name
        )
        print('Redis lock exists: ' + str(lock_exists))
        if not lock_exists:
            lock_active, redis_lock = get_redis_lock(
                redis_client = redis_client,
                lock_name = lock_name,
                timeout = 200
            )
            print('Redis lock aquired: ' + str(lock_active))
            if lock_active:
                output = {'status': 'fail'}
                try: 
                    storage_clients = get_clients(
                        configuration = configuration
                    )
                    storage_names = configuration['storage-names']

                    output = store_started_job(
                        storage_client = storage_clients[0],
                        storage_name = storage_names[0],
                        job_start = job_start
                    )
                except Exception as e:
                    print('Store started job run error: ' + str(e))

                lock_released = release_redis_lock(
                    redis_lock = redis_lock
                ) 
                
                print('Redis lock released: ' + str(lock_released))

                return output
            else:
                return {'status': 'fail'}
        return {'status': 'fail'}
    except Exception as e:
        print('Start job error: ' + str(e))
        return {'status': 'fail'}

@tasks_celery.task(
    bind = False, 
    max_retries = 1,
    soft_time_limit = 120,
    time_limit = 240,
    rate_limit = '2/m',
    name = 'tasks.stop-job'
)
def stop_job(
    configuration,
    job_cancel
):
    # Does need a lock, 
    # since chancing data.

    # Might need sanitazation

    # Can cause concurrency 
    # issues for submitter
    try:
        print('Stopping a job from frontend request')

        redis_client = get_redis_instance()

        lock_name = 'stop-job-lock'

        lock_exists = check_redis_lock(
            redis_client = redis_client,
            lock_name = lock_name
        )
        print('Redis lock exists: ' + str(lock_exists))
        if not lock_exists:
            lock_active, redis_lock = get_redis_lock(
                redis_client = redis_client,
                lock_name = lock_name,
                timeout = 200
            )
            print('Redis lock aquired: ' + str(lock_active))
            if lock_active:
                output = {'status': 'fail'}
                
                try: 
                    storage_clients = get_clients(
                        configuration = configuration
                    )
                    
                    storage_names = configuration['storage-names']
                    
                    output = store_stopped_job(
                        storage_client = storage_clients[0],
                        storage_name = storage_names[0],
                        job_cancel = job_cancel
                    )
                except Exception as e:
                    print('Store stopped job run error: ' + str(e))

                lock_released = release_redis_lock(
                    redis_lock = redis_lock
                ) 
                
                print('Redis lock released: ' + str(lock_released))

                return output
            else:
                return {'status': 'fail'}
        return {'status': 'fail'}
    except Exception as e:
        print('Stop job error: ' + str(e))
        return {'status': 'fail'}