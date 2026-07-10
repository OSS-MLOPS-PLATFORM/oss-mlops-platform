
from functions.utility.storage.objects import set_object
from functions.utility.storage.data import job_status_communication_object_data, job_time_communication_object_data
from functions.utility.storage.metadata import general_object_metadata

def get_template_structure():
    template_structure = {
        'object-store': {
            'submitter-status': {
                'object-name': 'jobs',
                'path-replacers': {
                    'name': 'status-template'
                },
                'path-names': [],
                'data': job_status_communication_object_data(),
                'metadata': general_object_metadata()
            },
            'job-times': {
                'object-name': 'job-time', 
                'path-replacers': {
                    'name': 'time-template'
                },
                'path-names': [],
                'data': job_time_communication_object_data(),
                'metadata': general_object_metadata()
            }
        }
    }
    return template_structure

def set_object_templates(
    storage_client: any,
    bucket_name: str,
    templates: any
):
    for template_name in templates.keys():
        object_name = templates[template_name]['object-name']
        path_replacers = templates[template_name]['path-replacers']
        path_names = templates[template_name]['path-names']
        object_data = templates[template_name]['data']
        object_metadata = templates[template_name]['metadata']
        
        set_object(
            storage_client = storage_client,
            bucket_name = bucket_name,
            object_name = object_name,
            path_replacers = path_replacers,
            path_names = path_names,
            overwrite = False,
            object_data = object_data,
            object_metadata = object_metadata
        )

def store_templates(
    storage_clients: any,
    storage_names: any,
    storage_parameters: any
):
    template_structure = get_template_structure()

    for template_storage, templates in template_structure.items():
        if not len(storage_parameters[template_storage]) == 0 and not len(templates) == 0:
            if template_storage == 'object-store':
                set_object_templates(
                    storage_client = storage_clients[0],
                    bucket_name = storage_names[0],
                    templates = templates
                )
