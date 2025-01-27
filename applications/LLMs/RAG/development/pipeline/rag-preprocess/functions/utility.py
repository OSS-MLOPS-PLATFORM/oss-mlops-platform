import uuid

from math import ceil

from qdrant_client.models import PointIdsList
from functions.qdrant_vb import qdrant_list_collections, qdrant_collection_number, qdrant_search_data, qdrant_remove_points
from functions.minio_os import minio_check_object, minio_get_object_data_and_metadata, minio_create_or_update_object

def divide_list(
    target: any, 
    number: int
):
  size = ceil(len(target) / number)
  return list(
    map(lambda x: target[x * size:x * size + size],
    list(range(number)))
  ) 

def batch_list(
    target: any, 
    size: int
):
    return [target[i:i + size] for i in range(0, len(target), size)]

def generate_uuid(
    id: str,
    index: int
) -> str:
    keyword_id = id + '-' + str(index + 1)
    keyword_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, keyword_id))
    return keyword_uuid

def get_github_storage_prefix(
    repository_owner: str,
    repository_name: str
) -> str:
    return repository_owner + '|' + repository_name + '|'

def get_checked(
    object_client: any,
    storage_parameters: any,
    prefix: str
):
    used_object_bucket = storage_parameters['object-bucket']
    used_object_path = storage_parameters['object-path'] + '-' + prefix
    
    object_exists = minio_check_object(
        minio_client = object_client,
        bucket_name = used_object_bucket, 
        object_path = used_object_path
    )

    data = []
    if object_exists:
        data = minio_get_object_data_and_metadata(
            minio_client = object_client,
            bucket_name = used_object_bucket, 
            object_path = used_object_path
        )['data']
    return data

def store_checked(
    object_client: any,
    storage_parameters: any,
    prefix: str,
    checked: any
):
    used_object_bucket = storage_parameters['object-bucket']
    used_object_path = storage_parameters['object-path'] + '-' + prefix
    
    minio_create_or_update_object(
        minio_client = object_client,
        bucket_name = used_object_bucket, 
        object_path = used_object_path,
        data = checked, 
        metadata = {}
    )

def remove_duplicate_vectors(
    vector_client: any
):
    collections = qdrant_list_collections(
        qdrant_client = vector_client
    )
    # This might be parallizable
    for collection in collections:
        print('Cleaning collection ' + str(collection))
        collection_number = qdrant_collection_number(
            qdrant_client = vector_client, 
            collection_name = collection,
            count_filter = {}
        )

        print('Collection vectors: ' + str(collection_number))

        batch_size = 200
        scroll_offset = None

        unique_point_ids = set()
        unique_chunk_hashes = set()
        duplicate_vectors = []
        while True:
            vectors = qdrant_search_data(
                qdrant_client = vector_client,  
                collection_name = collection,
                scroll_filter = {},
                limit = batch_size,
                offset = scroll_offset
            )
            
            for vector in vectors[0]:
                chunk_hash = vector.payload['chunk_hash']
                vector_id = vector.id
                # Scroll can cause double count
                # so id check is needed
                if not vector_id in unique_point_ids:
                    unique_point_ids.add(vector_id)
                    if not chunk_hash in unique_chunk_hashes:
                        unique_chunk_hashes.add(chunk_hash)
                    else:
                        duplicate_vectors.append(vector_id)

            if len(vectors[0]) < batch_size:
                break

            scroll_offset = vectors[0][-1].id

        print('Found unique vectors: ' + str(len(unique_chunk_hashes)))
        print('Found duplicate vectors: ' + str(len(duplicate_vectors)))
        if 0 < len(duplicate_vectors):
            status = qdrant_remove_points(
                qdrant_client = vector_client,  
                collection_name = collection, 
                points_selector = PointIdsList(
                    points = duplicate_vectors
                )
            ) 
