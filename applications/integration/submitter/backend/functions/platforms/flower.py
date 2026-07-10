import os
import requests
from requests.auth import HTTPBasicAuth

def get_flower_parameters():
    parameters = {
        'address': os.environ.get('FLOWER_ENDPOINT'),
        'port': os.environ.get('FLOWER_PORT'),
        'username': os.environ.get('FLOWER_USERNAME'),
        'password': os.environ.get('FLOWER_PASSWORD')
    }
    return parameters
 
def get_flower_tasks(
    parameters: any
) -> any:
    flower_url = 'http://' + parameters['address'] + ':' + parameters['port'] + '/api/tasks'
    response = requests.get(
        url = flower_url, 
        auth = HTTPBasicAuth(
            username = parameters['username'], 
            password = parameters['password']
        )
    )
    tasks = {}
    if response.status_code == 200:
        tasks = response.json()
    return tasks

def format_flower_tasks(
    tasks: any
) -> any:
    relevant_keys = [
        'worker',
        'children',
        'state',
        'received',
        'started',
        'succeeded',
        'failed',
        'result',
        'timestamp',
        'runtime',
    ]
    # This doesn't gurantee 
    # a time stamp order
    # and it doesn't 
    # specify the children names
    formatted_flower_tasks = {}
    sorted_tasks = sorted(
        tasks.values(), 
        key=lambda x: float(x['received']) if not x['received'] is None else float('-inf')
    )
    for task_info in sorted_tasks:
        if not task_info['name'] is None:
            task_id = task_info['uuid']
            task_name = task_info['name'].split('.')[-1].replace('_','-')
            used_key = ''
            if not task_name in formatted_flower_tasks:
                used_key = '1/' + task_id
                formatted_flower_tasks[task_name] = {
                    used_key: {}
                }
            else:
                new_key = len(formatted_flower_tasks[task_name]) + 1
                new_key = str(new_key)
                used_key = new_key + '/' + task_id
                formatted_flower_tasks[task_name][used_key] = {}
            
            for task_key, task_value in task_info.items():
                if task_key in relevant_keys:
                    formatted_flower_tasks[task_name][used_key][task_key] = task_value  
    return formatted_flower_tasks   