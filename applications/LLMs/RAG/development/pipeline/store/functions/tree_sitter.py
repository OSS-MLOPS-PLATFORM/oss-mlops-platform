
import re

import tree_sitter_python as tspython
import tree_sitter 

def tree_extract_imports(
    node: any, 
    code_text: str
) -> any:
    imports = []
    if node.type == 'import_statement' or node.type == 'import_from_statement':
        start_byte = node.start_byte
        end_byte = node.end_byte
        imports.append(code_text[start_byte:end_byte].decode('utf8'))
    for child in node.children:
        imports.extend(tree_extract_imports(child, code_text))
    return imports

def tree_extract_dependencies(
    node: any, 
    code_text: str
) -> any:
    dependencies = []
    for child in node.children:
        if child.type == 'call':
            dependency_name = child.child_by_field_name('function').text.decode('utf8')
            dependencies.append(dependency_name)
        dependencies.extend(tree_extract_dependencies(child, code_text))
    return dependencies

def tree_extract_code_and_dependencies(
    node: any,
    code_text: str
) -> any:
    codes = []
    if not node.type == 'function_definition':
        start_byte = node.start_byte
        end_byte = node.end_byte
        name = node.child_by_field_name('name')
        if name is None:
            code = code_text[start_byte:end_byte].decode('utf8')
            if not 'def' in code:
                dependencies = tree_extract_dependencies(node, code_text)
                codes.append({
                    'name': 'global',
                    'code': code,
                    'dependencies': dependencies
                })
    return codes

def tree_extract_functions_and_dependencies(
    node: any, 
    code_text: str
) -> any:
    functions = []
    if node.type == 'function_definition':
        start_byte = node.start_byte
        end_byte = node.end_byte
        name = node.child_by_field_name('name').text.decode('utf8')
        code = code_text[start_byte:end_byte].decode('utf8')
        dependencies = tree_extract_dependencies(node, code_text)
        functions.append({
            'name': name,
            'code': code,
            'dependencies': dependencies
        })
    for child in node.children:
        functions.extend(tree_extract_functions_and_dependencies(child, code_text))
    return functions

def tree_get_used_imports(
    general_imports: any,
    function_dependencies: any
) -> any:
    parsed_imports = {}
    for code_import in general_imports:
        import_factors = code_import.split('import')[-1].replace(' ', '')
        import_factors = import_factors.split(',')
    
        for factor in import_factors:
            if not factor in parsed_imports:
                parsed_imports[factor] = code_import.split('import')[0] + 'import ' + factor
            
    relevant_imports = {}
    for dependency in function_dependencies:
        initial_term = dependency.split('.')[0]
    
        if not initial_term in relevant_imports:
            if initial_term in parsed_imports:
                relevant_imports[initial_term] = parsed_imports[initial_term]
    
    used_imports = []
    for name, code in relevant_imports.items():
        used_imports.append(code)

    return used_imports

def tree_get_used_functions(
    general_functions: any,
    function_dependencies: any
): 
    used_functions = []
    for related_function_name in function_dependencies:
        for function in general_functions:
            if function['name'] == related_function_name:
                used_functions.append('from ice import ' + function['name'])
    return used_functions

def tree_create_code_document(
    code_imports: any,
    code_functions: any,
    function_item: any
) -> any:
    used_imports = tree_get_used_imports(
        general_imports = code_imports,
        function_dependencies = function_item['dependencies']
    )

    used_functions = tree_get_used_functions(
        general_functions = code_functions,
        function_dependencies = function_item['dependencies']
    )
    
    document = {
        'imports': used_imports,
        'functions': used_functions,
        'name': function_item['name'],
        'dependencies': function_item['dependencies'],
        'code': function_item['code']
    }
    
    return document
     
def tree_format_code_document(
    code_document: any
) -> any:
    formatted_document = ''
    for doc_import in code_document['imports']:
        formatted_document += doc_import + '\n'

    for doc_functions in code_document['functions']:
        formatted_document += doc_functions + '\n'

    if 0 < len(code_document['dependencies']):
        formatted_document += 'code dependencies\n'

        for doc_dependency in code_document['dependencies']:
            formatted_document += doc_dependency + '\n'

    if code_document['name'] == 'global':
        formatted_document += code_document['name'] + ' code\n'
    else:
        formatted_document += 'function ' + code_document['name'] + ' code\n'
    
    for line in code_document['code'].splitlines():
        if not bool(line.strip()):
            continue
        doc_code = re.sub(r'#.*','', line)
        if not bool(doc_code.strip()):
            continue
        formatted_document += doc_code + '\n'    
    return formatted_document

def tree_create_python_code_and_function_documents(
    code_document: any
):
    PY_LANGUAGE = tree_sitter.Language(tspython.language())
    parser = tree_sitter.Parser(PY_LANGUAGE)

    tree = parser.parse(
        bytes(
            code_document,
            "utf8"
        )
    )

    root_node = tree.root_node
    code_imports = tree_extract_imports(
        root_node, 
        bytes(
            code_document, 
            'utf8'
        )
    )

    code_global = tree_extract_code_and_dependencies(
        root_node, 
        bytes(
            code_document, 
            'utf8'
        )
    )

    code_functions = tree_extract_functions_and_dependencies(
        root_node, 
        bytes(
            code_document, 
            'utf8'
        )
    )

    initial_documents = []
    for item in code_global:
        document = tree_create_code_document(
            code_imports = code_imports,
            code_functions = code_functions,
            function_item = item
        )  
        initial_documents.append(document)

    for item in code_functions:
        document = tree_create_code_document(
            code_imports = code_imports,
            code_functions = code_functions,
            function_item = item
        )  
        initial_documents.append(document)

    formatted_documents = []
    seen_functions = []
    for document in initial_documents:
        if not document['name'] == 'global':
            if document['name'] in seen_functions:
                continue
        
        formatted_document = tree_format_code_document(
            code_document = document
        )

        formatted_documents.append(formatted_document)
        seen_functions.append(document['name'])

    return formatted_documents
