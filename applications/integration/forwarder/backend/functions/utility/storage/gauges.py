def get_sacct_gauge_structure():
    # Double check the labels
    structure = {
        'name': 'cloud_hpc_job_sacct_metrics',
        'docs': 'SLURM Sacct metrics collected from completed jobs',
        'labels': [
            'user',
            'jobkey',
            'jobid',
            'row',
            'jobname',
            'partition',
            'state',
            'metric'
        ],
        'names': {
            'req-cpus': 'RqCPUS',
            'alloc-cpus': 'AcCPUS',
            'req-nodes': 'RqNod',
            'alloc-nodes': 'AcNod',
            'ave-cpu-seconds': 'AvCPUSec',
            'ave-cpu-freq-khz': 'AvCPUFreqkhz',
            'ave-disk-read-bytes': 'AvDiReByte',
            'ave-disk-write-bytes': 'AvDiWrByte',
            'timelimit-seconds': 'TiLiSec',
            'elapsed-seconds': 'ElaSec',
            'planned-seconds': 'PlaSec',
            'planned-cpu-seconds': 'PlaCPUSec',
            'cpu-time-seconds': 'CPUTiSec',
            'total-cpu-seconds': 'ToCPUSec',
            'submit-time': 'SuTi',
            'start-time': 'StTi',
            'end-time': 'EnTi'
        }
    }
    return structure

def get_seff_gauge_structure():
    structure = {
        'name': 'cloud_hpc_job_seff_metrics',
        'docs': 'SLURM Seff metrics collected from completed jobs',
        'labels': [
            'user',
            'jobkey',
            'jobid',
            'project',
            'cluster', 
            'state',
            'metric'
        ],
        'names': {
            'nodes': 'Nod',
            'cores-per-node': 'CoPeNod',
            'cpu-utilized-seconds': 'CPUUSec',
            'cpu-efficiency-percentage': 'CPUEffPe',
            'cpu-efficiency-seconds': 'CPUEffSec',
            'job-wall-clock-time-seconds': 'JoWaClTISec',
            'memory-utilized-bytes': 'MemUtiByte',
            'memory-efficiency-percentage': 'MemEffPe',
            'memory-efficiency-bytes': 'MemEffByte',
            'billing-units': 'BiUn'
        }
    }
    return structure

def get_job_time_gauge_structure():
    structure = {
        'name': 'cloud_hpc_job_time_metrics',
        'docs': 'Time metrics collected from submitter jobs',
        'labels': [
            'collector',
            'jobkey',
            'metric'
        ],
        'names': {
            'total-start-seconds': 'ToStaSec',
            'total-configuration-seconds': 'ToConSec',
            'total-run-seconds': 'ToRunSec', 
            'total-cancel-seconds': 'ToCanSec',
            'total-store-seconds': 'ToStoSec'
        }
    }
    return structure

def get_pipeline_time_gauge_structure():
    structure = {
        'name': 'cloud_hpc_pipeline_time_metrics',
        'docs': 'Time metrics collected from pipeline times',
        'labels': [
            'collector',
            'sampleid',
            'group',
            'name',
            'metric'
        ],
        'names': {
            'total-seconds': 'ToSec'
        }
    }
    return structure

def get_task_time_gauge_structure():
    structure = {
        'name': 'cloud_hpc_task_time_metrics',
        'docs': 'Time metrics collected from forwarder and submitter tasks',
        'labels': [
            'collector',
            'sampleid',
            'group',
            'metric'
        ],
        'names': {
            'total-wait-seconds': 'ToWaiSec',
            'total-run-seconds': 'ToRunSec',
            'total-task-seconds': 'ToTasSec'
        }
    }
    return structure
