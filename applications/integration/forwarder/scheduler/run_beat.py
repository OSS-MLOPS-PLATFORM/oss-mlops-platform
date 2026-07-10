import os
import warnings
# Make run with Python3 run_celery.py
warnings.filterwarnings("ignore")
if __name__ == '__main__':
    #os.environ['REDIS_ENDPOINT'] = '127.0.0.1'
    #os.environ['REDIS_PORT'] = '6379'
    #os.environ['REDIS_DB'] = '0'

    #os.environ['SCHEDULER_TIMES'] = '50|165|230'

    from setup_beat import setup_beat_app
    
    beat = setup_beat_app()
    beat.Beat(loglevel='warning').run()