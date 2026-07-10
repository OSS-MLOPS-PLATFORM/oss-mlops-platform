from functions.utility.storage.objects import get_object
from functions.platforms.venv import check_missing_packages

def check_enviroment( 
    enviroment_data: any,
    job_data: any
) -> bool:
    missing_configuration = {}

    enviroment_properties = enviroment_data['properties']
    
    default_directory = enviroment_properties['default-directory']
    path_split = default_directory.split('/')

    if not 3 == len(path_split):
        missing_configuration['directory'] = 'Directory lacks paths'
    
    if not path_split[1] == 'users':
        missing_configuration['directory'] = 'Directory is not home'
        
    python_version = enviroment_properties['python-version']
    major = int(python_version[0])
    minor = int(python_version[1])

    if not 3 <= major and not 6 <= minor:
        missing_configuration['python'] = 'Python version is too old'

    # add later module check
    job_enviroment = job_data['enviroment']

    job_venv = job_enviroment['venv']
    venv_name = job_venv['name']
    
    venv_modules = job_venv['configuration-modules']
    venv_packages = job_venv['packages']
    
    enviroment_status = enviroment_data['status']
    workspace = enviroment_status['current-workspace']

    provided_files = job_data['files']['provide']
    missing_files = []
    for file_info in provided_files:
        if file_info['overwrite']:
            missing_files.append(file_info)
            continue
        target_file_split = file_info['target'].split('/')
        if target_file_split[0] == 'hpc':
            if target_file_split[1] == 'mahti':
                directory_files = workspace[target_file_split[2]][target_file_split[3]]['files']
                file_exists = False
                for file in directory_files:
                    if file == target_file_split[-1]:
                        file_exists = True
                        break
                if not file_exists:
                    missing_files.append(file_info) 

    if not len(missing_files) == 0:
        missing_configuration['files'] = missing_files

    # Refactor later for 
    # appl and scratch
    venv_directory = job_venv['directory']
    user = path_split[-1]

    used_directory_venvs = workspace[venv_directory][user]['venvs']
    
    venv_exists = False
    for name, configuration in used_directory_venvs.items():
        if venv_name == name:
            venv_exists = True
            used_venv_modules = configuration['configuration-modules']
            
            missing_modules = []
            for module in venv_modules:
                if not module in used_venv_modules:
                    missing_modules.append(module)
            
            if not len(missing_modules) == 0:
                missing_configuration['venv-modules'] = missing_modules
                
            used_venv_packages = configuration['packages']
            missing_packages = check_missing_packages(
                installed_packages = used_venv_packages,
                wanted_packages = venv_packages
            )
            
            if not len(missing_packages) == 0:
                missing_configuration['venv-packages'] = {
                    'name': venv_name,
                    'configuration-modules': venv_modules,
                    'packages': missing_packages
                }
            break
    
    if not venv_exists:
        missing_configuration['venv'] = {
            'name': venv_name,
            'configuration-modules': venv_modules,
            'packages': venv_packages
        }

    return missing_configuration

def format_enviroment_data(
    storage_client: any,
    storage_name: str,
    enviroment: str,
    platform: str
) -> any:
    enviroment_properties_name = platform + '-properties' 
    enviroment_properties = get_object(
        storage_client = storage_client,
        bucket_name = storage_name,
        object_name = enviroment,
        path_replacers = {
            'name': enviroment_properties_name
        },
        path_names = []
    )

    enviroment_status_name = platform + '-status' 
    enviroment_status = get_object(
        storage_client = storage_client,
        bucket_name = storage_name,
        object_name = enviroment,
        path_replacers = {
            'name': enviroment_status_name
        },
        path_names = []
    )

    enviroment_data = {
        'properties': enviroment_properties['data'],
        'status': enviroment_status['data']
    }
    return enviroment_data