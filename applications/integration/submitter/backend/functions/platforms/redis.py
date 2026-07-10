import os
import redis
import pickle

def get_redis_instance():
    redis_endpoint = os.environ.get('REDIS_ENDPOINT')
    redis_port = os.environ.get('REDIS_PORT')
    redis_db = os.environ.get('REDIS_DB')
    redis_client = redis.Redis(
        host = redis_endpoint,
        port = int(redis_port),
        db = redis_db
    )
    return redis_client

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

def get_redis_lock(
    redis_client: any,
    lock_name: str,
    timeout: int
) -> any:
    redis_lock = redis_client.lock(
        lock_name,
        timeout = timeout
    )

    lock_aquired = redis_lock.acquire(blocking = True)

    if lock_aquired:
        return True, redis_lock
    return False, redis_lock

def check_redis_lock(
    redis_client: any,
    lock_name: str
) -> bool:
    if redis_client.exists(lock_name) == 1:
        return True
    return False

def release_redis_lock(
    redis_lock: any
) -> bool:
    if redis_lock.locked():
        redis_lock.release()
        return True
    return False
