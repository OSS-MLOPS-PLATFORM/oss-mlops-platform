from fastapi import APIRouter, Request

from functions.platforms.redis import get_redis_nested_dict
from functions.platforms.celery import get_task, get_signature_id

tasks_fastapi = APIRouter()

@tasks_fastapi.put("/request/{task_signature}")
async def request_task(
    request: Request,
    task_signature: str
):
    request.app.state.logger.info('Requesting task ' + str(task_signature))
    
    configuration_dict = get_redis_nested_dict(
        redis_client = request.app.state.redis,
        dict_name = 'configuration'
    )

    task_id = get_signature_id(
        task_name = task_signature,
        task_kwargs = {
            'configuration': configuration_dict
        }
    )
    
    return {"id": task_id}

@tasks_fastapi.get("/result/{task_id}")
async def get_task_result(
    request: Request,
    task_id: str
):
    request.app.state.logger.info('Fetching task data with id ' + str(task_id))
    
    task_data = get_task( 
        celery_client = request.app.state.celery,
        task_id = task_id
    )

    return task_data
