from functions.platforms.celery import get_celery_instance
from functions.utility.scheduling.management import modify_scheduling
from functions.platforms.redis import get_redis_instance, get_redis_lock, check_redis_lock, release_redis_lock

tasks_celery = get_celery_instance()

@tasks_celery.task( 
    bind = False, 
    max_retries = 0,
    soft_time_limit = 120,
    time_limit = 240,
    rate_limit = '2/m',
    name = 'tasks.start-scheduler'
) 
def start_scheduler(
    scheduler_request: any
) -> any: 
    # Does need a lock 
    # since chancing data.
    # Atleast 1 thread 
    # needs to be ready 
    # any moment
    try:
        print('Starting scheduler per frontend request')

        redis_client = get_redis_instance()

        lock_name = 'start-scheduler-lock'

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
                output = False
                try:
                    output = modify_scheduling(
                        scheduler_request = scheduler_request,
                        action = 'start'
                    ) 
                except Exception as e:
                    print('Modify scheduling run error: ' + str(e))

                lock_released = release_redis_lock(
                    redis_lock = redis_lock
                ) 
                
                print('Redis lock released: ' + str(lock_released))

                return output
            else:
                return False
        return False
    except Exception as e:
        print('Start scheduler error: ' + str(e)) 
        return False
 
@tasks_celery.task( 
    bind = False, 
    max_retries = 0,
    soft_time_limit = 120,
    time_limit = 240,
    rate_limit = '2/m',
    name = 'tasks.stop-scheduler'
) 
def stop_scheduler() -> any:
    # Does need a lock 
    # since chancing data.
    # Atleast 1 thread 
    # needs to be 
    # ready any moment
    try:
        print('Stopping scheduler per frontend request')

        redis_client = get_redis_instance()

        lock_name = 'stop-scheduler-lock'

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
                output = False
                try:
                    output = modify_scheduling(
                        scheduler_request = {},
                        action = 'stop'
                    )
                except Exception as e:
                    print('Modify scheduling run error: ' + str(e))

                lock_released = release_redis_lock(
                    redis_lock = redis_lock
                ) 
                
                print('Redis lock released: ' + str(lock_released))

                return output
            else:
                return False
        return False
    except Exception as e:
        print('Stop scheduler error: ' + str(e))
        return False