import re

def format_python_version(
    resulted_print: str
) -> any:
    formatted_version = resulted_print.split('\n')[:-1][0]
    version = None
    if 'Python' in formatted_version:
        version = formatted_version.split(' ')[1]
        version = version.split('.')
    return version

def format_venv_packages(
    resulted_print: str
) -> any:
    formatted_list = resulted_print.split('\n')
    venv_packages = {}
    index = 0
    for row in formatted_list:
        if 0 == len(row):
            continue
        if 1 < index:
            empty_split = row.split(' ')
            package = empty_split[0]
            version = empty_split[-1]
            venv_packages[package] = version
        index += 1
    return venv_packages

def check_missing_packages(
    installed_packages: any,
    wanted_packages: any
) -> any:
    missing_packages = []
    for package_info in wanted_packages:
        used_package_info = package_info
        if '-f' in used_package_info:
            used_package_info = used_package_info.replace(' ', '')
            used_package_info = used_package_info.split('-f')[0]
        if '"' in used_package_info:
            used_package_info = used_package_info.replace('"','')
        if '[' in package_info:    
            used_package_info = re.sub(r'\[.*\]', '', used_package_info)
        if '==' in used_package_info:
            info_split = used_package_info.split('==')
            formatted_name = info_split[0]
            formatted_version = info_split[1]
        else:
            formatted_name = used_package_info
            formatted_version = None
        
        if not formatted_name in installed_packages:
            missing_packages.append(package_info)
        else:
            if not formatted_version is None:
                if not installed_packages[formatted_name] == formatted_version:
                    missing_packages.append(package_info)
    return missing_packages

def format_package_installation(
    wanted_packages: any
) -> any:
    install_separation = []
    line_packages = ''
    for package in wanted_packages:
        if '-f' in package:
            if 0 < len(line_packages):
                install_separation.append(line_packages)
                line_packages = ''
            install_separation.append(package + ' ')
            continue
        line_packages += package + ' '
    if 0 < len(line_packages):
        install_separation.append(line_packages)
    return install_separation

def check_venv_creation(
    resulted_prints: str
) -> bool:
    success = False
    for resulted_print in resulted_prints:
        row_split = resulted_print .split('\n')
        for row in row_split:
            if 0 == len(row):
                continue
            if 'Successfully installed' in row:
                success = True
    return success

def check_venv_package_installation(
    resulted_prints: str
) -> bool:
    success = True
    for resulted_print in resulted_prints:
        row_split = resulted_print.split('\n')
        for row in row_split:
            if 0 == len(row):
                continue
            if 'error' in row:
                success = False
    return success