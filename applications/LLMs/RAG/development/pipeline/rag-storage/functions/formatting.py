
import re
import markdown
import nbformat

from bs4 import BeautifulSoup

def extract_yaml_values(
    section: any,
    path: str,
    values: any
) -> any:
    for key, value in section.items():
        if path == '':
            current_path = key
        else:
            current_path = path + '/' + key
        if isinstance(value, dict):
            extract_yaml_values(
                section = value,
                path = current_path,
                values = values
            )
        if isinstance(value, list):
            number = 1
            
            for case in value:
                base_path = current_path
                if isinstance(case, dict):
                   extract_yaml_values(
                       section = case,
                       path = current_path,
                       values = values
                   ) 
                   continue
                base_path += '/' + str(number)
                number += 1
                values.append(base_path + '=' + str(case))
        else:
            if isinstance(value, dict):
                continue
            if isinstance(value, list):
                continue
            values.append(current_path + '=' + str(value))
            
    return values

def parse_jupyter_notebook_markdown_into_text(
    markdown_text: any
) -> any:
    html = markdown.markdown(markdown_text)
    soup = BeautifulSoup(html, features='html.parser')
    text = soup.get_text()
    code_block_pattern = re.compile(r"```")
    text = re.sub(code_block_pattern, '', text)
    text = text.rstrip('\n')
    text = text.replace('\nsh', '\n')
    text = text.replace('\nbash', '\n')
    return text

def extract_jupyter_notebook_markdown_and_code(
    notebook_text: any
): 
    notebook_documents = {
        'markdown': [],
        'code': []
    }

    notebook = nbformat.reads(notebook_text, as_version=2)
    index = 1
    for cell in notebook.worksheets[0].cells:
        if cell.cell_type == 'markdown':
            notebook_documents['markdown'].append({
                'id': index,
                'data': cell.source
            })
            index += 1
        if cell.cell_type == 'code':
            notebook_documents['code'].append({
                'id': index,
                'data': cell.input
            })
            index += 1
    
    return notebook_documents
