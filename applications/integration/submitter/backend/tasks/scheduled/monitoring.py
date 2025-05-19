from functions.utility.jobs.monitoring import monitor_jobs
from functions.platforms.celery import get_celery_instance
from functions.platforms.redis import get_redis_instance, get_redis_lock, check_redis_lock, release_redis_lock

tasks_celery = get_celery_instance() 

@tasks_celery.task(  
    bind = False, 
    max_retries = 0,
    soft_time_limit = 480,
    time_limit = 960,
    rate_limit = '1/m',
    name = 'tasks.monitoring-manager'
)
def monitoring_manager(    
    configuration: any
) -> bool:
    try:   
        print('Managing monitoring per scheduler request')

        redis_client = get_redis_instance()

        lock_name = 'monitoring-manager-lock'

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
                    print('Running monitor jobs') 
                    monitor_jobs(   
                        configuration = configuration,
                        celery_client = tasks_celery
                    ) 

                    status = True
                except Exception as e:
                    print('Monitor jobs error: ' + str(e))

                lock_released = release_redis_lock(
                    redis_lock = redis_lock
                )

                print('Redis lock released: ' + str(lock_released))

                return status
            else:
                return False
        return False
    except Exception as e:
        print('Monitoring handler error: ' + str(e))
        return False
