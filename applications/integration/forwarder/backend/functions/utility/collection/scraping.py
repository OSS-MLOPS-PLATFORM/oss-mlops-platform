from functions.platforms.slurm import parse_sacct_dict, parse_seff_dict

def scrape_sacct(
    prometheus_gauge: any,
    artifact_key: str,
    user: str,
    metric_names: any,
    data: any
):
    for row, sample in data.items():
        formatted_metrics, formatted_metadata = parse_sacct_dict(
            sacct_data = sample
        )
        
        if 'partition' in formatted_metadata:
            partition = formatted_metadata['partition']
        else:
            formatted_metadata['partition'] = partition

        job_user = str(user)
        job_key = str(artifact_key)
        sacct_row = str(row)
        job_id = str(formatted_metadata['job-id'])
        job_name = str(formatted_metadata['job-name'])
        job_partition = str(formatted_metadata['partition'])
        job_state = str(formatted_metadata['state'])

        for key, value in formatted_metrics.items():
            metric_name = metric_names[key]
            prometheus_gauge.labels(
                user = job_user,
                jobkey = job_key,
                jobid = job_id,
                row = sacct_row,
                jobname = job_name,
                partition = job_partition,
                state = job_state,
                metric = metric_name
            ).set(value)
 
def scrape_seff(
    prometheus_gauge: any,
    artifact_key: str,
    user: str,
    metric_names: any,
    data: any    
):
    formatted_metrics, formatted_metadata = parse_seff_dict(
        seff_data = data
    )
     
    job_user = str(user)
    job_key = str(artifact_key)
    job_id = str(formatted_metadata['job-id'])
    job_cluster = str(formatted_metadata['cluster'])
    job_project = str(formatted_metadata['billed-project'])
    job_state = str(formatted_metadata['status'])
    status = str(formatted_metadata['status'])
    exit_code = str(formatted_metadata['exit-code'])
    job_state = status + '-' + exit_code

    for key, value in formatted_metrics.items():
        metric_name = metric_names[key]
        prometheus_gauge.labels(
            user = job_user,
            jobkey = job_key,
            jobid = job_id,
            project = job_project,
            cluster = job_cluster, 
            state = job_state,
            metric = metric_name
        ).set(value)        

def scrape_job_time(
    prometheus_gauge: any,
    collector: str,
    job_key: str,
    metric_names: any,
    data: any
):
    for key, value in data.items():
        if 'total' in key: 
            metric_name = metric_names[key]
            prometheus_gauge.labels(
                collector = collector,
                jobkey = job_key,
                metric = metric_name
            ).set(value)   

def scrape_pipeline_time(
    prometheus_gauge: any,
    collector: str,
    time_group: str,
    metric_names: any,
    data: any
):
    for time_id, time_info in data.items():
        time_name = time_info['name']
        for key, value in time_info.items():
            if 'total' in key:
                metric_name = metric_names[key]
                prometheus_gauge.labels(
                    collector = collector,
                    sampleid = time_id,
                    group = time_group,
                    name = time_name,
                    metric = metric_name
                ).set(value)  

def scrape_task_time(
    prometheus_gauge: any,
    collector: str,
    time_group: str,
    metric_names: any,
    data: any
):
    for task_id, time_info in data.items():
        for key, value in time_info.items():
            if 'total' in key: 
                metric_name = metric_names[key]
                prometheus_gauge.labels(
                    collector = collector, 
                    sampleid = task_id,
                    group = time_group,
                    metric = metric_name
                ).set(value)  