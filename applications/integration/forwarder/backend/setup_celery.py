def setup_celery_app():
    from functions.platforms.celery import setup_celery_logging, get_celery_instance
    
    celery_logs = setup_celery_logging()
        
    celery_app = get_celery_instance()

    from functions.platforms.prometheus import create_prometheus_server

    create_prometheus_server() 

    from tasks.parts.frontend.general import get_logs, get_structure
    celery_app.task(get_logs)
    celery_app.task(get_structure)

    from tasks.parts.frontend.scheduler import start_scheduler, stop_scheduler
    celery_app.task(start_scheduler)
    celery_app.task(stop_scheduler)

    from tasks.parts.frontend.templates import template_handler
    celery_app.task(template_handler)

    from tasks.parts.frontend.requests import create_job, start_job, stop_job, create_forwarding, stop_forwarding
    celery_app.task(create_job)
    celery_app.task(start_job)
    celery_app.task(stop_job)
    celery_app.task(create_forwarding)
    celery_app.task(stop_forwarding)
    
    from tasks.parts.frontend.artifacts import fetch_job_status, fetch_job_sacct, fetch_job_seff, fetch_job_files
    celery_app.task(fetch_job_status)
    celery_app.task(fetch_job_sacct)
    celery_app.task(fetch_job_seff)
    celery_app.task(fetch_job_files)

    from tasks.parts.subtasks.artifacts import sacct_collector, seff_collector
    celery_app.task(sacct_collector)
    celery_app.task(seff_collector)

    from tasks.parts.subtasks.times import job_time_collector, pipeline_time_collector, task_time_collector
    celery_app.task(job_time_collector)
    celery_app.task(task_time_collector)
    celery_app.task(pipeline_time_collector)
    
    from tasks.scheduled.forwarding import forwarding_manager
    celery_app.task(forwarding_manager)

    from tasks.scheduled.collection import collection_manager
    celery_app.task(collection_manager)

    from tasks.scheduled.logging import logging_manager
    celery_app.task(logging_manager)

    return celery_app, celery_logs