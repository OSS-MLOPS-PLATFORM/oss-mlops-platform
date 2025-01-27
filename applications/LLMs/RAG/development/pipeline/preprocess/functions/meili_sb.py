
import meilisearch as ms

def meili_is_client(
    storage_client: any
) -> any:
    try:
        return isinstance(storage_client, ms.Connection)
    except Exception as e:
        print(e)
        return False

def meili_setup_client(
    api_key: str,
    host: str
) -> any:
    try:
        meili_client = ms.Client(
            url = host, 
            api_key = api_key
        )
        return meili_client 
    except Exception as e:
        print(e)
        return None

def meili_get_index( 
    meili_client: any, 
    index_name: str
) -> any:
    try:
        index = meili_client.index(
            uid = index_name
        )
        return index
    except Exception as e:
        print(e)
        return None
    
def meili_check_index(
    meili_client: any, 
    index_name: str
) -> bool:
    try:
        meili_client.get_index(
            uid = index_name
        )
        return True
    except Exception as e:
        print(e)
        return False
    
def meili_remove_index(
    meili_client: any, 
    index_name: str
) -> bool:
    try:
        response = meili_client.index(
            index_name = index_name
        ).delete()
        return response
    except Exception as e:
        print(e)
        return None
    
def meili_list_indexes(
    meili_client: any
) -> bool:
    try:
        names = []
        indexes = meili_client.get_indexes()
        for index in indexes['results']:
            names.append(index.uid)
        return names
    except Exception as e:
        print(e)
        return None

def meili_add_documents(
    meili_client: any, 
    index_name: str, 
    documents: any
) -> any:
    try:
        index = meili_get_index(
            meili_client = meili_client,
            index_name = index_name
        )
        response = index.add_documents(
            documents = documents
        )
        return response
    except Exception as e:
        print(e)
        return None

def meili_set_filterable(
    meili_client: any, 
    index_name: str, 
    attributes: any
) -> any:
    try:
        index = meili_get_index(
            meili_client = meili_client,
            index_name = index_name
        )
        response = index.update_filterable_attributes(attributes)
        return response
    except Exception as e:
        print(e)
        return None

def meili_search_documents(
    meili_client: any, 
    index_name: str, 
    query: any, 
    options: any
) -> any:
    try:
        index = meili_get_index(
            meili_client = meili_client,
            index_name = index_name
        )
        response = index.search(
            query,
            options
        )
        return response
    except Exception as e:
        print(e)
        return None
    
def meili_update_documents(
    meili_client, 
    index_name, 
    documents
) -> any:
    try:
        index = meili_client.index(
            index_name = index_name
        )
        response = index.update_documents(
            documents = documents
        )
        return response
    except Exception as e:
        print(e)
        return None

def meili_delete_documents(
    meili_client: any, 
    index_name: str, 
    ids: any
) -> any:
    try:
        index = meili_client.index(
            index_name = index_name
        )
        response = index.delete_documents(
            document_ids = ids
        )
        return response
    except Exception as e:
        print(e)
        return None
