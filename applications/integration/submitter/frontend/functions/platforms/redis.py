import pickle


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