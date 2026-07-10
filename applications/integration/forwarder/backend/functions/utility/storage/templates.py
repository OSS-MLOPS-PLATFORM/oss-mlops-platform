from functions.utility.storage.data import *
from functions.utility.storage.metadata import general_object_metadata
from functions.utility.storage.objects import set_object

def get_template_structure():
    template_structure = {
            'object-store': {
                'forwarding-status': {
                    'object-name': 'root',
                    'path-replacers': {
                        'name': 'FORWARDS'
                    },
                    'path-names': [
                        'status-template'
                    ],
                    'data': forwarding_status_communication_object_data(),
                    'metadata': general_object_metadata()
                },
                'monitoring-index': {
                    'object-name': 'monitor',
                    'path-replacers': {
                        'name': 'index-template'
                    }, 
                    'path-names': [],
                    'data': collection_index_communication_object(),
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