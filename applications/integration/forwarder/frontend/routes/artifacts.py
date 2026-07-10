from fastapi import APIRouter, Request

from functions.platforms.redis import get_redis_nested_dict
from functions.platforms.celery import get_signature_id

artifact_fastapi = APIRouter()

@artifact_fastapi.get("/job/{type}/{user}/{key}")
async def get_job_artifact(
    request: Request,
    type: str,
    user: str,
    key: str
):  
    request.app.state.logger.info('Requesting job ' + str(type) + ' for ' + str(user) + ' using key ' + str(key))
    # We assume that forwarders 
    # and submitters are all 
    # given a ice id.We also 
    # assume that bucket prefixes 
    # are constant

    configuration_dict = get_redis_nested_dict(
        redis_client = request.app.state.redis,
        dict_name = 'configuration'
    )   

    suitable_types = [
        'status',
        'sacct',
        'seff',
        'files'
    ]
    
    if type in suitable_types:
        task_prefix = 'tasks.fetch-job-'
        task_name = task_prefix + type

        request_dict = {
            'user': user,
            'key': key
        }
        
        task_id = get_signature_id(
            task_name = task_name,
            task_kwargs = {
                'configuration': configuration_dict,
                'request': request_dict
            }
        )

        request.app.state.logger.info('Job artifact fetching requested')
    return {"id": task_id} 

@artifact_fastapi.get("/forwarding/{type}/{user}/{key}")
async def get_forwarding_artifact(
    request: Request,
    type: str,
    user: str,
    key: str
):  
    request.app.state.logger.info('Requesting forwarding ' + str(type) + ' for ' + str(user) + ' using key ' + str(key))
    # We assume that forwarders 
    # and submitters are all 
    # given a ice id. We also 
    # assume that bucket 
    # prefixes are constant

    configuration_dict = get_redis_nested_dict(
        redis_client = request.app.state.redis,
        dict_name = 'configuration'
    )   

    suitable_types = [
        'status-imports'
    ]

    if type in suitable_types:
        type_split = type.split('-')

        task_prefix = 'tasks.fetch-forwarding-'
        task_name = task_prefix + type_split[0]

        request_dict = {
            'forwarding-type': type_split[1],
            'user': user,
            'key': key
        }
        
        task_id = get_signature_id(
            task_name = task_name,
            task_kwargs = {
                'configuration': configuration_dict,
                'request': request_dict
            }
        )

        request.app.state.logger.info('Forwarding artifact fetching requested')
    return {"id": task_id}