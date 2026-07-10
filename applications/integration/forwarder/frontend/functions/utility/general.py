import re
import collections.abc

def set_formatted_user(
    user: str   
) -> any:
    return re.sub(r'[^a-z0-9]+', '-', user)

def get_nested_keys(
    nested_dict: any,
    parent_key: str
) -> any:
    keys = []
    for key,value in nested_dict.items():
        formatted_key = ''
        if len(parent_key) == 0:
            formatted_key = key
        else:
            formatted_key += parent_key + '/' + key
        keys.append(formatted_key)
        if isinstance(value, dict):
            inner_keys = get_nested_keys(
                nested_dict = value,
                parent_key = formatted_key
            )
            keys.extend(inner_keys)
    return keys

def update_nested_dict(
    target: any, 
    update: any
) -> any:
    for k, v in update.items():
        if k in target:
            if isinstance(v, collections.abc.Mapping):
                target[k] = update_nested_dict(target.get(k, {}), v)
            else:
                target[k] = v
    return target