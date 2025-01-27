

import sys
import ray
import json

from functions.qdrant_vb import qdrant_setup_client
from functions.mongo_db import mongo_setup_client
from functions.minio_os import minio_setup_client

from functions.documents import get_divided_collections

from functions.embeddings import store_embeddings
from functions.keywords import store_keywords
from functions.utility import get_checked, store_checked, remove_duplicate_vectors

from importlib.metadata import version

from actors.generator import Generator

def preprocess_data(
    process_parameters: any,
    storage_parameters: any,
    data_parameters: any
):
    try:
        print('Creating mongo client')
        document_client = mongo_setup_client(
            username = storage_parameters['mongo-username'],
            password = storage_parameters['mongo-password'],
            address = storage_parameters['mongo-address'],
            port = storage_parameters['mongo-port']
        )
        print('Mongo client created')

        print('Creating minio client')
        object_client = minio_setup_client(
            endpoint = storage_parameters['minio-endpoint'],
            username = storage_parameters['minio-username'],
            password = storage_parameters['minio-password']
        )
        print('Minio client created') 

        print('Creating qdrant client')
        vector_client = qdrant_setup_client(
            api_key = storage_parameters['qdrant-key'],
            address = storage_parameters['qdrant-address'], 
            port = storage_parameters['qdrant-port']
        )
        print('Qdrant client created')

        actor_number = process_parameters['actor-number']
        
        print('Creating ' + str(actor_number) + ' generator actors')
        
        actor_refs = []
        for i in range(0, actor_number):
            actor_refs.append(Generator.remote(
                embedding_model = process_parameters['embedding-model'],
                keyword_model = process_parameters['keyword-model']
            ))

        worker_number = process_parameters['worker-number']

        print('Getting stored documents')
        print('Dividing documents for ' + str(worker_number) + ' workers')
 
        collection_batches = get_divided_collections(
            document_client = document_client,
            data_parameters = data_parameters,
            number = worker_number 
        )
        
        print('Referencing documents')
        collection_batch_refs = []
        for collection_batch in collection_batches:
            collection_batch_refs.append(ray.put(collection_batch))

        print('Getting data')
        vector_identities = get_checked(
            object_client = object_client,
            storage_parameters = storage_parameters,
            prefix = storage_parameters['vector-identity-prefix']
        )
        search_identities = get_checked(
            object_client = object_client,
            storage_parameters = storage_parameters,
            prefix = storage_parameters['search-identity-prefix']
        )

        print('Referencing data')
        vector_identity_ref = ray.put(vector_identities)
        search_identity_ref = ray.put(search_identities)
        
        print('Starting tasks')
        task_1_refs = [] 
        actor_index = 0
        for collection_batch_ref in collection_batch_refs:
            actor_ref = actor_refs[actor_index]
            task_1_refs.append(store_embeddings.remote(
                actor_ref = actor_ref,
                storage_parameters = storage_parameters,
                data_parameters = data_parameters,
                collection_tuples = collection_batch_ref,
                given_identities = vector_identity_ref
            ))
            actor_index = (actor_index + 1) % actor_number
        
        print('Waiting store embeddings')
        updated_vector_identities = []
        batch_index = 0
        task_2_refs = []
        actor_index = 0
        while len(task_1_refs):
            done_task_1_refs, task_1_refs = ray.wait(task_1_refs)
            for output_ref in done_task_1_refs:
                actor_ref = actor_refs[actor_index]
                collection_batch_ref = collection_batch_refs[batch_index]
                task_2_refs.append(store_keywords.remote(
                    actor_ref = actor_ref, 
                    storage_parameters = storage_parameters,
                    data_parameters = data_parameters,
                    collection_tuples = collection_batch_ref,
                    given_identities = search_identity_ref
                ))
                actor_index = (actor_index + 1) % actor_number
                batch_index += 1
                updated_vector_identities.extend(ray.get(output_ref))
        print('Store embeddings waited')

        updated_search_identities = []
        print('Waiting store keywords')
        while len(task_2_refs):
            done_task_2_refs, task_2_refs = ray.wait(task_2_refs)
            for output_ref in done_task_2_refs:
                updated_search_identities.extend(ray.get(output_ref))
        print('Store keywords waited')
        
        print('Storing vector identities')
        store_checked(
            object_client = object_client,
            storage_parameters = storage_parameters,
            prefix = storage_parameters['vector-identity-prefix'],
            checked = updated_vector_identities 
        )

        print('Storing search identities')
        store_checked(
            object_client = object_client,
            storage_parameters = storage_parameters,
            prefix = storage_parameters['search-identity-prefix'],
            checked = updated_search_identities
        )

        print('All stored')

        remove_duplicate_vectors(
            vector_client = vector_client
        )

        return True
    except Exception as e:
        print('Preprocess error')
        print(e)
        return False 

if __name__ == "__main__":
    print('Starting ray job')
    print('Python version is:' + str(sys.version))
    print('Ray version is:' + version('ray'))
    print('PyMongo version is:' + version('pymongo'))
    print('Qdrant version is:' + version('qdrant-client'))
    print('Meilisearch version is:' + version('meilisearch'))
    print('Langchain version is:' + version('langchain'))
    print('Langchain huggingface version is:' + version('langchain-huggingface'))
    print('Spacy version is:' + version('spacy'))
    
    input = json.loads(sys.argv[1])

    process_parameters = input['process-parameters']
    storage_parameters = input['storage-parameters']
    data_parameters = input['data-parameters']

    print('Running preprocess')

    preprocess_status = preprocess_data(
        process_parameters = process_parameters,
        storage_parameters = storage_parameters,
        data_parameters = data_parameters
    )
    
    print('Preprocess success:' + str(preprocess_status))

    print('Ray job Complete')
