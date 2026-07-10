import yaml
import os

from functions.utility.storage.objects import set_object_path, check_bucket, get_object, set_object

def get_identity_imports(
    storage_client: any,
    storage_name: str
) -> any:
    # We will assume that 
    # unnecessery import 
    # objects are deleted

    # Concurrency source
    forwarder_bucket_info = check_bucket(
        storage_client = storage_client,
        bucket_name = storage_name
    )

    forwader_bucket_objects = forwarder_bucket_info['objects']
    
    import_prefix = set_object_path(
        object_name = 'forwards',
        path_replacers = {
            'name': 'IMPORTS'
        },
        path_names = []
    )
    
    import_objects = {}
    for object_path in forwader_bucket_objects.keys():
        if import_prefix in object_path:
            path_split = object_path.split('/')
            submitter_name = path_split[-2]
            import_key = path_split[-1]
            
            import_object = get_object(
                storage_client = storage_client,
                bucket_name = storage_name,
                object_name = 'imports',
                path_replacers = {
                    'name': submitter_name
                },
                path_names = [
                    import_key
                ]
            )
            
            stored_data = {
                'data': import_object['data'],
                'metadata': import_object['custom-meta']
            }

            if not submitter_name in import_objects:
                import_objects[submitter_name] = {
                    import_key: stored_data
                }
                continue

            import_objects[submitter_name][import_key] = stored_data  
    return import_objects

def set_import_kustomize_folder(
    identity: str,
    key: str
):
    kustomize_folder = 'forwards/imports/' 
    kustomize_folder += identity + '/'
    kustomize_folder += key
    os.makedirs(kustomize_folder, exist_ok=True)
    return kustomize_folder

def get_import_template_folder(
    type: str
) -> str:
    template_folder = ''
    if type == 'regular':
        template_folder = 'forwards/imports/templates/regular'
    if type == 'scrapable':
        template_folder = 'forwards/imports/templates/scrapable'
    return template_folder

def define_import_deployment(
    import_type: str,
    import_identity: str,
    import_key: str,
    import_connections: any
) -> any:
    # We assume that all forwarding 
    # imports are put under the same 
    # namespace while the names are 
    # used for differentation
    kustomize_folder = set_import_kustomize_folder(
        identity = import_identity,
        key = import_key
    )
    
    template_folder = get_import_template_folder(
        type = import_type
    ) 

    namespace_data = None
    namespace_path = template_folder + '/namespace.yaml'
    with open(namespace_path,'r') as f:
        namespace_data = yaml.safe_load(f)
    
    endpoints_data = None
    endpoints_path = template_folder + '/endpoints.yaml'
    with open(endpoints_path,'r') as f:
        endpoints_data = yaml.safe_load(f)
    
    service_data = None
    service_path = template_folder + '/service.yaml'
    with open(service_path,'r') as f:
        service_data = yaml.safe_load(f)
    
    kustomization_data = None
    kustomization_path = template_folder + '/kustomization.yaml'
    with open(kustomization_path,'r') as f:
        kustomization_data = yaml.safe_load(f)
    
    services = {}
    file_names = []

    namespace = 'forwarder-imports'
    namespace_yaml_path =  kustomize_folder + '/namespace.yaml' 
    if not os.path.exists(namespace_yaml_path):
        namespace = namespace_data['metadata']['name'] 
        with open(namespace_yaml_path, 'w') as f:
            yaml.dump(namespace_data, f, sort_keys = False)
        file_names.append('namespace.yaml')

    for connection in import_connections:
        name = connection['name']
        address = connection['address']
        port = connection['port']

        # Service-endpoints need to have 
        # the same name. Kustomize has a 
        # 253 name limit 

        username = '-'.join(import_identity.split('-')[5:])
        user_separation_prefix = username + '-' + import_key 
        service_endpoints_name = user_separation_prefix + '-' + name 
        
        endpoints_yaml_path = kustomize_folder + '/' + name + '-endpoints.yaml'
        if not os.path.exists(endpoints_yaml_path):
            endpoints_data['metadata']['name'] = service_endpoints_name
            endpoints_data['subsets'][0]['addresses'][0]['ip'] = address
            endpoints_data['subsets'][0]['ports'][0]['port'] = int(port)
            with open(endpoints_yaml_path, 'w') as f:
                yaml.dump(endpoints_data, f, sort_keys = False)
            file_names.append(name + '-endpoints.yaml')

        service_yaml_path = kustomize_folder + '/' + name + '-service.yaml'
        # Example http://remote-ray-bridge.default.svc.cluster.local:8280
        services[name] = service_endpoints_name + '.' + namespace + '.svc.cluster.local:' + str(port)
        if not os.path.exists(service_yaml_path):
            service_data['metadata']['name'] = service_endpoints_name
            service_data['spec']['ports'][0]['port'] = int(port)
            service_data['spec']['ports'][0]['targetPort'] = int(port)
            with open(service_yaml_path, 'w') as f:
                yaml.dump(service_data, f, sort_keys = False)
            file_names.append(name + '-service.yaml')

    kustomization_yaml_path = kustomize_folder + '/kustomization.yaml'
    if not os.path.exists(kustomization_yaml_path):
        kustomization_data['namespace'] = namespace
        kustomization_data['resources'] = file_names
        with open(kustomization_yaml_path, 'w') as f:
            yaml.dump(kustomization_data, f, sort_keys = False)

    return [kustomize_folder, services] 

