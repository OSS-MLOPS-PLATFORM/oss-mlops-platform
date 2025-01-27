

import ray

from functions.mongo_db import mongo_setup_client
from functions.pygithub import pygithub_get_repo_contents
from functions.mongo_db import mongo_check_collection, mongo_create_document
from functions.create import create_markdown_documents, create_python_documents, create_notebook_documents, create_yaml_documents
from functions.utility import divide_list, get_path_database_and_collection

def store_documents(
    mongo_client: any,
    database: str,
    collection: str, 
    path: str,
    content: any
):
    path_split = path.split('/')
    path_type = path_split[-1].split('.')[-1]
    
    path_documents = {}
    if path_type == 'md':
        try:
            path_documents = create_markdown_documents(
                markdown_text = content
            )
        except Exception as e:
            print('Create markdown document error with path: ' + str(path))
            print(e)

    if path_type == 'yaml':
        try:
            path_documents = create_yaml_documents(
                yaml_text = content
            )
        except Exception as e: 
            print('Create yaml document error with path: ' + str(path))
            print(e)

    if path_type == 'py':
        try:
            path_documents = create_python_documents(
                python_text = content
            )
        except Exception as e:
            print('Create python document error with path: ' + str(path))
            print(e)

    if path_type == 'ipynb':
        try:
            path_documents = create_notebook_documents(
                notebook_text = content
            )
        except Exception as e:
            print('Create notebook document error with path: ' + str(path))
            print(e)
    
    if 0 < len(path_documents):
        for doc_type, docs in path_documents.items():
            for document in docs:
                result = mongo_create_document(
                    mongo_client = mongo_client,
                    database_name = database,
                    collection_name = collection,
                    document = document
                )
        return True
    return False

@ray.remote(
    num_cpus = 1,
    memory = 5 * 1024 * 1024 * 1024
)
def store_path_documents(
    storage_parameters: any,
    data_parameters: any,
    path_tuples: any
) -> bool:
    amount_of_paths = len(path_tuples)
    print('Storing documents of ' + str(amount_of_paths) + ' paths')
    document_client = mongo_setup_client(
        username = storage_parameters['mongo-username'],
        password = storage_parameters['mongo-password'],
        address = storage_parameters['mongo-address'],
        port = storage_parameters['mongo-port']
    )

    github_token = data_parameters['github-token']
    repository_owner = data_parameters['repository-owner']
    repository_name = data_parameters['repository-name']
    batch_size = data_parameters['batch-size'] 

    path_batches = divide_list(
        target_list = path_tuples,
        number = batch_size
    ) 

    stored_amount = 0
    batch_index = 0
    amount_of_batches = len(path_batches)
    for path_batch in path_batches:
        print('Batches processed: ' + str(batch_index) + '/' + str(amount_of_batches))
        new_paths = []
        for path_tuple in path_batch:
            path = path_tuple[0]

            database, collection = get_path_database_and_collection(
                repository_owner = repository_owner,
                repository_name = repository_name,
                path = path
            )
            
            collection_exists = mongo_check_collection(
                mongo_client = document_client, 
                database_name = database, 
                collection_name = collection
            )

            if not collection_exists:
                new_paths.append(path)
        
        print('New paths: ' + str(len(new_paths)))
        if 0 < len(new_paths):
            contents = []
            try:
                contents = pygithub_get_repo_contents( 
                    token = github_token,
                    owner = repository_owner, 
                    name = repository_name, 
                    paths = new_paths
                )
            except Exception as e:
                print('PyGithub error')
                print(e)

            if 0 < len(contents):
                contents_index = 0
                for path in new_paths:
                    content = contents[contents_index]

                    if not content is None:
                        database, collection = get_path_database_and_collection(
                            repository_owner = repository_owner,
                            repository_name = repository_name,
                            path = path
                        )

                        stored = store_documents(
                            mongo_client = document_client,
                            database = database,
                            collection = collection,
                            path = path,
                            content = content
                        )

                        if stored:
                            stored_amount += 1

                    contents_index += 1
        batch_index += 1
    return stored_amount
