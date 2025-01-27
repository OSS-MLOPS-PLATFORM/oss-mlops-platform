
import sys
import ray
import json

from functions.minio_os import minio_setup_client
from functions.paths import get_divided_paths
from functions.store import store_path_documents

from importlib.metadata import version 

def store_data(
    process_parameters: any,
    storage_parameters: any, 
    data_parameters: any
):
    try: 
        worker_number = process_parameters['worker-number']

        print('Creating minio client')
        object_client = minio_setup_client(
            endpoint = storage_parameters['minio-endpoint'],
            username = storage_parameters['minio-username'],
            password = storage_parameters['minio-password']
        )
        print('Minio client created')  

        print('Getting repository paths')
        
        print('Dividing paths for ' + str(worker_number) + ' workers')
        # This takes longer than the actual processing
        # No more than 100 concurrent requests are allowed
        # https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api
        # https://docs.github.com/en/rest/using-the-rest-api/best-practices-for-using-the-rest-api
        path_batches = get_divided_paths( 
            object_client = object_client,
            storage_parameters = storage_parameters,
            data_parameters = data_parameters,
            number = worker_number
        )

        print('Referencing paths')

        path_batch_refs = []
        for path_batch in path_batches:
            path_batch_refs.append(ray.put(path_batch))

        print('Storing path documents')
        task_1_refs = []
        for path_batch_ref in path_batch_refs:
            task_1_refs.append(store_path_documents.remote(
                storage_parameters = storage_parameters,
                data_parameters = data_parameters,
                path_tuples = path_batch_ref 
            ))
        
        remaining_task_1 = task_1_refs
        task_1_outputs = []
        while len(remaining_task_1):
            done_task_1_refs, remaining_task_1 = ray.wait(remaining_task_1)
            for output_ref in done_task_1_refs:   
                task_1_outputs.append(ray.get(output_ref))
        
        print('Path documents stored: ' + str(task_1_outputs))
        
        return True
    except Exception as e:
        print('Fetch and store error')
        print(e)
        return False

if __name__ == "__main__":
    print('Starting ray job')
    print('Python version is:' + str(sys.version))
    print('Ray version is:' + version('Ray'))
    print('PyGithub version is:' + version('PyGithub'))
    print('PyMongo version is:' + version('PyMongo'))
    print('Markdown version is:' + version('Markdown'))
    print('Tree-sitter version is:' + version('tree-sitter'))
    print('Tree-sitter-python version is:' + version('tree-sitter-python'))
    print('BeautifulSoup version is:' + version('beautifulsoup4'))
    print('NBformat version is:' + version('nbformat'))
    
    input = json.loads(sys.argv[1])

    process_parameters = input['process-parameters']
    storage_parameters = input['storage-parameters']
    data_parameters = input['data-parameters']

    print('Running store data')

    store_data_status = store_data(
        process_parameters = process_parameters,
        storage_parameters = storage_parameters,
        data_parameters = data_parameters
    )
    
    print('Store data success:' + str(store_data_status))

    print('Ray job Complete')
