import os
import warnings

# Make run with Python3 run_flower.py
warnings.filterwarnings("ignore")
if __name__ == '__main__': 
    #os.environ['REDIS_ENDPOINT'] = '127.0.0.1'
    #os.environ['REDIS_PORT'] = '6379'
    #os.environ['REDIS_DB'] = '0'

    #os.environ['FLOWER_USERNAME'] = 'flower123'
    #os.environ['FLOWER_PASSWORD'] = 'flower456'
    
    endpoint = '0.0.0.0'
    port = '6501'

    from setup_flower import setup_flower_app
    flower = setup_flower_app()
    used_address = '--address=' + endpoint
    used_port = '--port=' + port
    basic_authentication = '--basic_auth=' + os.environ.get('FLOWER_USERNAME') + ':' + os.environ.get('FLOWER_PASSWORD')
    flower.start(argv = ['flower', used_address, used_port, basic_authentication])