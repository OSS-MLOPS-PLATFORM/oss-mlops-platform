import json
import os

def check_secrets(
    secrets: any
) -> bool:
    valid_prefixes = [
        'CLOUD',
        'STORAGE',
        'HPC',
        'INTEGRATION'
    ]

    prefix_separations = [
        0,
        0,
        0,
        0
    ]
    
    for key, value in secrets.items():
        key_split = key.split('_')
        if not key_split[0] in valid_prefixes:
            # Put logging
            return False
        case = 0
        for prefix in valid_prefixes:
            if prefix == key_split[0]:
                value_separations = value.split('|')
                if prefix_separations[case] == 0:
                    prefix_separations[case] = len(value_separations)
                    break
                if not len(value_separations) == prefix_separations[case]:
                    # Put logging
                    return False
            case += 1
    return True

def create_secret_dict(
    secrets: any
) -> any: 
    valid_prefixes = [
        'CLOUD',
        'STORAGE',
        'HPC',
        'INTEGRATION'
    ]
    
    valid_root = [
        'ENVIROMENT'
    ]

    valid_values = [
        'USER',
        'ADDRESS',
        'KEY',
        'PASSWORD'
    ]

    secret_dict = {}
    for key, value in secrets.items():
        key_split = key.split('_')
        if key_split[0] in valid_prefixes:
            if key_split[-1] in valid_root:
                secret_dict[key_split[0].lower()] = {}
                value_split = value.split('|')
                for value in value_split:
                    secret_dict[key_split[0].lower()][value] = {}
                continue
            if key_split[-1] in valid_values:
                value_split = value.split('|')
                i = 0
                for enviroment in secret_dict[key_split[0].lower()].keys():
                    secret_dict[key_split[0].lower()][enviroment][key_split[-1].lower()] = value_split[i]
                    i += 1
    return secret_dict

def get_secret_dict(
    secrets_path: str
):
    secret_metadata = {}
    with open(secrets_path, 'r') as f:
        fetched_metadata = json.load(f)
    
        correct_format = check_secrets(
            secrets = fetched_metadata
        )

        if correct_format:
            secret_metadata = create_secret_dict(
                secrets = fetched_metadata
            )
    return secret_metadata

def create_file(
    file_name: str,
    file_data: any
) -> str:
    directory = 'files'
    file_path = directory + '/' + file_name
    os.makedirs(directory, exist_ok=True)
    with open(file_path, 'w') as f:
        f.write(file_data)
    return file_path

def get_stored_file_path(
    file_name: str
) -> str:
    directory = 'files'
    file_path = directory + '/' + file_name
    return file_path

def get_file_data(
    file_name: str
) -> any:
    directory = 'files'
    file_path = directory + '/' + file_name
    os.makedirs(directory, exist_ok=True)
    file_data = None
    with open(file_path, 'w') as f:
        file_data = f.read()
    return file_data