from functions.platforms.celery import get_celery_instance
from functions.utility.scheduling.strategy import pessimistic_strategy
from functions.platforms.redis import get_redis_instance, get_redis_lock, check_redis_lock, release_redis_lock

tasks_celery = get_celery_instance()

@tasks_celery.task(
    bind = False, 
    max_retries = 0,
    soft_time_limit = 480,
    time_limit = 960,
    rate_limit = '1/m',
    name = 'tasks.collection-manager'
)
def collection_manager(  
    configuration: any
) -> any:
    # Does need a lock 
    # since chancing data.
    # Can cause concurrency 
    # issues with other threads.
    # 1 + 5 threads with optimistic.
    # 1 + 1 threads with pessimistic
    try:
        print('Collecting per scheduler request') 

        redis_client = get_redis_instance()

        lock_name = 'collection-manager-lock'

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
                output = []
                try:
                    print('Running collection strategy')
                    output = pessimistic_strategy(
                        celery_client = tasks_celery,
                        configuration = configuration
                    )
                except Exception as e:
                    print('Deploy forwards error: ' + str(e))

                lock_released = release_redis_lock(
                    redis_lock = redis_lock
                ) 

                print('Redis lock released: ' + str(lock_released))

                return output
            else:
                return []
        return []
    except Exception as e:
        print('Collection manager error:' + str(e))
        return []
