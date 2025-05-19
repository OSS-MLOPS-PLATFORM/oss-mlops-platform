from functions.utility.storage.objects import get_clients
from functions.utility.jobs.submission import submit_jobs
from functions.platforms.celery import get_celery_instance
from functions.platforms.redis import get_redis_instance, get_redis_lock, check_redis_lock, release_redis_lock

tasks_celery = get_celery_instance()

@tasks_celery.task(
    bind = False, 
    max_retries = 0,
    soft_time_limit = 480,
    time_limit = 960,
    rate_limit = '1/m',
    name = 'tasks.job-handler'
)
def job_handler(   
    configuration: any
) -> bool:
    try:
        print('Handling jobs for backend')

        redis_client = get_redis_instance()

        lock_name = 'collections-manager-lock'

        lock_exists = check_redis_lock(
            redis_client = redis_client,
            lock_name = lock_name
        )
        print('Redis lock exists: ' + str(lock_exists))
        if not lock_exists:
            lock_active, redis_lock = get_redis_lock(
                redis_client = redis_client,
                lock_name = lock_name,
                timeout = 500
            )
            print('Redis lock aquired: ' + str(lock_active))
            if lock_active:
                status = False

                try:  
                    storage_clients = get_clients(
                        configuration = configuration
                    )
                    storage_names = configuration['storage-names']
                    secrets_path = configuration['enviroments']['secrets-path']
                    
                    submit_jobs(
                        storage_client = storage_clients[0],
                        storage_names = storage_names,
                        secrets_path = secrets_path
                    )

                    status = True
                except Exception as e:
                    print('Submit jobs run error: ' + str(e))

                lock_released = release_redis_lock(
                    redis_lock = redis_lock
                ) 
                
                print('Redis lock released: ' + str(lock_released))

                return status
            else:
                return False 
        return False
    except Exception as e:
        print('Job handler error: ' + str(e))
        return False