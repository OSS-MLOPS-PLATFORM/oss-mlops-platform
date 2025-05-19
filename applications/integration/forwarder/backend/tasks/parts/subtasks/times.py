from functions.platforms.celery import get_celery_instance
from functions.utility.storage.objects import get_clients
from functions.platforms.celery import get_celery_instance
from functions.utility.collection.management import utilize_time
from functions.platforms.redis import get_redis_instance, get_redis_lock, check_redis_lock, release_redis_lock
 
tasks_celery = get_celery_instance()
   
@tasks_celery.task( 
    bind = False, 
    max_retries = 0,
    soft_time_limit = 480,
    time_limit = 960,
    rate_limit = '2/m',
    name = 'tasks.job-time-collector'
)
def job_time_collector( 
    configuration
):
    # Does need a lock 
    # since chancing data

    try:   
        print('Collecting job times per backend request')

        redis_client = get_redis_instance()

        lock_name = 'job-time-collector-lock'

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
                status = False
                try:
                    storage_clients = get_clients(
                        configuration = configuration
                    )
                    storage_names = configuration['storage-names']

                    utilize_time(
                        storage_client = storage_clients[0],
                        storage_name = storage_names[0],
                        type = 'job-time'
                    ) 

                    status = True
                except Exception as e:
                    print('Utilize time run error: ' + str(e))

                lock_released = release_redis_lock(
                    redis_lock = redis_lock
                ) 
                
                print('Redis lock released: ' + str(lock_released))

                return status
            else:
                return False
        return False
    except Exception as e:
        print('Job time collector error:' + str(e))
        return False

@tasks_celery.task( 
    bind = False,  
    max_retries = 0,
    soft_time_limit = 480,
    time_limit = 960,
    rate_limit = '2/m',
    name = 'tasks.pipeline-time-collector'
)
def pipeline_time_collector( 
    configuration
):
    # Does need a lock 
    # since chancing data

    try:   
        print('Collecting job times per backend request')

        redis_client = get_redis_instance()

        lock_name = 'pipeline-time-collector-lock'

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
                status = False
                try:
                    storage_clients = get_clients(
                        configuration = configuration
                    )
                    storage_names = configuration['storage-names']

                    utilize_time(
                        storage_client = storage_clients[0],
                        storage_name = storage_names[0],
                        type = 'pipeline-time'
                    )

                    status = True
                except Exception as e:
                    print('Utilize time run error: ' + str(e))

                lock_released = release_redis_lock(
                    redis_lock = redis_lock
                ) 
                
                print('Redis lock released: ' + str(lock_released))

                return status
            else:
                return False
        return False
    except Exception as e:
        print('Pipeline time collector error:' + str(e))
        return False

@tasks_celery.task( 
    bind = False, 
    max_retries = 0,
    soft_time_limit = 480,
    time_limit = 960,
    rate_limit = '2/m',
    name = 'tasks.task-time-collector'
)
def task_time_collector( 
    configuration
):
    # Does need a lock 
    # since chancing data

    try:   
        print('Collecting task times per backend request')

        redis_client = get_redis_instance()

        lock_name = 'task-time-collector-lock'

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
                status = False
                try:
                    storage_clients = get_clients( 
                        configuration = configuration
                    )
                    storage_names = configuration['storage-names']

                    utilize_time(
                        storage_client = storage_clients[0],
                        storage_name = storage_names[0],
                        type = 'task-time'
                    )

                    status = True
                except Exception as e:
                    print('Utilize time run error: ' + str(e))

                lock_released = release_redis_lock(
                    redis_lock = redis_lock
                ) 
                
                print('Redis lock released: ' + str(lock_released))

                return status
            else:
                return False
        return False
    except Exception as e:
        print('Task time collector error:' + str(e))
        return False
