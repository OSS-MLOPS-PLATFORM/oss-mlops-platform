from prometheus_client import CollectorRegistry, multiprocess

from functions.platforms.prometheus import set_prometheus_gauge
from functions.utility.storage.gauges import get_sacct_gauge_structure, get_seff_gauge_structure, get_job_time_gauge_structure, get_pipeline_time_gauge_structure, get_task_time_gauge_structure
from functions.utility.collection.artifacts import gather_artifacts
from functions.utility.collection.times import gather_times
from functions.utility.collection.scraping import scrape_sacct,scrape_seff, scrape_job_time, scrape_pipeline_time, scrape_task_time

global_registry = CollectorRegistry()
multiprocess.MultiProcessCollector(global_registry)

sacct_gauge = set_prometheus_gauge(
    prometheus_registry = global_registry,
    gauge_structure = get_sacct_gauge_structure()
)

seff_gauge = set_prometheus_gauge(
    prometheus_registry = global_registry,
    gauge_structure = get_seff_gauge_structure()
)

job_time_gauge = set_prometheus_gauge(
    prometheus_registry = global_registry,
    gauge_structure = get_job_time_gauge_structure()
)

pipeline_time_gauge = set_prometheus_gauge(
    prometheus_registry = global_registry,
    gauge_structure = get_pipeline_time_gauge_structure()
)

task_time_gauge = set_prometheus_gauge(
    prometheus_registry = global_registry,
    gauge_structure = get_task_time_gauge_structure()
)

def utilize_artifacts(
    storage_client: any, 
    storage_name: str,
    type: str
):
    submitters_artifacts = gather_artifacts(
        storage_client = storage_client,
        storage_name = storage_name,
        type = type
    )

    gauge_structure = {}
    prometheus_gauge = None
    if type == 'sacct':
        gauge_structure = get_sacct_gauge_structure()
        prometheus_gauge = sacct_gauge
    if type == 'seff':
        gauge_structure = get_seff_gauge_structure()
        prometheus_gauge = seff_gauge
    if 0 < len(submitters_artifacts):
        if 0 < len(gauge_structure):
            for submitter_name, artifacts in submitters_artifacts.items():
                for artifact_key, artifact in artifacts.items():
                    submitter_name_split = submitter_name.split('-')
                    submitter_user = '-'.join(submitter_name_split[5:])
                    if type == 'sacct':
                        scrape_sacct(
                            prometheus_gauge = prometheus_gauge,
                            artifact_key = artifact_key,
                            user = submitter_user,
                            metric_names = gauge_structure['names'],
                            data = artifact
                        )
                    if type == 'seff':
                        scrape_seff(
                            prometheus_gauge = prometheus_gauge,
                            artifact_key = artifact_key,
                            user = submitter_user,
                            metric_names = gauge_structure['names'],
                            data = artifact
                        )  

def utilize_time(
    storage_client: any, 
    storage_name: str,
    type: str
): 
    time_artifacts = gather_times(
        storage_client = storage_client,
        storage_name = storage_name,
        type = type
    ) 
    
    gauge_structure = {}
    prometheus_gauge = None
    if type == 'job-time':
        gauge_structure = get_job_time_gauge_structure()
        prometheus_gauge = job_time_gauge
    if type == 'pipeline-time':
        gauge_structure = get_pipeline_time_gauge_structure()
        prometheus_gauge = pipeline_time_gauge
    if type == 'task-time':
        gauge_structure = get_task_time_gauge_structure()
        prometheus_gauge = task_time_gauge
    if 0 < len(time_artifacts):
        if 0 < len(gauge_structure):
            for collector_name, artifacts in time_artifacts.items():
                for artifact_name, artifact in artifacts.items():
                    if type == 'job-time':
                        scrape_job_time(
                            prometheus_gauge = prometheus_gauge,
                            collector = collector_name,
                            job_key = artifact_name,
                            metric_names = gauge_structure['names'],
                            data = artifact
                        )
                    if type == 'pipeline-time':
                        scrape_pipeline_time(
                            prometheus_gauge = prometheus_gauge,
                            collector = collector_name,
                            time_group = artifact_name,
                            metric_names = gauge_structure['names'],
                            data = artifact
                        )
                    if type == 'task-time': 
                        scrape_task_time(
                            prometheus_gauge = prometheus_gauge,
                            collector = collector_name,
                            time_group = artifact_name,
                            metric_names = gauge_structure['names'],
                            data = artifact
                        )