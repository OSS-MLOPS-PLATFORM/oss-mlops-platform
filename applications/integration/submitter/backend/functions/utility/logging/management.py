from functions.utility.logging.tasks import store_tasks

def collect_logs(
    storage_client: any,
    storage_name: str
):
    store_tasks(
        storage_client = storage_client,
        storage_name = storage_name
    )