from functions.platforms.celery import await_signature

def collect_objects(    
    celery_client: any,
    configuration: any 
): 
    task_data = await_signature(
        celery_client = celery_client,
        task_name = 'tasks.artifact-handler',
        task_kwargs ={ 
            'configuration': configuration
        },
        timeout = 500
    ) 
    return task_data['result'] 