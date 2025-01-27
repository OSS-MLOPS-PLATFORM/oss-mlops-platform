from qdrant_client import QdrantClient as qc

def qdrant_is_client(
    storage_client: any
) -> any:
    try:
        return isinstance(storage_client, qc.Connection)
    except Exception as e:
        return False

def qdrant_setup_client(
    api_key: str,
    address: str, 
    port: str
) -> any:
    try:
        qdrant_client = qc(
            host = address,
            port = int(port),
            api_key = api_key,
            https = False
        ) 
        return qdrant_client
    except Exception as e:
        return None

def qdrant_create_collection(
    qdrant_client: any, 
    collection_name: str,
    configuration: any
) -> any:
    try:
        result = qdrant_client.create_collection(
            collection_name = collection_name,
            vectors_config = configuration
        )
        return result
    except Exception as e:
        print(e)
        return None

def qdrant_get_collection(
    qdrant_client: any, 
    collection_name: str
) -> any:
    try:
        collection = qdrant_client.get_collection(
            collection_name = collection_name
        )
        return collection
    except Exception as e:
        return None

def qdrant_collection_number(
    qdrant_client: any, 
    collection_name: str,
    count_filter: any
) -> any:
    try:
        result = qdrant_client.count(
            collection_name = collection_name,
            count_filter = count_filter,
            exact =  True
        )
        return result.count
    except Exception as e:
        print(e)
        return None

def qdrant_list_collections(
    qdrant_client: any
) -> any:
    try:
        collections = qdrant_client.get_collections()
        collection_list = []
        for description in collections.collections:
            collection_list.append(description.name)
        return collection_list
    except Exception as e:
        return []
    
def qdrant_remove_collection(
    qdrant_client: any, 
    collection_name: str
) -> bool:
    try:
        qdrant_client.delete_collection(collection_name)
        return True
    except Exception as e:
        return False

def qdrant_upsert_points(
    qdrant_client: qc, 
    collection_name: str,
    points: any
) -> any:
    try:
        results = qdrant_client.upsert(
            collection_name = collection_name, 
            points = points
        )
        return results
    except Exception as e:
        print(e)
        return None

def qdrant_search_data(
    qdrant_client: qc,  
    collection_name: str,
    scroll_filter: any,
    limit: int,
    offset: any
) -> any:
    try:
        hits = qdrant_client.scroll(
            collection_name = collection_name,
            scroll_filter = scroll_filter,
            limit = limit,
            with_payload = True,
            offset = offset
        )
        return hits
    except Exception as e:
        print(e)
        return []

def qdrant_search_vectors(
    qdrant_client: qc,  
    collection_name: str,
    query_vector: any,
    limit: str
) -> any:
    try:
        hits = qdrant_client.search(
            collection_name = collection_name,
            query_vector = query_vector,
            limit = limit
        )
        return hits
    except Exception as e:
        return []

def qdrant_remove_points(
    qdrant_client: qc,  
    collection_name: str, 
    points_selector: any
) -> bool:
    try:
        results = qdrant_client.delete(
            collection_name = collection_name,
            points_selector = points_selector
        )
        return results
    except Exception as e:
        print(f"Error removing document: {e}")
        return None