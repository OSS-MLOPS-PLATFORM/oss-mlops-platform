from functions.utility.storage.objects import get_clients
from functions.platforms.celery import get_celery_instance
from functions.utility.logging.management import collect_logs
from functions.platforms.redis import get_redis_instance, get_redis_lock, check_redis_lock, release_redis_lock

tasks_celery = get_celery_instance()

@tasks_celery.task(
    bind = False, 
    max_retries = 0,
    soft_time_limit = 480,
    time_limit = 960,
    rate_limit = '1/m', 
    name = 'tasks.logging-manager'
)
def logging_manager(
    configuration: any
) -> any:
    # Can cause concurrency 
    # issues with other threads
    try:
        print('Managing logging per scheduler request') 

        redis_client = get_redis_instance()

        lock_name = 'logging-manager-lock'

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
                    print('Running collect logs')
                    storage_clients = get_clients(
                        configuration = configuration
                    )
                    storage_names = configuration['storage-names']

                    collect_logs(
                        storage_client = storage_clients[0],
                        storage_name = storage_names[0]
                    )

                    status = True
                except Exception as e:
                    print('Collect logs error: ' + str(e))
          
                lock_released = release_redis_lock(
                    redis_lock = redis_lock
                ) 

                print('Redis lock released: ' + str(lock_released))

                return status
            else:
                return False
        return False
    except Exception as e:
        print('Logging manager error:' + str(e))
        return False