import ray

def check_resources(
    resources: any
):
    cluster_resources = {
        'CPU': resources['CPU'],
        'OSM': resources['object_store_memory'],
        'RAM': resources['memory']
    }
    if 'GPU' in resources:
        cluster_resources['GPU'] = resources['GPU']
    return cluster_resources

def check_nodes(
    nodes: any
):
    cluster_nodes = []
    for node in nodes:
        node_data = {
            'name': node['NodeManagerHostname'],
            'address': node['NodeManagerAddress'],
            'alive': node['Alive'],
            'CPUs': node['Resources']['CPU'],
            'OSM': node['Resources']['object_store_memory'],
            'RAM': node['Resources']['memory']
        }
        if 'GPU' in node['Resources']:
            node_data['GPU'] = node['Resources']['GPU']
        cluster_nodes.append(node_data)
    return cluster_nodes

def check_cluster(
    cluster_resources: any,
    cluster_nodes: any
):
    collective = [0,0,0,0]
    checked_resources = check_resources(
        resources = cluster_resources
    )
    
    collective[0] = checked_resources['CPU']
    collective[1] = checked_resources['OSM']
    collective[2] = checked_resources['RAM']

    if 'GPU' in checked_resources:
        collective[3] = checked_resources['GPU']

    checked_nodes = check_nodes(
        nodes = cluster_nodes
    )

    return collective, checked_resources, checked_nodes

def check_clusters(
    cluster_urls: any
) -> any:
    try:
        clusters = {}
        # CPU, OSM, RAM, GPU
        collective = [0,0,0,0]
        for i in range(len(cluster_urls)+1):
            checked_collective = [0,0,0,0]
            checked_resources = {}
            checked_nodes = {}
            if i == 0:
                ray.init()
                checked_collective, checked_resources, checked_nodes = check_cluster(
                    cluster_resources = ray.available_resources(),
                    cluster_nodes = ray.nodes()
                )
            else:
                head_url = 'ray://' + cluster_urls[i-1]
                head_client = ray.init(
                    address = head_url, 
                    allow_multiple = True
                )

                with head_client:
                    checked_collective, checked_resources, checked_nodes = check_cluster(
                        cluster_resources = ray.available_resources(),
                        cluster_nodes = ray.nodes()
                    )
                head_client.disconnect()

            collective = [a + b for a,b in zip(collective, checked_collective)]
            clusters[str(i)] = {
                'resources': checked_resources,
                'nodes': checked_nodes
            }
        
            i += 1
        clusters['collective'] = {
            'CPU': collective[0],
            'OSM': collective[1],
            'RAM': collective[2],
            'GPU': collective[3]
        }
        return clusters
    except Exception as e:
        print('Check resources error')
        print(e)
        return {}