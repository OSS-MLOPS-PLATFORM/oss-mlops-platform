
from functions.utility.scheduling.deployment import define_scheduler_deployment, remove_scheduler_deployment
from functions.platforms.kustomize import kustomize_create_deployment, kustomize_delete_deployment

def modify_scheduling(
    scheduler_request: any,
    action: str
):
    deployment_folder = define_scheduler_deployment(
        scheduler_request = scheduler_request
    ) 
    
    deployment_status = False
    
    if action == 'start':
        deployment_status = kustomize_create_deployment(
            kustomize_folder = deployment_folder
        )

    if action == 'stop':
        removed = kustomize_delete_deployment(
            kustomize_folder = deployment_folder
        )

        if removed: 
            deployment_status = remove_scheduler_deployment()
            
    return deployment_status