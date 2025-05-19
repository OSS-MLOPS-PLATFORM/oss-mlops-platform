def format_supercomputer_workspace(
    resulted_print: str
) -> any:
    row_format = resulted_print.split('\n')
    workspace = {}
    if 0 < len(row_format):
        valid_rows = [
            '/users/',
            '/projappl/',
            '/scratch/'
        ]
        workspace = {}
        for row in row_format:
            for valid_row in valid_rows:
                if valid_row in row:
                    empty_split = row.split(' ')
                    index = 0
                    area = ''
                    folder = ''
                    for case in empty_split:
                        if len(case) == 0:
                            continue
                        if '/' in case[0]:
                            path_split = case.split('/')
                            if not path_split[1] in workspace:
                                workspace[path_split[1]] = {}
                            workspace[path_split[1]][path_split[2]] = {
                                'used-capacity': None,
                                'max-capacity': None,
                                'used-files': None,
                                'max-files': None,
                                'description': None
                            }
                            area = path_split[1]
                            folder = path_split[2]
                            index = 0
                            continue
                        if '/' in case:
                            path_split = case.split('/')
                            if index == 0:
                                workspace[area][folder]['used-capacity'] = path_split[0]
                                workspace[area][folder]['max-capacity'] = path_split[1]
                            if index == 1:
                                workspace[area][folder]['used-files'] = path_split[0]
                                workspace[area][folder]['max-files'] = path_split[1]
                        if index == 2:
                            workspace[area][folder]['description'] = case
                        index += 1
    return workspace