import re
from datetime import timedelta
import collections.abc

def get_porter_logs():
    logs_path = 'logs/porter.log'
    listed_logs = {'porter-logs':[]}
    with open(logs_path, 'r') as f:
        for line in f:
            listed_logs['porter-logs'].append(line.strip())
    return listed_logs

def unit_converter(
    value: str,
    bytes: bool
) -> any:
    units = {
        'K': {
            'normal': 1000,
            'bytes': 1024
        },
        'M': {
            'normal': 1000**2,
            'bytes': 1024**2
        },
        'G': {
            'normal': 1000**3,
            'bytes': 1024**3
        },
        'T': {
            'normal': 1000**4,
            'bytes': 1024**4
        },
        'P': {
            'normal': 1000**5,
            'bytes': 1024**5
        }
    }
    
    converted_value = 0
    unit_letter = ''

    character_index = 0
    for character in value:
        if character.isalpha():
            unit_letter = character
            break
        character_index += 1
    
    if 0 < len(unit_letter):
        if not bytes:
            converted_value = int(float(value[:character_index]) * units[unit_letter]['normal'])
        else:
            converted_value = int(float(value[:character_index]) * units[unit_letter]['bytes'])
    else:
        converted_value = value
    return converted_value

def convert_into_seconds(
    given_time: str
) -> int:
    days = 0
    hours = 0
    minutes = 0
    seconds = 0
    milliseconds = 0

    day_split = given_time.split('-')
    if '-' in given_time:
        days = int(day_split[0])

    millisecond_split = day_split[-1].split('.')
    if '.' in given_time:
        milliseconds = int(millisecond_split[1])
    
    hour_minute_second_split = millisecond_split[0].split(':')

    if len(hour_minute_second_split) == 3:
        hours = int(hour_minute_second_split[0])
        minutes = int(hour_minute_second_split[1])
        seconds = int(hour_minute_second_split[2])
    else:
        minutes = int(hour_minute_second_split[0])
        seconds = int(hour_minute_second_split[1])
    
    result = timedelta(
        days = days,
        hours = hours,
        minutes = minutes,
        seconds = seconds,
        milliseconds = milliseconds
    ).total_seconds()
    return result

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