from fastapi import APIRouter, Request

from functions.utility.apis.configuration import Configuration
from functions.utility.storage.management import modify_storage_configuration

from functions.platforms.redis import store_redis_nested_dict
from functions.platforms.celery import get_signature_id

setup_fastapi = APIRouter()

@setup_fastapi.post("/config")
async def configure(
    request: Request,
    config: Configuration
):   
    request.app.state.logger.info('Configuring frontend')
      
    config_dict = config.model_dump(by_alias = True)

    modified_configuration = modify_storage_configuration(
        configuration = config_dict
    )

    success = store_redis_nested_dict(
        redis_client = request.app.state.redis,
        dict_name = 'configuration',
        nested_dict = modified_configuration
    )

    request.app.state.logger.info('Configuration added to redis: ' + str(success))
    
    task_id = ''
    if success:
        task_id = get_signature_id(
            task_name = 'tasks.setup-handler',
            task_kwargs = {
                'configuration': modified_configuration
            }
        )
        
        request.app.state.logger.info('Setup handler requested')
    return  {'id': task_id}