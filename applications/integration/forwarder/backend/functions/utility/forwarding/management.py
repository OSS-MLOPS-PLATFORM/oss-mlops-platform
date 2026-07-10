from functions.utility.forwarding.imports import define_import_deployment,  get_identity_imports
from functions.platforms.kustomize import kustomize_create_deployment, kustomize_delete_deployment
from functions.utility.storage.objects import set_object

def modify_forwarding( 
    storage_client: any,
    storage_name: str,
    forwarding_identity: str,
    forwarding_key: str,
    forwarding_object: any,
    forwarding_type: str
) -> str:
    # Can cause concurrency issues 
    # between forwarder workers
    forwarding_data = forwarding_object['data']
    forwarding_metadata = forwarding_object['metadata']
    forwarding_connections = forwarding_data['connections']
    
    forwarding_data_changed = False
    deployment_status = 'no deployment'
    # Creates deployment
    if not forwarding_data['created'] and not forwarding_data['cancel'] and not forwarding_data['deleted']:
        deployment = None
        if forwarding_type == 'imports':
            # Refactor later to handle different types
            deployment = define_import_deployment(
                import_type = 'regular',  
                import_identity = forwarding_identity,
                import_key = forwarding_key,
                import_connections = forwarding_connections
            ) 
        
        if deployment is None:
            return 'No definition' 
        
        deployment_folder = deployment[0]
        deployment_services = deployment[1]

        created = kustomize_create_deployment(
            kustomize_folder = deployment_folder
        )

        if created:
            forwarding_data['created'] = True
            forwarding_data['services'] = deployment_services
            forwarding_metadata['version'] = forwarding_metadata['version'] + 1
            forwarding_data_changed = True
            deployment_status = 'creation success'
        else:
            deployment_status = 'creation failure'
    # removes deployment
    if forwarding_data['created'] and forwarding_data['cancel'] and not forwarding_data['deleted']:
        deployment = None
        if forwarding_type == 'imports':
            # Refactor later to handle different types
            deployment = define_import_deployment( 
                import_type = 'regular',
                import_identity = forwarding_identity,
                import_key = forwarding_key,
                import_connections = forwarding_connections
            )
        
        if deployment is None:
            return 'No definition' 
        
        deployment_folder = deployment[0]
        #deployment_services = deployment[1]

        removed = kustomize_delete_deployment(
            kustomize_folder = deployment_folder
        )

        if removed:
            forwarding_data['deleted'] = True
            forwarding_metadata['version'] = forwarding_metadata['version'] + 1
            forwarding_data_changed = True
            deployment_status = 'deletion success'
        else:
            deployment_status = 'deletion failure'
  
    if forwarding_data_changed:
        # Concurrency source
        set_object(
            storage_client = storage_client,
            bucket_name = storage_name,
            object_name = forwarding_type,
            path_replacers = {
                'name': forwarding_identity
            },
            path_names = [
                forwarding_key
            ],
            overwrite = True,
            object_data = forwarding_data,
            object_metadata = forwarding_metadata
        )
    
    return deployment_status

def deploy_forwards(
    storage_client: any,
    storage_name: str
):
    import_objects = get_identity_imports(
        storage_client = storage_client,
        storage_name = storage_name
    )
    
    if not len(import_objects) == 0:
        for import_identity, imports in import_objects.items():
            for import_key, import_object in imports.items():
                print('Modifying import forwarding with key: ' + str(import_key))
                deployment_status = modify_forwarding(
                    storage_client = storage_client,
                    storage_name = storage_name,
                    forwarding_identity = import_identity,
                    forwarding_key = import_key,
                    forwarding_object = import_object,
                    forwarding_type = 'imports'
                )
                print('Modification status: ' + str(deployment_status))

