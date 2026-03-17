import os
import redis
from celery import Celery
from celery.schedules import timedelta
import pickle

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

    return celery_app

def store_redis_nested_dict(
    redis_client: any,
    dict_name: str,
    nested_dict: any
) -> bool:
    try:
        formatted_dict = pickle.dumps(nested_dict)
        result = redis_client.set(dict_name, formatted_dict)
        return result
    except Exception as e:
        return False

def get_redis_nested_dict(
    redis_client: any,
    dict_name: str
) -> any:
    try:
        pickled_dict = redis_client.get(dict_name)
        unformatted_dict = pickle.loads(pickled_dict)    
        return unformatted_dict
    except Exception as e:
        return None

def setup_beat_scheduling(
    beat_app: any,
    redis_client: any
) -> any:
    schelude_absolute_path = os.path.abspath('celerybeat-schedule')
    
    if os.path.exists(schelude_absolute_path):
        os.remove(schelude_absolute_path)

    configuration_dict = get_redis_nested_dict(
        redis_client = redis_client,
        dict_name = 'configuration'
    )
    
    task_times = os.environ.get('SCHEDULER_TIMES').split('|')
    schedule = []
    expires_seconds = []
    for time in task_times:
        schedule.append(timedelta(seconds = int(time)))
        expires_seconds.append(int(time)) 

    beat_app.conf.beat_schedule = {
        'configuration-manager': {
            'task': 'tasks.forwarding-manager',
            'schedule': schedule[0],
            'kwargs': {
                'configuration': configuration_dict
            },
            'relative': True,
            'options': {
                'expire_seconds': expires_seconds[0]
            }
        },
        'monitoring-manager': {
            'task': 'tasks.collection-manager',
            'schedule': schedule[1],
            'kwargs': {
                'configuration': configuration_dict
            },
            'relative': True,
            'options': {
                'expire_seconds': expires_seconds[1]
            }
        },
        'collections-manager': {
            'task': 'tasks.logging-manager',
            'schedule': schedule[2],
            'kwargs': {
                'configuration': configuration_dict
            },
            'relative': True,
            'options': {
                'expire_seconds': expires_seconds[2]
            }
        },
    }

    beat_app.conf.timezone = 'UTC'
    return beat_app

def setup_beat_app():
    beat_app = get_celery_instance()

    redis_client = redis.Redis(
        host = os.environ.get('REDIS_ENDPOINT'), 
        port = os.environ.get('REDIS_PORT'), 
        db = os.environ.get('REDIS_DB')
    )

    beat_app = setup_beat_scheduling(
        beat_app = beat_app,
        redis_client = redis_client
    )
    
    return beat_app 