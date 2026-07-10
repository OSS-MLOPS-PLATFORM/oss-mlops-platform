from fastapi import APIRouter, Request

from functions.utility.apis.job_request import Job_Request
from functions.platforms.redis import get_redis_nested_dict
from functions.platforms.celery import get_signature_id

requests_fastapi = APIRouter()

@requests_fastapi.post("/submit/job")
async def submit_job(
    request: Request,
    job_request: Job_Request
):  
    request.app.state.logger.info('Submitting a job')
    # We assume that forwarders 
    # and submitters are all given 
    # a ice id. We also assume that 
    # bucket prefixes are constant

    job_request_dict = job_request.model_dump(by_alias = True)

    configuration_dict = get_redis_nested_dict(
        redis_client = request.app.state.redis,
        dict_name = 'configuration'
    )

    task_id = get_signature_id(
        task_name = 'tasks.create-job',
        task_kwargs = {
            'configuration': configuration_dict,
            'job_request': job_request_dict
        }
    )

    request.app.state.logger.info('Create job requested')

    return {"id": task_id}

@requests_fastapi.put("/run/job/{key}")
async def run_job(
    request: Request,
    key: str
):  
    request.app.state.logger.info('Running job with key ' + str(key))
    # We assume that forwarders 
    # and submitters are all given 
    # a ice id. We also assume that 
    # bucket prefixes are constant

    job_start_dict = {
        'key': key
    }
    
    configuration_dict = get_redis_nested_dict(
        redis_client = request.app.state.redis,
        dict_name = 'configuration'
    )

    task_id = get_signature_id(
        task_name = 'tasks.start-job',
        task_kwargs = {
            'configuration': configuration_dict,
            'job_start': job_start_dict
        }
    )

    request.app.state.logger.info('Start job requested')

    return {"id": task_id}

@requests_fastapi.put("/cancel/job/{key}")
async def cancel_job(
    request: Request,
    key: str
): 
    request.app.state.logger.info('Cancelling job with key ' + str(key))

    # Might need sanitazation
    job_cancel_dict = {
        'key': key
    }

    configuration_dict = get_redis_nested_dict(
        redis_client = request.app.state.redis,
        dict_name = 'configuration'
    )

    task_id = get_signature_id(
        task_name = 'tasks.stop-job',
        task_kwargs = {
            'configuration': configuration_dict,
            'job_cancel': job_cancel_dict
        }
    )

    request.app.state.logger.info('Stop job requested')

    return {"id": task_id}