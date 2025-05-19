import os
import subprocess

def kustomize_create_deployment( 
    kustomize_folder: str
) -> bool:
    # It seems that this gets not found errors, 
    # when a host computer has restarted and 
    # made the cluster run. Fortunelly this is 
    # mostly mitigated by the scaler 

    if not os.path.exists(kustomize_folder):
        return False
    
    try:
        argument = ['kubectl', 'apply', '-k', kustomize_folder]
        print('Attempting to use kubectl to run: ' + str(argument))
        result = subprocess.run(
            args = argument,
            capture_output = True,
            text = True,
            check = True 
        )
        result_print = result.stdout.replace('\n', ' ')
        print('Resulted print: ' + str(result_print))
        return True
    except Exception as e:
        print('Kustomize create deployment errror: ' + str(e))
        return False

def kustomize_delete_deployment(
    kustomize_folder: str
) -> bool:
    # It seems that this gets not found errors, 
    # when a host computer has restarted and 
    # made the cluster run. Fortunelly this is 
    # mostly mitigated by the scaler 

    if not os.path.exists(kustomize_folder):
        return False
    
    try:
        argument = ['kubectl', 'delete', '-k', kustomize_folder]
        print('Attempting to use kubectl to run: ' + str(argument))
        result = subprocess.run(
            args = argument,
            capture_output = True,
            text = True,
            check = True 
        )
        result_print = result.stdout.replace('\n', ' ')
        print('Resulted print: ' + str(result_print))
        return True
    except Exception as e:
        print('Kustomize delete deployment error: ' + str(e))
        return False