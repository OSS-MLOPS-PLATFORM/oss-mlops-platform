from functions.utility.storage.objects import get_clients
from functions.platforms.celery import get_celery_instance
from functions.utility.storage.jobs import store_created_job, store_started_job, store_stopped_job
from functions.utility.storage.forwarding import store_created_forwarding, store_stopped_forwarding
from functions.platforms.redis import get_redis_instance, get_redis_lock, check_redis_lock, release_redis_lock

tasks_celery = get_celery_instance()
 
@tasks_celery.task( 
    bind = False, 
    max_retries = 0,
    soft_time_limit = 120,
    time_limit = 240,
    rate_limit = '2/m',
    name = 'tasks.create-job' 
)
def create_job( 
    configuration,
    job_request 
) -> any:
    # Does need a lock 
    # since chancing data.
    # Only concurrency issue 
    # is with keys
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
                    
                    object_store_config = configuration['enviroments']['storage']['object-store']
                    bucket_parameters = {
                        'bucket-prefix': object_store_config['bucket-prefix'],
                        'ice-id': configuration['ice-id'],
                        'user': job_request['user']
                    }

                    del job_request['user'] 
                    
                    output = store_created_job( 
                        storage_client = storage_clients[0],
                        bucket_parameters = bucket_parameters,
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
    # Does need a lock 
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
                    
                    object_store_config = configuration['enviroments']['storage']['object-store']
                    bucket_parameters = {
                        'bucket-prefix': object_store_config['bucket-prefix'],
                        'ice-id': configuration['ice-id'],
                        'user': job_start['user']
                    }

                    del job_start['user']

                    output =  store_started_job(
                        storage_client = storage_clients[0],
                        bucket_parameters = bucket_parameters,
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
    max_retries = 0,
    soft_time_limit = 120,
    time_limit = 240,
    rate_limit = '2/m',
    name = 'tasks.stop-job'
)
def stop_job(
    configuration,
    job_cancel
):
    # Does need a lock 
    # since chancing data

    # Might need sanitazation

    # Can cause concurrency issues for submitter
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
                    
                    object_store_config = configuration['enviroments']['storage']['object-store']
                    bucket_parameters = {
                        'bucket-prefix': object_store_config['bucket-prefix'],
                        'ice-id': configuration['ice-id'],
                        'user': job_cancel['user']
                    }

                    del job_cancel['user']
                    
                    output = store_stopped_job(
                        storage_client = storage_clients[0],
                        bucket_parameters = bucket_parameters,
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

@tasks_celery.task(
    bind = False, 
    max_retries = 0,
    soft_time_limit = 60,
    time_limit = 120,
    rate_limit = '2/m',
    name = 'tasks.create-forwarding'
)
def create_forwarding(  
    configuration: any,
    forwarding_request: any
) -> any:
    # Does need a lock 
    # since chancing data.
    # Only concurrency 
    # issue is with keys

    # There are import 
    # and export connections.
    # Import connections are 
    # outside the cluster 
    # forwarder into 
    # the cluster.
    # Export connections are 
    # inside the cluster 
    # forwarder outside 
    # the cluster

    try:
        print('Creating a forward from frontend request')

        redis_client = get_redis_instance()

        lock_name = 'create-forwarding-lock'

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
                output = {'keys': '0,0'} 
                
                try: 
                    storage_clients = get_clients(
                        configuration = configuration
                    )
                    
                    storage_names = configuration['storage-names'] 

                    object_store_config = configuration['enviroments']['storage']['object-store']
                    bucket_parameters = {
                        'bucket-prefix': object_store_config['bucket-prefix'],
                        'ice-id': configuration['ice-id'],
                        'user': forwarding_request['user']
                    } 

                    output = store_created_forwarding(
                        storage_client = storage_clients[0],
                        storage_name = storage_names[0],
                        forwarding_request = forwarding_request,
                        bucket_parameters = bucket_parameters,
                    )
                except Exception as e:
                    print('Store created forwarding run error: ' + str(e))

                lock_released = release_redis_lock(
                    redis_lock = redis_lock
                ) 
                
                print('Redis lock released: ' + str(lock_released))

                return output
            else:
                return {'keys': '0,0'} 
        return {'keys': '0,0'} 
    except Exception as e:
        print('Create forwarding error: ' + str(e))
        return {'keys': '0,0'} 

@tasks_celery.task(
    bind = False, 
    max_retries = 0,
    soft_time_limit = 60,
    time_limit = 120,
    rate_limit = '2/m',
    name = 'tasks.stop-forwarding'
)
def stop_forwarding(
    configuration: any,
    forwarding_cancel: any
) -> any:
    # Does need a lock 
    # since chancing data

    # Can cause concurrency 
    # issues with celery workers 

    # Might need sanitazation
    try:
        print('Stopping a forward from frontend request')

        redis_client = get_redis_instance()

        lock_name = 'stop-forwarding-lock'

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

                    object_store_config = configuration['enviroments']['storage']['object-store']
                    bucket_parameters = {
                        'bucket-prefix': object_store_config['bucket-prefix'],
                        'ice-id': configuration['ice-id'],
                        'user': forwarding_cancel['user'] 
                    }
                    
                    output = store_stopped_forwarding(
                        storage_client = storage_clients[0],
                        storage_name = storage_names[0],
                        forwarding_cancel = forwarding_cancel,
                        bucket_parameters = bucket_parameters,
                    )
                except Exception as e:
                    print('Store created forwarding run error: ' + str(e))

                lock_released = release_redis_lock(
                    redis_lock = redis_lock
                ) 
                
                print('Redis lock released: ' + str(lock_released))

                return output
            else:
                return {'keys': 'fail'} 
        return {'keys': 'fail'} 
    except Exception as e:
        print('Stop forwarding error: ' + str(e))
        return {'keys': 'fail'}