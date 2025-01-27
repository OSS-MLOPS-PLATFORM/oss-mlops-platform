
from functions.pygithub import pygithub_get_repo_paths
from functions.utility import get_checked, store_checked

def round_robin_division(
    target_list: any, 
    number: int
) -> any:
    lists = [[] for _ in range(number)]
    i = 0
    sorted_list = sorted(target_list, key = lambda x: (x[-2], x[-1]))
    for elem in sorted_list:
        lists[i].append(elem)
        i = (i + 1) % number
    return lists

def get_divided_paths(
    object_client: any,
    storage_parameters: any,
    data_parameters: any,
    number: int
) -> any:
    print('Fetching paths') 

    repository_paths = get_checked(
        object_client = object_client,
        storage_parameters = storage_parameters,
        prefix = storage_parameters['fetch-path-prefix']
    )

    replace = data_parameters['replace']
    if 0 == len(repository_paths) or replace == 'true':
        print('Getting github paths')

        github_token = data_parameters['github-token']
        repository_owner = data_parameters['repository-owner']
        repository_name = data_parameters['repository-name']

        repository_paths = pygithub_get_repo_paths(
            token = github_token,
            owner = repository_owner, 
            name = repository_name 
        ) 

        print('Storing paths')

        store_checked(
            object_client = object_client,
            storage_parameters = storage_parameters,
            prefix = storage_parameters['fetch-path-prefix'],
            checked = repository_paths
        )

        print('Paths stored') 
    
    print('Filtering paths')
    type_priority = data_parameters['document-type-priority']
    relevant_files = data_parameters['relevant-files']
    path_tuples = []
    for path in repository_paths:
        path_split = path.split('/')
        file_end = path_split[-1].split('.')[-1].rstrip()
        if file_end in relevant_files:
            path_priority = type_priority[file_end]
            path_length = len(path_split)
            tuple = (path.rstrip(), path_priority, path_length)
            path_tuples.append(tuple)
            
    print('Amount of paths: ' + str(len(path_tuples)))

    return round_robin_division(
        target_list = path_tuples,
        number = number
    )