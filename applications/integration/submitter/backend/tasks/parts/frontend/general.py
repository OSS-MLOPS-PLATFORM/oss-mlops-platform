from functions.platforms.celery import get_celery_instance, get_celery_logs

tasks_celery = get_celery_instance()

@tasks_celery.task( 
    bind = False, 
    max_retries = 0,
    soft_time_limit = 120,
    time_limit = 240,
    rate_limit = '1/m',
    name = 'tasks.get-logs'
)
def get_logs() -> any:
    # Doesn't need lock, 
    # since fetching data
    try:
        print('Sending logs to frontend')
        return get_celery_logs()
    except Exception as e:
        print('Get logs error: ' + str(e))
        return {'logs':[]} 