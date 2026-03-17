from functions.platforms.celery import get_celery_instance
from functions.utility.storage.objects import get_clients
from functions.platforms.celery import get_celery_instance
from functions.utility.collection.management import utilize_artifacts
from functions.platforms.redis import get_redis_instance, get_redis_lock, check_redis_lock, release_redis_lock
 
tasks_celery = get_celery_instance()
 
@tasks_celery.task(   
    bind = False, 
    max_retries = 0,
    soft_time_limit = 480, 
    time_limit = 960,
    rate_limit = '2/m',
    name = 'tasks.sacct-collector'
)
def sacct_collector( 
    configuration
): 
    # Does need a lock 
    # since chancing data

    try:   
        print('Collecting saccts per backend request')

        redis_client = get_redis_instance()

        lock_name = 'sacct-collector-lock'

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

                    utilize_artifacts(
                        storage_client = storage_clients[0],
                        storage_name = storage_names[0],
                        type = 'sacct'
                    ) 

                    status = True
                except Exception as e:
                    print('Utilize artifacts run error: ' + str(e))

                lock_released = release_redis_lock(
                    redis_lock = redis_lock
                ) 
                
                print('Redis lock released: ' + str(lock_released))

                return status
            else:
                return False
        return False
    except Exception as e:
        print('Sacct collector error:' + str(e))
        return False

@tasks_celery.task( 
    bind = False, 
    max_retries = 0,
    soft_time_limit = 480,
    time_limit = 960,
    rate_limit = '2/m',
    name = 'tasks.seff-collector'
)
def seff_collector( 
    configuration
):
    # Does need a lock 
    # since chancing data

    try:  
        print('Collecting seff per backend request')

        redis_client = get_redis_instance()

        lock_name = 'seff-collector-lock'

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

                    utilize_artifacts(
                        storage_client = storage_clients[0],
                        storage_name = storage_names[0],
                        type = 'seff'
                    )

                    status = True
                except Exception as e:
                    print('Utilize artifacts run error: ' + str(e))

                lock_released = release_redis_lock(
                    redis_lock = redis_lock
                ) 
                
                print('Redis lock released: ' + str(lock_released))

                return status
            else:
                return False
        return False
    except Exception as e:
        print('Seff collector error:' + str(e))
        return False
    