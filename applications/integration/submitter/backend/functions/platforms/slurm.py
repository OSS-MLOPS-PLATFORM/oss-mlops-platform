import re
from datetime import datetime
from functions.utility.general import convert_into_seconds,unit_converter

def format_slurm_sbatch(
    resulted_print: str   
) -> str:
    job_id = resulted_print.split(' ')[-1]
    job_id = job_id.replace('\n','')
    return job_id

def check_slurm_scancel(
    resulted_print: str 
) -> bool: 
    if len(resulted_print) == 0:
        return True
    return False

def get_slurm_job_states():
    state_codes = {
        'BF': 'BOOT FAIL',
        'CA': 'CANCELLED',
        'CD': 'COMPLETED',
        'CF': 'CONFIGURING',
        'CG': 'COMPLETING',
        'DL': 'DEADLINE',
        'F': 'FAILED',
        'NF': 'NODE FAIL',
        'OOM': 'OUT OF MEMORY',
        'PD': 'PENDING',
        'PR': 'PREEMPTED',
        'R': 'RUNNING',
        'RD': 'RESERVATION DELETION HOLD',
        'RF': 'REQUEUE FEDERATION',
        'RH': 'REQUEUE HOLD',
        'RQ': 'REQUEUED',
        'RS': 'RESIZING',
        'RV': 'REVOKED',
        'SI': 'SIGNALING',
        'SE': 'SPECIAL EXIT',
        'SO': 'STAGE OUT',
        'ST': 'STOPPED',
        'S': 'SUSPENDED',
        'TO': 'TIMEOUT'
    }
    return state_codes

def get_slurm_pending_states():
    pending_states = [
        'PENDING',
        'CONFIGURING',
        'REQUEUE FEDERATION',
        'REQUEUE HOLD',
        'REQUEUED',
        'RESIZING',
        'STAGE OUT'
    ]
    return pending_states

def get_slurm_running_states():
    running_states = [
        'RUNNING',
        'SIGNALING'
    ]
    return running_states

def get_slurm_failure_states():
    failure_states = [
        'BOOT FAIL',
        'OUT OF MEMORY',
        'NODE FAIL',
        'REVOKED'
    ]
    return failure_states

def get_slurm_completion_states():
    completion_states = [
        'COMPLETED',
        'DEADLINE',
        'CANCELLED',
        'COMPLETING',
        'TIMEOUT',
        'SPECIAL EXIT',
        'PREEMPTED',
        'RESERVATION DELETION HOLD',
        'STOPPED',
        'SUSPENDED'
    ]
    return completion_states

def format_slurm_squeue(
    file_path: str,
    resulted_print: any
) -> any:
    with open(file_path, 'w') as f:
        f.write(resulted_print)

    squeue_text = None
    with open(file_path, 'r') as f:
        squeue_text = f.readlines()

    values_dict = {}
    if not squeue_text is None:
        row_list = []
        for line in squeue_text:
            row = line.split(' ')
            filtered_row = [s for s in row if s != '']
            if not len(row) == 1:
                filtered_row[-1] = filtered_row[-1].replace('\n','')
                row_list.append(filtered_row)
        
        header_dict = {}
        i = 1
        for key in row_list[0]:
            header_dict[str(i)] = key
            i = i + 1

        if 1 < len(row_list):
            i = 1
            for values in row_list[1:]:
                j = 1
                values_dict[i] = {}
                for value in values:
                    key = header_dict[str(j)]
                    values_dict[i][key] = value
                    j = j + 1
                i = i + 1 
    return values_dict

def format_slurm_sacct(
    file_path: str,
    resulted_print: any
) -> any: 
    with open(file_path, 'w') as f:
        f.write(resulted_print)

    sacct_text = None
    with open(file_path, 'r') as f:
        sacct_text = f.readlines()

    values_dict = {}
    if not sacct_text is None:
        header = sacct_text[0].split(' ')[:-1]
        columns = [s for s in header if s != '']

        spaces = sacct_text[1].split(' ')[:-1]
        space_sizes = []
        for space in spaces:
            space_sizes.append(len(space))

        rows = sacct_text[2:]
        if 1 < len(sacct_text):
            for i in range(1,len(rows) + 1):
                values_dict[str(i)] = {} 
                for column in columns:
                    values_dict[str(i)][column] = ''
            i = 1
            for row in rows:
                start = 0
                end = 0
                j = 0
                
                for size in space_sizes:
                    end += size
                    formatted_value = [s for s in row[start:end].split(' ') if s != '']
                    column_value = None
                    if 0 < len(formatted_value):
                        column_value = formatted_value[0] 
                    column = columns[j]
                    values_dict[str(i)][column] = column_value
                    start = end
                    end += 1
                    j += 1
                i += 1
    return values_dict

def format_slurm_seff(
    file_path: str,
    resulted_print: any
) -> any:
    with open(file_path, 'w') as f:
        f.write(resulted_print)

    seff_text = None
    with open(file_path, 'r') as f:
        seff_text = f.readlines()

    values_dict = {}
    if not seff_text is None:
        for line in seff_text:
            if not ':' in line:
                continue 
            filtered = line.replace('\n','')
            
            landmark_indexes = [idx for idx, item in enumerate(filtered.lower()) if ':' in item]
            
            key = filtered[:landmark_indexes[0]]
            value = filtered[landmark_indexes[0]+2:] 

            values_dict[key] = value
    return values_dict

def format_slurm_logs(
    file_path: str
) -> any:
    log_text = None
    with open(file_path, 'r') as f:
        log_text = f.readlines()
    
    row_list = []
    if not log_text is None:
        for line in log_text:
            filter_1 = line.replace('\n', '')
            filter_2 = filter_1.replace('\t', ' ')
            filter_3 = filter_2.replace('\x1b', ' ')
            row_list.append(filter_3)
    return row_list 

def sacct_metric_formatting(
    metric: str
) -> any:
    formatted_name = ''
    first = True
    index = -1
    for character in metric:
        index += 1
        if character.isupper():
            if first:
                first = False
                formatted_name += character
                continue
            if index + 1 < len(metric): 
                if metric[index - 1].islower():
                    formatted_name += '-' + character
                    continue
                if metric[index - 1].isupper() and metric[index + 1].islower():
                    formatted_name += '-' + character
                    continue
        formatted_name += character 
    return formatted_name

def parse_sacct_dict(
    sacct_data:any
):
    formatted_data = {}

    metric_units = {
        'ave-cpu': 'seconds',
        'ave-cpu-freq': 'khz',
        'ave-disk-read': 'bytes',
        'ave-disk-write': 'bytes',
        'timelimit': 'seconds',
        'elapsed': 'seconds',
        'planned': 'seconds',
        'planned-cpu': 'seconds',
        'cpu-time': 'seconds',
        'total-cpu': 'seconds',
        'submit': 'time',
        'start': 'time',
        'end': 'time'
    }
   
    for key,value in sacct_data.items():
        spaced_key = sacct_metric_formatting(
            metric = key
        )
        formatted_key = spaced_key.lower()
        
        if formatted_key in metric_units:
            formatted_key += '-' + metric_units[formatted_key]
        
        formatted_data[formatted_key] = value

    ignore = [
        'account'
    ]
    
    metadata = [
        'job-name',
        'job-id',
        'partition',
        'state'
    ]
    
    parsed_metrics = {}
    parsed_metadata = {}
    
    for key in formatted_data.keys():
        key_value = formatted_data[key]

        if key_value is None:
            continue

        if key in ignore:
            continue

        if key in metadata:
            if key == 'job-id':
                key_value = key_value.split('.')[0]
            parsed_metadata[key] = key_value
            continue
        
        if ':' in key_value:
            if 'T' in key_value:
                format = datetime.strptime(key_value, '%Y-%m-%dT%H:%M:%S')
                key_value = round(format.timestamp())
            else:
                key_value = convert_into_seconds(
                    given_time = key_value
                )
        else:
            if 'bytes' in key_value:
                key_value = unit_converter(
                    value = key_value,
                    bytes = True
                )
            else:
                key_value = unit_converter(
                    value = key_value,
                    bytes = False
                )
        parsed_metrics[key] = key_value
    return parsed_metrics, parsed_metadata

def parse_seff_dict(
    seff_data: any
):
    parsed_data = {}
    for metric in seff_data.keys():
        formatted_key = re.sub(r'\([A-Z]*\)','',metric).lower().replace(' ','-').replace('/','-')
        value = seff_data[metric]
        
        if 'of' in str(value):
            value_split = value.split('of')
            percentage = value_split[0].replace(' ', '')
            amount = value_split[1].replace(' ', '')
            parsed_data[formatted_key + '-percentage'] = re.sub(r'[%]*','',percentage)
            formatted_value = re.sub(r'[A-Za-z-]*','',amount)
            if ':' in formatted_value:
                parsed_data[formatted_key + '-seconds'] = convert_into_seconds(
                    given_time = formatted_value
                )
                continue
            if 'memory' in formatted_key:
                converted_value = unit_converter(
                    value = amount,
                    bytes = True
                )
                parsed_data[formatted_key + '-bytes'] = converted_value
                continue
            parsed_data[formatted_key + '-amount'] = formatted_value
            continue
            
        if ':' in str(value):
            parsed_data[formatted_key + '-seconds'] = convert_into_seconds(
                given_time = value
            )
            continue
        
        if 'state' in formatted_key:
            value_split = value.split(' ')
            status = value_split[0]
            exit_code = value_split[-1][:-1]
            parsed_data['status'] = status
            parsed_data['exit-code'] = exit_code
            continue
            
        if 'non-interactive-bus' in formatted_key:
            parsed_data['billing-units'] = value
            continue
            
        if 'memory' in formatted_key:
            amount = value.replace(' ', '')
            converted_value = unit_converter(
                value = amount,
                bytes = True
            )
            parsed_data[formatted_key + '-bytes'] = converted_value
            continue
           
        parsed_data[formatted_key] = value
                
    ignore = [
        'user-group'
    ]
    
    metadata = [
        'billed-project',
        'job-id',
        'cluster',
        'status',
        'exit-code'
    ]
    
    parsed_metadata = {}
    parsed_metrics = {}
    for key in parsed_data.keys():
        if key in ignore:
            continue
        if key in metadata:
            parsed_metadata[key] = parsed_data[key]
            continue
        parsed_metrics[key] = parsed_data[key]
    return parsed_metrics, parsed_metadata