

import re
import yaml 

import markdown
from bs4 import BeautifulSoup

from functions.formatting import extract_yaml_values, extract_jupyter_notebook_markdown_and_code, parse_jupyter_notebook_markdown_into_text
from functions.tree_sitter import tree_create_python_code_and_function_documents

def create_markdown_documents(
    markdown_text: any
) -> any:
    html = markdown.markdown(markdown_text)
    soup = BeautifulSoup(html, features='html.parser')
    code_block_pattern = re.compile(r"```")
    
    documents = []
    document = ''
    index = 1
    for element in soup.descendants:
        if element.name in ['h2', 'h3', 'h4', 'h5', 'h6']:
            text = element.get_text(strip = True)
            if not document == '':
                document = document.replace('\n', '')
                if not len(document.split()) == 1:
                    documents.append({
                        'index': index,
                        'sub-index': 0,
                        'type': 'markdown',
                        'data': document
                    })
                    index += 1
                document = ''
            document += text
        elif element.name == 'p':
            text = element.get_text(strip = True)
            text = re.sub(code_block_pattern, '', text)
            text = text.rstrip('\n')
            text = text.replace('\nsh', '')
            text = text.replace('\nbash', '')
            document += ' ' + text
        elif element.name in ['ul', 'ol']:
            text = ''
            for li in element.find_all('li'):
                item = li.get_text(strip=True)
                if not '-' in item:
                    text += '-' + item
                    continue
                text += item
            document += ' ' + text
            
    documents.append({
        'index': index,
        'sub-index': 0,
        'type': 'markdown',
        'data': document
    })
    
    formatted_documents = {
        'text': documents
    }
    
    return formatted_documents

def create_yaml_documents(
    yaml_text: any
) -> any:
    yaml_data = list(yaml.safe_load_all(yaml_text))

    documents = []
    index = 1
    for data in yaml_data:
        yaml_values = extract_yaml_values(
            section = data,
            path = '',
            values = []
        )

        previous_root = ''
        document = ''
        sub_index = 1
        for value in yaml_values:
            equal_split = value.split('=')
            path_split = equal_split[0].split('/')
            root = path_split[0]
            if not root == previous_root:
                if 0 < len(document):
                    documents.append({
                        'index': index,
                        'sub-index': sub_index,
                        'type': 'yaml',
                        'data': document
                    })
                    sub_index += 1
                    
                previous_root = root
                document = value
            else:
                document += value
                
        documents.append({
            'index': index,
            'sub-index': sub_index,
            'type': 'yaml',
            'data': document
        })
        index += 1

    formatted_documents = {
        'text': documents
    }
            
    return formatted_documents

def create_python_documents(
    python_text: any
): 
    joined_code = ''.join(python_text)
    block_code_documents = tree_create_python_code_and_function_documents(
        code_document = joined_code
    )
    
    code_documents = []
    seen_function_names = []
    code_doc_index = 0
    for code_doc in block_code_documents:
        row_split = code_doc.split('\n')
        for row in row_split:
            if 'function' in row and 'code' in row:
                # This causes problems with some documents
                # list index out of range
                function_name = row.split(' ')[1]
                if not function_name in seen_function_names:
                    seen_function_names.append(function_name)
                else:
                    del block_code_documents[code_doc_index]
        code_doc_index += 1
    
    if 0 < len(block_code_documents):
        index = 1
        for code_doc in block_code_documents:
            code_documents.append({
                'index': index,
                'sub-index': 0,
                'type': 'python',
                'data': code_doc
            })
            index += 1
   
    formatted_documents = {
        'code': code_documents
    }
    return formatted_documents

def create_notebook_documents(
    notebook_text: any
):
    notebook_documents = extract_jupyter_notebook_markdown_and_code(
        notebook_text = notebook_text
    )
    
    markdown_documents = []
    for block in notebook_documents['markdown']:
        joined_text = ''.join(block['data'])
        markdown_text = parse_jupyter_notebook_markdown_into_text(
            markdown_text = joined_text
        )
        markdown_documents.append({
            'index': block['id'],
            'sub-index': 0,
            'type': 'markdown',
            'data': markdown_text
        })
    
    code_documents = []
    seen_function_names = []
    for block in notebook_documents['code']:
        joined_code = ''.join(block['data'])
        block_code_documents = tree_create_python_code_and_function_documents(
            code_document = joined_code
        )

        code_doc_index = 0
        for code_doc in block_code_documents:
            row_split = code_doc.split('\n')
            for row in row_split:
                if 'function' in row and 'code' in row:
                    # This causes problems with some documents
                    # list index out of range
                    function_name = row.split(' ')[1]
                    if not function_name in seen_function_names:
                        seen_function_names.append(function_name)
                    else:
                        del block_code_documents[code_doc_index]
            code_doc_index += 1
        
        if 0 < len(block_code_documents):
            sub_indexes = False
            if 1 < len(block_code_documents):
                sub_indexes = True
            index = 1
            for code_doc in block_code_documents:
                if sub_indexes:
                    code_documents.append({
                        'index': block['id'],
                        'sub-index': index, 
                        'type': 'python',
                        'data': code_doc
                    })
                else:
                    code_documents.append({ 
                        'index': block['id'],
                        'sub-index': 0,
                        'type': 'python',
                        'data': code_doc
                    })
                index += 1
    
    formatted_documents = {
        'text': markdown_documents,
        'code': code_documents
    }
    
    return formatted_documents
