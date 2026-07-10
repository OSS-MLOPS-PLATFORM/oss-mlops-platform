from kubernetes import client, config
from typing import Dict

def get_kubernetes_clients():
    try:
        config.load_kube_config()
    except Exception as e:
        print('Kube config error: ' + str(e))
    try:
        config.load_incluster_config()
    except Exception as e:
        print('Incluster config error: ' + str(e))
    regular = client.CoreV1Api()
    custom = client.CustomObjectsApi()
    clients = [
        regular,
        custom
    ]
    return clients

def get_cluster_structure(
    kubernetes_clients: any
) -> Dict[str, Dict[str,str]]:
    regular = kubernetes_clients[0]
    cluster = {}
    namespaces = regular.list_namespace().items
    for namespace in namespaces:
        namespace_name = namespace.metadata.name
        
        pods = regular.list_namespaced_pod(namespace_name).items
        pod_names = [pod.metadata.name for pod in pods] 

        services = regular.list_namespaced_service(namespace_name).items
        service_names = [service.metadata.name for service in services]
        
        cluster[namespace_name] = {'pods': pod_names, 'services': service_names}
    structure = {'structure': cluster}
    return structure