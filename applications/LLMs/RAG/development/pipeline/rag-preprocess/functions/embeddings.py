
import ray

import re
import hashlib

from qdrant_client.models import VectorParams, Distance, PointStruct

from langchain_text_splitters import Language

from functions.utility import generate_uuid, batch_list
from functions.documents import get_sorted_documents
from functions.mongo_db import mongo_setup_client
from functions.langchain import langchain_create_code_chunks, langchain_create_text_chunks
from functions.qdrant_vb import qdrant_setup_client, qdrant_list_collections, qdrant_create_collection, qdrant_upsert_points

def generate_hash(
    chunk: any
) -> any:
    chunk = re.sub(r'[^\w\s]', '', chunk)
    chunk = re.sub(r'\s+', ' ', chunk) 
    chunk = chunk.strip()
    chunk = chunk.lower()
    return hashlib.md5(chunk.encode('utf-8')).hexdigest()

def create_chunks(
    data_parameters: any,
    database: str,
    collection: str,
    id: str,
    type: str,
    data: any
):
    chunks = []
    try:
        created_chunks = []
        if type == 'python':
            used_configuration = data_parameters[type]
            created_chunks = langchain_create_code_chunks(
                language = Language.PYTHON,
                chunk_size = used_configuration['chunk-size'],
                chunk_overlap = used_configuration['chunk-overlap'],
                code = data
            )
        if type == 'text' or type == 'yaml' or type == 'markdown':
            used_configuration = data_parameters[type]
            created_chunks = langchain_create_text_chunks(
                chunk_size = used_configuration['chunk-size'],
                chunk_overlap = used_configuration['chunk-overlap'],
                text = data
            )
            
        for chunk in created_chunks:
            if chunk.strip() and 2 < len(chunk):
                chunks.append(chunk)
    except Exception as e:
        print(database,collection,id)
        print(e)
    
    return chunks

def check_collection(
    vector_client: any,
    vector_collection: str,
    embedding_size: int
) -> bool:
    vector_collections = qdrant_list_collections(
        qdrant_client = vector_client
    )
    
    collection_created = False
    if not vector_collection in vector_collections:
        try:
            collection_configuration = VectorParams(
                size = embedding_size, 
                distance = Distance.COSINE
            )
            collection_created = qdrant_create_collection(
                qdrant_client = vector_client,
                collection_name = vector_collection,
                configuration = collection_configuration
            )
        except Exception as e:
            print(e)
    return collection_created

def create_point(
    database: str,
    collection: str,
    id: any,
    embedding: any,
    index: any,
    type: str,
    chunk: any,
    chunk_hash: any
):
    embedding_uuid = generate_uuid(
        id = id,
        index = index
    )

    point = PointStruct(
        id = embedding_uuid, 
        vector = embedding,
        payload = {
            'database': database,
            'collection': collection,
            'document': id,
            'type': type,
            'chunk': chunk,
            'chunk_hash': chunk_hash
        }
    )
    return point

@ray.remote(
    num_cpus = 1,
    memory = 4 * 1024 * 1024 * 1024
)
def store_embeddings(
    actor_ref: any,
    storage_parameters: any,
    data_parameters: any,
    collection_tuples: any,
    given_identities: any 
):
    collection_amount = len(collection_tuples) 
    print('Storing embeddings of ' + str(collection_amount) + ' collections')
    
    document_client = mongo_setup_client(
        username = storage_parameters['mongo-username'], 
        password = storage_parameters['mongo-password'],
        address = storage_parameters['mongo-address'],
        port = storage_parameters['mongo-port']
    )

    vector_client = qdrant_setup_client(
        api_key = storage_parameters['qdrant-key'],
        address = storage_parameters['qdrant-address'], 
        port = storage_parameters['qdrant-port']
    )
    
    collection_prefix = storage_parameters['vector-collection-prefix']
    document_identities = given_identities
    embedding_index = len(document_identities)
    collection_number = 1
    for collection_tuple in collection_tuples:
        document_database = collection_tuple[0]
        document_collection = collection_tuple[1] 
        
        collection_documents = get_sorted_documents( 
            document_client = document_client,
            database = document_database,
            collection = document_collection
        )

        if collection_number % data_parameters['vector-collection-print'] == 0:
            print(str(collection_number) + '/' + str(collection_amount))
        collection_number += 1

        document_batches = batch_list(
            target = collection_documents,
            size = data_parameters['embedding-batch-size']
        )

        vector_collection = document_database.replace('|','-') + '-' + collection_prefix
        
        created = check_collection(
            vector_client = vector_client,
            vector_collection = vector_collection,
            embedding_size = data_parameters['embedding-length'] 
        )
        
        #print('Collection ' + str(vector_collection) + ' created: ' + str(created))
    
        embedding_task_refs = []
        list_chunks = []
        list_index = 0
        for document_batch in document_batches:    
            document_batch_chunks = [] 
            for document in document_batch:
                id = str(document['_id'])
                document_identity = document_database + '-' + document_collection + '-' + id
                if not document_identity in document_identities:
                    type = document['type']
                    data = document['data']

                    document_chunks = create_chunks(
                        data_parameters = data_parameters,
                        database = document_database,
                        collection = document_collection,
                        id = id,
                        type = type,
                        data = data
                    )

                    document_identities.append(document_identity)
                    list_chunks.append(document_chunks)
                    document_batch_chunks.append((list_index, document_chunks))
                    list_index += 1
                    
            if 0 < len(document_batch_chunks):
                # Might need a release mechanism
                batched_chunks_ref = ray.put(document_batch_chunks)
                embedding_task_refs.append(actor_ref.batch_create_embeddings.remote(
                    batched_chunks = batched_chunks_ref
                ))
                
        list_embeddings = []
        while len(embedding_task_refs):
            done_task_refs, embedding_task_refs = ray.wait(embedding_task_refs)
            for output_ref in done_task_refs: 
                batched_embeddings_ref = ray.get(output_ref)
                batched_embeddings = ray.get(batched_embeddings_ref)
                list_embeddings.extend(batched_embeddings)

        for tuple in list_embeddings:
            used_index = tuple[0]
            document_embeddings = tuple[-1]
            used_chunks = list_chunks[used_index]
            points = []
            added_hashes = []
            chunk_index = 0
            for chunk in used_chunks:
                chunk_hash = generate_hash(
                    chunk = chunk
                )
                if not chunk_hash in added_hashes:
                    embedding = document_embeddings[chunk_index]
                    document = collection_documents[used_index]
                    
                    point = create_point(
                        database = document_database,
                        collection = document_collection,
                        id = str(document['_id']),
                        embedding = embedding,
                        index = embedding_index,
                        type = document['type'],
                        chunk = chunk,
                        chunk_hash = chunk_hash
                    )

                    points.append(point)
                    embedding_index += 1

            if 0 < len(points):
                batched_points = batch_list(
                    target = points,
                    size = data_parameters['points-batch-size']
                )

                for batch_points in batched_points:
                    points_stored = qdrant_upsert_points( 
                        qdrant_client = vector_client, 
                        collection_name = vector_collection,
                        points = batch_points
                    )

    return document_identities
