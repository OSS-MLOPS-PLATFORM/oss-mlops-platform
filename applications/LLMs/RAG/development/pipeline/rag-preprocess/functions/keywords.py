

import ray

from functions.utility import batch_list, generate_uuid
from functions.documents import get_sorted_documents
from functions.mongo_db import mongo_setup_client
from functions.meili_sb import meili_setup_client, meili_add_documents, meili_set_filterable

def create_payload(  
    database: str,
    collection: str,
    id: any,
    index: int,
    type: str,
    keywords: any
) -> any:
    keyword_uuid = generate_uuid(
        id = id,
        index = index
    ) 

    keyword_payload = {
        'id': keyword_uuid,
        'database': database,
        'collection': collection,
        'document': id,
        'type': type,
        'keywords': keywords
    }

    return keyword_payload

@ray.remote(
    num_cpus = 1,
    memory = 4 * 1024 * 1024 * 1024
) 
def store_keywords(
    actor_ref: any,
    storage_parameters: any,
    data_parameters: any,
    collection_tuples: any,
    given_identities: any
):
    collection_amount = len(collection_tuples)
    print('Storing keywords of ' + str(collection_amount) + ' collections')
    
    document_client = mongo_setup_client(
        username = storage_parameters['mongo-username'],
        password = storage_parameters['mongo-password'],
        address = storage_parameters['mongo-address'],
        port = storage_parameters['mongo-port']
    )

    search_client = meili_setup_client(
        api_key = storage_parameters['meili-key'],
        host = storage_parameters['meili-host']
    )
    
    collection_prefix = storage_parameters['search-collection-prefix']
    document_identities = given_identities
    keyword_index = len(document_identities)
    collection_number = 1
    for collection_tuple in collection_tuples:
        document_database = collection_tuple[0]
        document_collection = collection_tuple[1]
        
        collection_documents = get_sorted_documents(
            document_client = document_client,
            database = document_database,
            collection = document_collection
        ) 

        if collection_number % data_parameters['search-collection-print'] == 0:
            print(str(collection_number) + '/' + str(collection_amount))
        collection_number += 1
    
        document_batches = batch_list(
            target = collection_documents,
            size = data_parameters['keyword-batch-size'] 
        )

        search_collection = document_database.replace('|','-') + '-' + collection_prefix

        keyword_task_refs = []
        list_index = 0        
        for document_batch in document_batches:
            document_batch_text = []
            for document in document_batch:
                id = str(document['_id'])
                document_identity = document_database + '-' + document_collection + '-' + id
                if not document_identity in document_identities:
                    document_text = document['data']
                    document_identities.append(document_identity)
                    document_batch_text.append((list_index, document_text))
                    list_index += 1
                    
            if 0 < len(document_batch_text):
                batched_text_ref = ray.put(document_batch_text)
                keyword_task_refs.append(actor_ref.batch_search_keywords.remote(
                    batched_text = batched_text_ref
                ))
        
        list_keywords = []
        while len(keyword_task_refs):
            done_task_refs, keyword_task_refs = ray.wait(keyword_task_refs)
            for output_ref in done_task_refs: 
                batched_keywords_ref = ray.get(output_ref)
                batched_keywords = ray.get(batched_keywords_ref)
                list_keywords.extend(batched_keywords)
        
        payloads = []
        for tuple in list_keywords:
            used_index = tuple[0]
            document_keywords = tuple[-1]
            
            if 0 < len(document_keywords):
                document = collection_documents[used_index]
                payload = create_payload(
                    database = document_database,
                    collection = document_collection,
                    id = str(document['_id']),
                    index = keyword_index,
                    type = document['type'],
                    keywords = document_keywords
                )
                payloads.append(payload)
                keyword_index += 1 
        
        stored = meili_add_documents(
            meili_client = search_client,
            index_name = search_collection,
            documents = payloads
        )  

        meili_set_filterable(
            meili_client = search_client, 
            index_name = search_collection, 
            attributes = ['keywords']
        )
 
    return document_identities
