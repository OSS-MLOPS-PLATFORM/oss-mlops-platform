import os

from paramiko import RSAKey, Ed25519Key
from fabric import Connection

def get_ssh_parameters(
    platform_secrets: any
) -> any:
    try:
        platform_host = platform_secrets['address']
        platform_user = platform_secrets['user']
        file_path = platform_secrets['key']
        if '~' in file_path:
            file_path = os.path.expanduser(file_path)
        private_key_file = file_path
        private_key_password = platform_secrets['password']

        private_key = None
        try:
            private_key = Ed25519Key.from_private_key_file(
                filename = private_key_file, 
                password = private_key_password
            )
        except Exception as e:
            pass  

        try:  
            private_key = RSAKey.from_private_key_file(
                filename = private_key_file, 
                password = private_key_password
            )
        except Exception as e:
            pass

        connect_parameters = {
            'host': platform_host,
            'user': platform_user,
            'kwargs': {
                'pkey': private_key
            }
        }
        return connect_parameters
    except Exception as e:
        print('Get SSH parameters error: ' + str(e))
        return {}

def run_remote_commands(
    platform_secrets: any,
    commands: any
) -> any:
    connection_parameters = get_ssh_parameters(
        platform_secrets = platform_secrets
    )
    
    if 0 < len(connection_parameters):
        print('Attempting to run commands over ssh')
        try: 
            run_results = []
            with Connection(
                host = connection_parameters['host'],
                user = connection_parameters['user'],
                connect_kwargs = connection_parameters['kwargs']
            ) as c:
                for command in commands:
                    result = c.run(
                        command, 
                        hide = True
                    )
                    if result.ok:
                        run_results.append(result.stdout)
            return run_results 
        except Exception as e:
            print('Run remote commands error: ' + str(e))
            return []
    return []

def upload_file(
    platform_secrets: any,
    absolute_local_path: str,
    absolute_remote_path: str
) -> bool:  
    connection_parameters = get_ssh_parameters(
        platform_secrets = platform_secrets
    )

    if 0 < len(connection_parameters):
        print('Uploading file over ssh')
        try:
            with Connection(
                host = connection_parameters['host'],
                user = connection_parameters['user'],
                connect_kwargs = connection_parameters['kwargs']
            ) as c:
                c.put(
                    local = absolute_local_path, 
                    remote = absolute_remote_path
                )
            return True
        except Exception as e:
            print('Upload file error: ' + str(e))
            return False
    return False

def download_file(
    platform_secrets: any,
    absolute_remote_path: str,
    absolute_local_path: str
) -> bool: 
    connection_parameters = get_ssh_parameters(
        platform_secrets = platform_secrets
    )

    if 0 < len(connection_parameters):
        print('Downloading file over ssh')
        try:
            with Connection(
                host = connection_parameters['host'],
                user = connection_parameters['user'],
                connect_kwargs = connection_parameters['kwargs']
            ) as c:
                c.get(
                    remote = absolute_remote_path,
                    local = absolute_local_path
                )   
            return True
        except Exception as e:
            print('Download file error: ' + str(e))
            return False
    return False