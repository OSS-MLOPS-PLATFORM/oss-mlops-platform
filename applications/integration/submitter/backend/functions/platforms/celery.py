import time
import os
import shutil

from celery import Celery, signature
from celery.result import AsyncResult

def setup_celery_logging():
    log_directory = os.path.abspath('logs')
    
    if os.path.exists(log_directory):
        shutil.rmtree(log_directory)
    
    os.makedirs(log_directory, exist_ok=True)
    log_path = log_directory + '/backend.log'
    with open(log_path, 'w') as f:
        pass

    return log_path

def get_celery_logs(): 
    log_path = os.path.abspath('logs/backend.log')
    listed_logs = {'logs':[]}
    with open(log_path, 'r') as f:
        for line in f:
            listed_logs['logs'].append(line.strip())
    return listed_logs

def get_celery_instance():
    redis_endpoint = os.environ.get('REDIS_ENDPOINT')
    redis_port = os.environ.get('REDIS_PORT')
    redis_db = os.environ.get('REDIS_DB')
    
    name = 'tasks'
    redis_connection = 'redis://' + redis_endpoint + ':' + str(redis_port) + '/' + str(redis_db)

    celery_app = Celery(
        main = name,
        broker = redis_connection,
        backend = redis_connection
    )

    celery_app.conf.broker_connection_retry_on_startup = True

    return celery_app

def check_task_status(
    celery_client: any,
    task_id: str
) -> any:
    response = AsyncResult(
        id = task_id, 
        app = celery_client
    )
    return response.state

def get_task_result(
    celery_client: any,
    task_id: str
) -> any:
    response = AsyncResult(
        id = task_id, 
        app = celery_client
    )
    return response.result

def get_task( 
    celery_client: any,
    task_id: str
) -> any:
    task_data = {
        'status': '',
        'result': None
    }
    task_status = check_task_status(
        celery_client = celery_client,
        task_id = task_id
    )
    task_data['status'] = task_status
    if task_status == 'SUCCESS':
        task_result = get_task_result(
            celery_client = celery_client,
            task_id = task_id
        )
        task_data['result'] = task_result
    return task_data

def await_task(
    celery_client: any,
    task_id: str,
    timeout: int
) -> any:
    task_data = {}
    start = time.time()
    # In the case of 
    # errors this
    # makes wait the 
    # whole timeout
    while time.time() - start <= timeout:
        task_data = get_task(
            celery_client = celery_client,
            task_id = task_id
        )
        if not task_data['result'] is None:
            break
        time.sleep(2)
    return task_data

def get_signature_id(
    task_name: str,
    task_kwargs: any
) -> str:
    task = None
    if 0 < len(task_kwargs):
        task = signature(task_name, kwargs = task_kwargs)
    else: 
        task = signature(task_name)
    celery_task = task.apply_async()
    return celery_task.id

def await_signature(
    celery_client: any,
    task_name: str,
    task_kwargs: any,
    timeout: int
) -> any:
    task_id = get_signature_id(
        task_name = task_name,
        task_kwargs = task_kwargs
    )
    return await_task(
        celery_client = celery_client,
        task_id = task_id,
        timeout = timeout
    )