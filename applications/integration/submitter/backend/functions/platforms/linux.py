def format_pwd_directory(
    resulted_print: str
) -> str:
    formatted_version = resulted_print.split('\n')[:-1][0]
    directory = None
    if '/' in formatted_version:
        directory = formatted_version
    return directory

def format_folders_and_files(
    resulted_print: str
) -> str:
    formatted_names = resulted_print.split('\n')[:-1]
    folders = []
    files = []
    for name in formatted_names:
        if '.' in name:
            files.append(name)
        else:
            folders.append(name)
    return folders, files   