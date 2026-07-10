from fastapi import APIRouter, Request

from functions.utility.apis.configuration import Configuration
from functions.utility.apis.scheduler_request import Scheduler_Request
from functions.utility.storage.management import modify_storage_configuration

from functions.platforms.redis import store_redis_nested_dict
from functions.platforms.celery import get_signature_id

setup_fastapi = APIRouter() 
 
@setup_fastapi.post("/config")
async def configure(
    request: Request,
    config: Configuration
):  
    request.app.state.logger.info('Configuring forwarder')

    config_dict = config.model_dump(by_alias = True)

    modified_configuration = modify_storage_configuration(
        configuration = config_dict
    )

    success = store_redis_nested_dict(
        redis_client = request.app.state.redis,
        dict_name = 'configuration',
        nested_dict = modified_configuration
    )

    task_id = ''
    if success:
        task_id = get_signature_id(
            task_name = 'tasks.template-handler',
            task_kwargs = {
                'configuration': modified_configuration
            }
        ) 

        request.app.state.logger.info('Template handler requested')
 
    return  {'status': 'configuration success', 'id': task_id}

@setup_fastapi.post("/start")
async def start_scheduling(
    request: Request,
    scheduler_request: Scheduler_Request
):  
    request.app.state.logger.info('Starting forwarder scheduler')

    scheduler_dict = scheduler_request.model_dump(by_alias = True)

    task_id = get_signature_id(
        task_name = 'tasks.start-scheduler',
        task_kwargs = {
            'scheduler_request': scheduler_dict
        }
    ) 

    request.app.state.logger.info('Start scheduler requested')

    return  {'status': 'scheduler started', 'id': task_id}

@setup_fastapi.post("/stop")
async def stop_scheduling(
    request: Request
): 
    request.app.state.logger.info('Stopping forwarder scheduler')

    task_id = get_signature_id(
        task_name = 'tasks.stop-scheduler',
        task_kwargs = {}
    ) 

    request.app.state.logger.info('Stop scheduler requested')

    return  {'status': 'scheduler stopped', 'id': task_id}
