import sys
import ray
import json
import requests

from importlib.metadata import version

def check_clusters(
    cluster_urls: any
) -> any:
    try:
        url_prefix = 'http://'
        resource_prefix = '/api/cluster/resources'
        for cluster_url in cluster_urls:
            #print(cluster_url)
            request_url = url_prefix + cluster_url + resource_prefix
            print(request_url)
            resp = requests.get(
                url = request_url,
                timeout = 5
            )
            data = resp.json()
            total = data.get('total', {})
            available = data.get('available', {})
            print(total)
            print(available)
        return True
    except Exception as e:
        print('Request error')
        print(e)
        return False 

def cluster_orhestrator(
    process_parameters: any,
    storage_parameters: any,
    data_parameters: any
):
    try:
        status = check_clusters(
            cluster_urls = process_parameters['cluster-urls']
        )
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
