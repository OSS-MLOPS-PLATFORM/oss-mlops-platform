# Created and works
def setup_celery_app():
    from functions.platforms.celery import setup_celery_logging, get_celery_instance
    
    celery_logs = setup_celery_logging()
        
    celery_app = get_celery_instance()

    from tasks.parts.frontend.general import get_logs
    celery_app.task(get_logs)

    from tasks.parts.mixed.enviroment import enviroment_handler  
    celery_app.task(enviroment_handler)

    from tasks.parts.frontend.templates import template_handler
    celery_app.task(template_handler)

    from tasks.parts.frontend.configuration import setup_handler
    celery_app.task(setup_handler)

    from tasks.parts.frontend.requests import create_job, start_job, stop_job
    celery_app.task(create_job) 
    celery_app.task(start_job)
    celery_app.task(stop_job) 

    from tasks.parts.frontend.artifacts import fetch_job_status, fetch_job_sacct, fetch_job_seff, fetch_job_files
    celery_app.task(fetch_job_status)
    celery_app.task(fetch_job_sacct) 
    celery_app.task(fetch_job_seff)
    celery_app.task(fetch_job_files) 

    from tasks.scheduled.configuration import configuration_manager
    celery_app.task(configuration_manager) 

    from tasks.parts.subtasks.jobs import job_handler
    celery_app.task(job_handler) 

    from tasks.parts.subtasks.artifacts import artifact_handler
    celery_app.task(artifact_handler)
    
    from tasks.scheduled.monitoring import monitoring_manager
    celery_app.task(monitoring_manager) 

    from tasks.scheduled.collection import collection_manager
    celery_app.task(collection_manager)

    from tasks.scheduled.logging import logging_manager
    celery_app.task(logging_manager)

    return celery_app, celery_logs