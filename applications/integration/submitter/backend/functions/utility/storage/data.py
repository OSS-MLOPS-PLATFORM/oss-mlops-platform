# Communication object = High writes and reads with small size
# Artifact object = Low append only writes with occational reads with large size

def job_status_communication_object_data():
    # There might be cases, 
    # where jobs need to be 
    # run at the same time
    # but that can be left 
    # for later.This might 
    # need a option to 
    # designate other folders 
    # besides personal directory
    # maybe move files up
    # add stopped
    job_status = {
        'name': '',
        'target': '',
        'id': '',
        'enviroment': {
            'submission-modules': [],
            'venv': {
                'name': '',
                'directory': '',
                'configuration-modules': [],
                'packages': []
            }
        },
        'files': {
            'provide': [],
            'store': []
        },
        'workflow': {
            'requires': [],
            'enables': []
        }, 
        'start': False,
        'ready': False,
        'submit': False,
        'pending': False,
        'running': False,
        'failed': False,
        'complete': False,
        'cancel': False,
        'stopped': False,
        'stored': False
    } 
    return job_status

def enviroment_properties_communication_object_data():
    # Per enviroment
    enviroment_properties = {
        'default-directory': '',
        'python-version': ''
    }
    return enviroment_properties

def enviroment_status_communication_object_data():
    # Per enviroment
    enviroment_status = {
        'current-workspace': {}
    }
    return enviroment_status

def job_time_communication_object_data():
    # Per job
    job_time_status = {
        'begin-start': 0,
        'end-start': 0,
        'total-start-seconds': 0,
        'begin-configuration': 0,
        'end-configuration': 0,
        'total-configuration-seconds': 0,
        'begin-run': 0,
        'end-run': 0,
        'total-run-seconds': 0,
        'begin-cancel': 0,
        'end-cancel': 0,
        'total-cancel-seconds': 0,
        'begin-store': 0,
        'end-store': 0,
        'total-store-seconds': 0
    }
    return job_time_status

def slurm_sacct_artifact_object_data():
    # Per job, so not cumulative
    sacct_artifact_data = {
        'row': {
            'JobID': '',
            'JobName': '',
            'Account': '',
            'Partition': '',
            'ReqCPUS': '',
            'AllocCPUS': '',
            'ReqNodes': '',
            'AllocNodes': '',
            'State': '',
            'AveCPU': '',
            'AveCPUFreq': '',
            'AveDiskRead': '',
            'AveDiskWrite': '',
            'Timelimit': '',
            'Submit': '',
            'Start': '',
            'Elapsed': '',
            'Planned': '',
            'End': '',
            'PlannedCPU': '',
            'CPUTime': '',
            'TotalCPU': ''
        }
    }
    return sacct_artifact_data

def slurm_seff_artifact_object_data():
    # Per job, so not cumulative
    seff_artifact_data = {
        'Job ID': '',
        'Cluster': '',
        'User/Group': '',
        'State': '',
        'Nodes': '',
        'Cores per node': '',
        'CPU Utilized': '',
        'CPU Efficiency': '',
        'Job Wall-clock time': '',
        'Memory Utilized': '',
        'Memory Efficiency': '',
        'Billed project': '',
        'Non-Interactive BUs': ''
    }
    return seff_artifact_data

def slurm_log_artifact_object_data():
    log_artifact_data = [
        'row 1',
        'row 2',
        'row n'
    ]
    return log_artifact_data
# Consider remote forwarding the flower address
# into kind to enable prometheus to scrape it
# Though, for statelessnes, it would be a good idea 
# to store atleast the time data into Allas
def flower_task_artifact_object_data():
    # Per task name, so key cumulative
    task_artifact_data = {
        'id/uuid': {
            'worker': '',
            'chilren': [
                'name-uuid'
            ],
            'state': '',
            'received': '',
            'started': '',
            'succeeded': '',
            'failed': '',
            'result': '',
            'timestamp': '',
            'runtime': ''
        }
    }
    return task_artifact_data