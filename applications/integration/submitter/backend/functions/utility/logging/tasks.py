from functions.platforms.flower import get_flower_tasks, format_flower_tasks, get_flower_parameters
from functions.utility.storage.objects import get_object, set_object
from functions.utility.storage.metadata import general_object_metadata

def get_tasks(
    parameters: any
):
    tasks = get_flower_tasks(
        parameters = parameters 
    )
    formatted_tasks = None
    if 0 < len(tasks):
        formatted_tasks = format_flower_tasks(
            tasks = tasks
        )
    return formatted_tasks

def store_tasks(
    storage_client: any,
    storage_name: str
):
    flower_parameters = get_flower_parameters()

    tasks = get_tasks(
        parameters = flower_parameters
    )
    
    for task_name, task_cases in tasks.items(): 
        task_object = get_object(
            storage_client = storage_client,
            bucket_name = storage_name,
            object_name = 'tasks',
            path_replacers = {
                'name': task_name
            },
            path_names = []
        )
        task_data = {}
        task_metadata = {}
        if task_object is None:
            task_data = task_cases
            task_metadata = general_object_metadata()
        else:
            # There are tasks 
            # such as 
            # collection manager
            # that require 
            # updating due to 
            # running at the same
            task_data = task_object['data']
            task_metadata = task_object['custom-meta']

            existing_keys = list(task_data.keys())
            
            existing_uuids = []
            for case_name in existing_keys:
                existing_uuids.append(case_name.split('/')[-1])
            
            new_keys = list(task_cases.keys())
            
            unseen_keys = []
            seen_keys = []
            for key in new_keys:
                new_uuid = key.split('/')[-1]
                if new_uuid in existing_uuids:
                    seen_keys.append(key)
                    continue
                unseen_keys.append(key)

            highest_id = 0
            for key in existing_keys:
                existing_id = int(key.split('/')[0])
                if highest_id < existing_id:
                    highest_id = existing_id
            # Add new keys
            for unseen_key in unseen_keys: 
                new_id = highest_id + 1
                new_uuid = unseen_key.split('/')[-1]
                new_key = str(new_id) + '/' + new_uuid
                task_data[new_key] = tasks[task_name][unseen_key]
            
            # Update existing keys
            modified_keys = list(task_data.keys())
            for current_key in modified_keys:
                current_uuid = current_key.split('/')[-1]
                for seen_key in seen_keys:
                    seen_uuid = seen_key.split('/')[-1]
                    if current_uuid == seen_uuid:
                        task_data[current_key] = tasks[task_name][seen_key]
                        
            task_metadata['version'] = task_metadata['version'] + 1

        set_object(
            storage_client = storage_client,
            bucket_name = storage_name,
            object_name = 'tasks',
            path_replacers = {
                'name': task_name
            },
            path_names = [],
            overwrite = True,
            object_data = task_data,
            object_metadata = task_metadata
        )