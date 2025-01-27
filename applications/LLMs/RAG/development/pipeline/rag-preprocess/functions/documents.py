
from pymongo import ASCENDING

from functions.utility import get_github_storage_prefix
from functions.mongo_db import mongo_list_databases, mongo_list_collections, mongo_collection_number, mongo_list_documents

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

def get_divided_collections(
    document_client: any,
    data_parameters: any,
    number: int
) -> any:
    database_list = mongo_list_databases(
        mongo_client = document_client
    )

    storage_structure = {}    
    
    database_prefix = get_github_storage_prefix(
        repository_owner = data_parameters['repository-owner'],
        repository_name = data_parameters['repository-name']
    )
    for database_name in database_list:
        if database_prefix in database_name:
            collection_list = mongo_list_collections(
                mongo_client = document_client,
                database_name = database_name
            )
            storage_structure[database_name] = collection_list
    
    type_priority = data_parameters['document-type-priority']
    collection_tuples = []
    for database_name, collections in storage_structure.items():
        for collection_name in collections:
            collection_type = database_name.split('|')[-1]
            collection_priority = type_priority[collection_type]
            amount_of_documents = mongo_collection_number(
                mongo_client = document_client,
                database_name = database_name,
                collection_name = collection_name
            )
            tuple = (database_name, collection_name, collection_priority, amount_of_documents)
            collection_tuples.append(tuple)
            
    print('Amount of collections: ' + str(len(collection_tuples)))

    return round_robin_division(
        target_list = collection_tuples, 
        number = number
    )

def get_sorted_documents(
    document_client: any,
    database: str,
    collection: str
) -> any:
    collection_documents = mongo_list_documents(
        mongo_client = document_client,
        database_name = database,
        collection_name = collection,
        filter_query = {},
        sorting_query = [
            ('index', ASCENDING),
            ('sub-index', ASCENDING)
        ]
    )
    return collection_documents