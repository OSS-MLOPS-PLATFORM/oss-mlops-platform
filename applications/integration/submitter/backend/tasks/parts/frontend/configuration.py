from functions.platforms.celery import get_celery_instance
from functions.utility.scheduling.strategy import setup_pessimistic_strategy
from functions.platforms.redis import get_redis_instance, get_redis_lock, check_redis_lock, release_redis_lock

tasks_celery = get_celery_instance()

@tasks_celery.task(
    bind = False, 
    max_retries = 0,
    soft_time_limit = 480,
    time_limit = 960,
    rate_limit = '1/m', 
    name = 'tasks.setup-handler'
)
def setup_handler(
    configuration: any
):
    # Needs a lock, 
    # since creating data.
    # 1 + 2 threads for optimistic
    # 1 + 1 threads for pessimistic
    try:
        print('Handling setup per frontend request')

        redis_client = get_redis_instance()

        lock_name = 'setup-handler-lock' 
 
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
                    print('Running setup strategy')
                    status = setup_pessimistic_strategy(  
                        celery_client = tasks_celery,
                        configuration = configuration
                    ) 
                except Exception as e:
                    print('Setup strategy error: ' + str(e))
                
                lock_released = release_redis_lock(
                    redis_lock = redis_lock
                ) 

                print('Redis lock released: ' + str(lock_released))

                return status
            else:
                return False
        return False
    except Exception as e:
        print('Setup handler error:' + str(e))
        return False