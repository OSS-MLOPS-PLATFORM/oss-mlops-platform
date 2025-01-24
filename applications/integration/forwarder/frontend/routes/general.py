from fastapi import APIRouter, Request

from functions.platforms.logger import get_logs
from functions.platforms.celery import wait_signature_result

general_fastapi = APIRouter()

@general_fastapi.post("/demo")  
async def demo(
    request: Request
):  
    request.app.state.logger.info('Demo')
    return {"status": 'demo'}

@general_fastapi.get("/logs/{component}")
async def fetch_logs(
    request: Request,
    component: str
):
    # Exception due to 
    # debugging and low priority
    request.app.state.logger.info('Requesting logs from ' + str(component))
    logs = {}
    if component == 'frontend':
        logs = get_logs(
            log_path = request.app.state.log_path
        )
        request.app.state.logger.info('Frontend logs received')
    if component == 'backend': 
        task_data = wait_signature_result(
            celery_client = request.app.state.celery,
            task_name = 'tasks.get-logs',
            task_kwargs = {},
            timeout = 10
        )
        if task_data['status'] == 'SUCCESS':
            logs = task_data['result']
            request.app.state.logger.info('Backend logs received')
    return logs

@general_fastapi.get("/structure")
async def fetch_structure(
    request: Request
):
    # Exception due to 
    # debugging and low priority
    request.app.state.logger.info('Fetching cluster structure')
    
    structure = {}
    task_data = wait_signature_result(
        celery_client = request.app.state.celery,
        task_name = 'tasks.get-structure',
        task_kwargs = {},
        timeout = 20
    )
    if task_data['status'] == 'SUCCESS':
        structure = task_data['result']
        request.app.state.logger.info('Backend logs received')
    return structure