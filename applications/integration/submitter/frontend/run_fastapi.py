import os
import uvicorn
import warnings 
# Make run with Python3 run_fastapi.py
warnings.filterwarnings("ignore")
if __name__ == "__main__":
    #os.environ['REDIS_ENDPOINT'] = '127.0.0.1'
    #os.environ['REDIS_PORT'] = '6379'
    #os.environ['REDIS_DB'] = '0'
 
    from setup_fastapi import setup_fastapi_app

    fastapi = setup_fastapi_app()
    uvicorn.run(
        app = fastapi, 
        host = '0.0.0.0', 
        port = 6600
    )
