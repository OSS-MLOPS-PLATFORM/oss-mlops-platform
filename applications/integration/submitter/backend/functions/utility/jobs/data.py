from functions.utility.storage.objects import set_object_path, check_bucket, get_object
from functions.platforms.slurm import get_slurm_job_states, get_slurm_pending_states, get_slurm_running_states, get_slurm_failure_states, get_slurm_completion_states 
from functions.utility.requests.artifacts import get_squeue
 
def get_submitter_jobs(
    storage_client: any,
    storage_name: str
) -> any:
    # We will assume 
    # that unnecessery 
    # jobs objects
    # are deleted

    submitter_bucket_info = check_bucket(
        storage_client = storage_client,
        bucket_name = storage_name
    )

    job_prefix = set_object_path(
        object_name = 'root',
        path_replacers = {
            'name': 'JOBS'
        },
        path_names = []
    )

    submitter_bucket_objects = submitter_bucket_info['objects']
    
    job_objects = {}
    for object_path in submitter_bucket_objects.keys():
        if job_prefix in object_path:
            path_split = object_path.split('/')
            job_key = path_split[-1]

            if job_key.isnumeric():
                job_object = get_object(
                    storage_client = storage_client,
                    bucket_name = storage_name,
                    object_name = 'jobs',
                    path_replacers = {
                        'name': job_key
                    },
                    path_names = []
                )

                stored_data = {
                    'data': job_object['data'],
                    'metadata': job_object['custom-meta']
                }

                job_objects[job_key] = stored_data
            
    return job_objects

def get_supercomputer_jobs(
    platform_secrets: any
):
    print('Get squeue')
    job_dict = get_squeue(
        platform_secrets = platform_secrets
    )
    
    state_codes = get_slurm_job_states()
    pending_states = get_slurm_pending_states()
    running_states = get_slurm_running_states()
    failure_states = get_slurm_failure_states()
    completion_states = get_slurm_completion_states()

    job_info = {}
    print('id|state|elapsed|parition')
    for key in job_dict.keys():
        id = job_dict[key]['JOBID']
        state = state_codes[job_dict[key]['ST']]
        elapsed = job_dict[key]['TIME']
        partition = job_dict[key]['PARTITION']
        
        print(str(id) + '|' + str(state) + '|' + str(elapsed) + '|' + str(partition))

        formatted_state = ''
        if state in pending_states:
            formatted_state = 'pending'
        if state in running_states:
            formatted_state = 'running'
        if state in failure_states:
            # Since squeue jobs 
            # are either pending 
            # or running, this can 
            # only be checked with sacct
            formatted_state = 'failed'
        if state in completion_states:
            # Since squeue jobs 
            # are either pending 
            # or running, this can 
            # only be checked with sacct
            formatted_state = 'complete'

        job_info[id] = {
            'state': formatted_state,
            'elapsed': elapsed,
            'partition': partition
        }
    return job_info