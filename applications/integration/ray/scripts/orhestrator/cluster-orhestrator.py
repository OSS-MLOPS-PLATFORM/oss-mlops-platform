import sys
import json

from importlib.metadata import version

from functions.resources import check_clusters

def cluster_orhestrator(
    process_parameters: any,
    storage_parameters: any,
    data_parameters: any
):
    try:
        collective_resources = check_clusters(
            cluster_urls = process_parameters['cluster-urls']
        )
        print(collective_resources)
        return True
    except Exception as e:
        print('Orhestrator error')
        print(e)
        return False 

if __name__ == "__main__":
    print('Starting ray job')
    print('Python version is:' + str(sys.version))
    print('Ray version is:' + version('ray'))
    
    input = json.loads(sys.argv[1])

    process_parameters = input['process-parameters']
    storage_parameters = input['storage-parameters']
    data_parameters = input['data-parameters']

    print('Running orhestrator')

    job_1_status = cluster_orhestrator(
        process_parameters = process_parameters,
        storage_parameters = storage_parameters,
        data_parameters = data_parameters
    )
    
    print('Orchestrator success:' + str(job_1_status))

    print('Ray job Complete')
