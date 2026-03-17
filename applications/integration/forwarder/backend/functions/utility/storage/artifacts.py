from functions.utility.storage.objects import get_object
from functions.utility.storage.management import get_user_bucket_name
from functions.platforms.slurm import parse_sacct_dict, parse_seff_dict

def get_job_status(
    storage_client: any,
    bucket_parameters: any,
    request: any
) -> any:
    submitter_bucket_name = get_user_bucket_name(
        target = 'submitter',
        bucket_parameters = bucket_parameters
    )
    
    job_status_object = get_object(
        storage_client = storage_client,
        bucket_name = submitter_bucket_name,
        object_name = 'jobs',
        path_replacers = {
            'name': request['key']
        }, 
        path_names = []
    )

    job_status = {'job-status': {}}
    if not len(job_status_object) == 0:
        job_status_data = job_status_object['data']
        job_status['job-status'] = job_status_data
    return job_status

def get_job_sacct(
    storage_client: any,
    bucket_parameters: any,
    request: str
) -> any:
    submitter_bucket_name = get_user_bucket_name(
        target = 'submitter',
        bucket_parameters = bucket_parameters
    )

    job_sacct_object = get_object(
        storage_client = storage_client,
        bucket_name = submitter_bucket_name,
        object_name = 'job-sacct',
        path_replacers = {
            'name': request['key']
        }, 
        path_names = []
    )

    job_sacct = {'job-sacct': {}}
    if not len(job_sacct_object) == 0:
        job_sacct_data = job_sacct_object['data']
        key = 1
        for sample in job_sacct_data.values():
            formatted_metrics, formatted_metadata = parse_sacct_dict(
                sacct_data = sample
            )
            job_sacct['job-sacct'][str(key)] = {
                'metrics': formatted_metrics,
                'metadata': formatted_metadata
            }
            key += 1
    return job_sacct

def get_job_seff(
    storage_client: any,
    bucket_parameters: any,
    request: str
) -> any:
    submitter_bucket_name = get_user_bucket_name(
        target = 'submitter',
        bucket_parameters = bucket_parameters
    )

    job_seff_object = get_object(
        storage_client = storage_client,
        bucket_name = submitter_bucket_name,
        object_name = 'job-seff', 
        path_replacers = {
            'name': request['key']
        }, 
        path_names = []
    )

    job_seff = {'job-seff': {}}
    if not len(job_seff_object) == 0:
        sample = job_seff_object['data']
        formatted_metrics, formatted_metadata = parse_seff_dict(
            seff_data = sample
        )
        job_seff['job-seff']['metrics'] = formatted_metrics
        job_seff['job-seff']['metadata'] = formatted_metadata
    return job_seff

def get_job_files(
    storage_client: any,
    bucket_parameters: any,
    request: any
) -> any:
    submitter_bucket_name = get_user_bucket_name(
        target = 'submitter',
        bucket_parameters = bucket_parameters
    )

    job_status_object = get_object(
        storage_client = storage_client,
        bucket_name = submitter_bucket_name,
        object_name = 'jobs',
        path_replacers = {
            'name': request['key']
        }, 
        path_names = []
    )

    job_files = {'job-files': {}}
    if not len(job_status_object) == 0:
        job_status_data = job_status_object['data']
        if job_status_data['stored']:
            job_stored_files = job_status_data['files']['store']
            for file_info in job_stored_files:
                file_target_split = file_info['target'].split('/')
                file_enviroment = file_target_split[0]
                file_platform = file_target_split[1]
                if file_enviroment == 'storage':
                    if file_platform == 'allas':
                        # Its unknown if large files 
                        # can be fetched this way
                        file_bucket = get_user_bucket_name(
                            target = file_target_split[2],
                            bucket_parameters = bucket_parameters
                        )
                        file_path = file_target_split[3:]
                        job_files['job-files'][file_path[-2]] = {}
                        file_object = get_object(
                            storage_client = storage_client,
                            bucket_name = file_bucket,
                            object_name = 'root',
                            path_replacers = {
                                'name': file_path[0]
                            },
                            path_names = file_path[1:]
                        )
                        job_files['job-files'][file_path[-2]][file_path[-1]] = file_object['data']
    return job_files

def get_forwarding_status(
    storage_client: any,
    storage_name: any,
    bucket_parameters: any,
    request: any
) -> any:
    submitter_bucket_name = get_user_bucket_name(
        target = 'submitter',
        bucket_parameters = bucket_parameters
    )
    # Concurrency source
    forwarding_status_object = get_object(
        storage_client = storage_client,
        bucket_name = storage_name,
        object_name = request['forwarding-type'],
        path_replacers = {
            'name': submitter_bucket_name
        },
        path_names = [
            request['key']
        ]
    )

    forwarding_status = {'forwarding-status':{}}
    if not 0 == len(forwarding_status_object):
        forwarding_status_data = forwarding_status_object['data']
        forwarding_status['forwarding-status'] = forwarding_status_data
    return forwarding_status