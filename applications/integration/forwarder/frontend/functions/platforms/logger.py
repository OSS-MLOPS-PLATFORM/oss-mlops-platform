import os
import logging

def initilized_logger(
    log_path: str,
    logger_name: str
):
    log_path_split = log_path.split('/')
    folder_path = '/'.join(log_path_split[:-1])
    os.makedirs(folder_path, exist_ok=True)
    if os.path.exists(log_path):
        os.remove(log_path)
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)
    file_handler = logging.FileHandler(log_path)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger

def get_logs(
    log_path: str
):
    listed_logs = {'logs':[]}
    with open(log_path, 'r') as f:
        for line in f:
            listed_logs['logs'].append(line.strip())
    return listed_logs