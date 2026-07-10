import os
import yaml
import shutil

def set_scheduler_kustomize_folder():
    kustomize_folder = 'scheduler/definition' 
    os.makedirs(kustomize_folder, exist_ok=True)
    return kustomize_folder

def get_scheduler_template_folder():
    template_folder = 'scheduler/template'
    return template_folder

def define_scheduler_deployment(
    scheduler_request: any
): 
    # We assume that name 
    # space is already created
    kustomize_folder = set_scheduler_kustomize_folder()
    template_folder = get_scheduler_template_folder()

    deployment_folder = None
    kustomization_yaml_path = kustomize_folder + '/kustomization.yaml'
    if not os.path.exists(kustomization_yaml_path) and 0 == len(scheduler_request):
        return deployment_folder
    
    deployment_yaml_path = kustomize_folder + '/deployment.yaml'
    if not os.path.exists(deployment_yaml_path):
        deployment_path = template_folder + '/deployment.yaml'
        deployment_data = None
        with open(deployment_path,'r') as f:
            deployment_data = yaml.safe_load(f)

        used_container = deployment_data['spec']['template']['spec']['containers']
        container_envs = used_container[0]['env']
        scheduler_times = container_envs[-1]['value']

        modified_scheduler_times = scheduler_times.split('|')
        given_scheduler_times = scheduler_request['task-times']
        index = 0
        for time in modified_scheduler_times:
            modified_scheduler_times[index] = str(given_scheduler_times[index])
            index += 1

        set_scheduler_times = '|'.join(modified_scheduler_times)
        deployment_data['spec']['template']['spec']['containers'][0]['env'][-1]['value'] = set_scheduler_times

        with open(deployment_yaml_path, 'w') as f:
            yaml.dump(deployment_data, f, sort_keys = False)
    
    if not os.path.exists(kustomization_yaml_path):
        kustomization_data = None
        kustomization_path = template_folder + '/kustomization.yaml'
        with open(kustomization_path,'r') as f:
            kustomization_data = yaml.safe_load(f)

        with open(kustomization_yaml_path, 'w') as f:
            yaml.dump(kustomization_data, f, sort_keys = False)

    return kustomize_folder

def remove_scheduler_deployment() -> bool:
    kustomize_folder = os.path.abspath(set_scheduler_kustomize_folder())
    try:
        shutil.rmtree(kustomize_folder)
        return True
    except Exception as e:
        print('Remove scheduler deployment error:' + str(e))
        return False
        
    

