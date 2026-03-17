import os
import warnings

# Make run with Python3 run_celery.py
warnings.filterwarnings("ignore") 
if __name__ == '__main__': 
    #os.environ['REDIS_ENDPOINT'] = '127.0.0.1'
    #os.environ['REDIS_PORT'] = '6379'
    #os.environ['REDIS_DB'] = '0'

    #os.environ['CELERY_CONCURRENCY'] = '8'
    #os.environ['CELERY_LOGLEVEL'] = 'warning'
    
    #os.environ['FLOWER_ENDPOINT'] = '127.0.0.1'
    #os.environ['FLOWER_PORT'] = '6601'
    #os.environ['FLOWER_USERNAME'] = 'flower123'
    #os.environ['FLOWER_PASSWORD'] = 'flower456'

    from setup_celery import setup_celery_app
    
    celery_concurrency = '--concurrency='
    celery_loglevel = '--loglevel='
    celery_logfile = '--logfile='
    
    used_concurrency = celery_concurrency + os.environ.get('CELERY_CONCURRENCY')
    used_loglevel = celery_loglevel + os.environ.get('CELERY_LOGLEVEL')
    
    celery, log_path = setup_celery_app()

    used_logpath = celery_logfile + log_path
    
    celery.worker_main(
        argv = [
            'worker', 
            used_concurrency, 
            used_loglevel, 
            used_logpath
        ]
    )
    