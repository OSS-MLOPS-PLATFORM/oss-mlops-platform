from fastapi import FastAPI

import redis
import os

def setup_fastapi_app():
    from functions.platforms.logger import initilized_logger
    log_path = 'logs/frontend.log'
    logger = initilized_logger(
        log_path = log_path,
        logger_name = 'forwader-frontend'
    )

    logger.info('Creating FastAPI instance')

    fastapi_app = FastAPI()

    fastapi_app.state.log_path = log_path
    fastapi_app.state.logger = logger

    fastapi_app.state.logger.info('FastAPI created')

    fastapi_app.state.logger.info('Connecting to redis')

    fastapi_app.state.redis = redis.Redis(
        host = os.environ.get('REDIS_ENDPOINT'), 
        port = os.environ.get('REDIS_PORT'), 
        db = os.environ.get('REDIS_DB')
    )

    fastapi_app.state.logger.info('Redis connected')

    fastapi_app.state.logger.info('Defining Celery client')

    from functions.platforms.celery import get_celery_instance

    # Defining required 
    # by the used signatures
    fastapi_app.state.celery = get_celery_instance()

    fastapi_app.state.logger.info('Celery client defined')

    fastapi_app.state.logger.info('Importing routes')

    from routes.general import general_fastapi
    from routes.setup import setup_fastapi
    from routes.requests import requests_fastapi
    from routes.tasks import tasks_fastapi
    from routes.artifacts import artifact_fastapi
    
    fastapi_app.state.logger.info('Including routers')
    
    fastapi_app.include_router(general_fastapi, prefix='/general')
    fastapi_app.include_router(setup_fastapi, prefix = '/setup')
    fastapi_app.include_router(requests_fastapi, prefix = '/requests')
    fastapi_app.include_router(tasks_fastapi, prefix = '/tasks')
    fastapi_app.include_router(artifact_fastapi, prefix = '/artifacts')
    
    fastapi_app.state.logger.info('Routes implemented')
    
    fastapi_app.state.logger.info('Frontend ready')
    return fastapi_app