import re
import os
import numpy as np
from helper_functions import *
import copy
from special_characters import get_special_characters
from path_searching import *
from remove_markdown_comment import *

allowed_chars = get_special_characters()

def parse_dataview_query_0(query: str, vault_folder: str):
    result = {}
    
    # Step 1: Check if it's a Dataview table query
    if not query.strip().lower().startswith("table") and not not query.strip().startswith("Table"):
        raise Exception('Could not identify a dataview table!')
        return {"error": "Not a Dataview table query"}
        
    result["query_type"] = "table"
    
    # Step 2: Extract fields (handling 'replace' and 'as' aliases)
    field_pattern = re.compile(r'([^,]+?)(?:\s+as\s+([^,]+))?(?=,|$)')
    fields_line = query.split("\n")[0]  # Get the first line (table ...)
    fields_raw = fields_line.split("table", 1)[1].strip()
    fields = []
    
    for match in field_pattern.finditer(fields_raw):
        expression, alias = match.groups()
        expression = expression.strip()
        alias = alias.strip() if alias else expression  # If no alias, use original
        fields.append({"expression": expression, "alias": alias})
    
    result["fields"] = fields
    
    # Step 3: Extract folder name (after 'from')
    from_match = re.search(r'from\s+"([^"]+)"', query)
    if from_match:
        result["folder"] = from_match.group(1)
    
    # Step 4: Extract sorting (sort + field + order)
    sort_match = re.search(r'sort\s+([^\s]+)\s+(asc|desc)', query)# re.search(r'sort\s+(\w+)\s+(asc|desc)', query)
    if sort_match:
        result["sort"] = {"field": sort_match.group(1), "order": sort_match.group(2)}
    
    # Step 5: Extract 'contains' filters (after 'where')
    where_match = re.search(r'where\s+(.+)', query, re.DOTALL)
    if where_match:
        where_clause = where_match.group(1)
        contains_matches = re.findall(r'contains\(([^,]+),\s*"([^"]+)"\)', where_clause)
        result["filters"] = [{"field": field.strip(), "value": value} for field, value in contains_matches]
    
    return result

def extract_fields_from_query_0(query: str):
    # Remove lines starting with 'from "'
    query = re.sub(r'\n\s*from\s+".*"', '', query)
    
    # Remove words enclosed in double quotes
    query = re.sub(r'"[^"]*"', '', query)
    
    # Extract words that start with a letter and do not contain math symbols, whitespace, parentheses, brackets, '/', '\', or emojis
    word_pattern = re.compile(r'\b[a-zA-Z][^\s\W\[\]\(\)\/\\\U0001F300-\U0001FAD6]*\d*')
    words = word_pattern.findall(query)
    
    # Define reserved words (commands in the query language)
    reserved_words = {"table", "from", "sort", "where", "contains", "replace", "AND", "OR", "desc", "asc", "as"}
    
    # Filter out reserved words
    filtered_words = [word for word in words if word not in reserved_words]
    
    # Extract the line starting with 'table'
    table_line_match = re.search(r'\btable\b(.*)', query)
    if table_line_match:
        table_line = table_line_match.group(1)
        
        # Find words that appear after 'as ' and any whitespace
        alias_pattern = re.compile(r'\bas\s+([a-zA-Z][^\s\d\W\[\]\(\)\/\\\U0001F300-\U0001FAD6]*)')
        aliases = {match.group(1) for match in alias_pattern.finditer(table_line)}
        
        # Remove alias words from filtered_words, unless they also appear as original words
        filtered_words = [word for word in filtered_words if word not in aliases or word in words]
    
    return list(np.unique(filtered_words))


def get_expressions_and_aliases(input_str):
    expressions = []
    aliases = []
    for part in input_str:
        parts = part.split(' as ')
        expressions.append(parts[0].strip())
        aliases.append((parts[1].strip() if len(parts) > 1 else parts[0].strip()).replace('"', ''))
    return expressions, aliases

def extract_fields_from_query(query: str):
    # Remove lines starting with 'from "'
    # query = re.sub(r'\n\s*from\s+".*"', '', query)
    query = re.sub(r'\n\s*from\s+("[^"]*"|\[\[[^\]]+\]\]|\S+)(\s+(AND|OR)\s+("[^"]*"|\[\[[^\]]+\]\]|\S+))*', '', query, flags=re.IGNORECASE)
    
    # (no need) Remove words enclosed in double quotes
    # query = re.sub(r'"[^"]*"', '', query)
    
    # Extract the line starting with 'table' and trim leading whitespaces
    table_line_match = re.search(r'\btable\b(.*)', query, re.IGNORECASE)
    table_line = table_line_match.group(1).strip() if table_line_match else ""
    
    # Split by commas outside parentheses (only on the table line)
    query_parts = split_outside_parentheses(table_line)
    
    # Get expressions and aliases
    expressions, aliases = get_expressions_and_aliases(query_parts)
    
    # Define reserved words (commands in the query language)
    reserved_words = {"table", "from", "sort", "where", "contains", "replace", "AND", "OR", "desc", "asc", "startswith", "as"}
    
    # Filter out reserved words
    filtered_words = [word for word in expressions if word not in reserved_words]
    
    fields = []
    
    for expression, alias in zip(expressions, aliases):
        # If the expression is not a reserved word, add it to the fields list
        if expression not in reserved_words and len(expression) > 0:
            fields.append({"expression": expression, "alias": alias})
    
    return fields

def parse_dataview_query(query: str, PATHS: dict, this_note_path: str):
    result = {}
    vault_folder = PATHS['vault']
    # Step 1: Check if it's a Dataview table query
    if not query.strip().lower().startswith("table"):
        return {"error": "Not a Dataview table query"}
    result["query_type"] = "table"
    
    # Step 2: Extract fields using the helper function
    result["fields"] = extract_fields_from_query(query)
    
    # Step 3: Extract folder name or tag (after 'from')
    code_version = 1
    if code_version == 0:
        from_match = re.search(r'(?i)from\s+"([^"]+)"', query)
        if from_match:
            result["folder"] = from_match.group(1)
    elif code_version == 1:        
        match = re.search(r'from\s+(.+?)(\s+sort|\s+where|\s*$)', query, re.IGNORECASE)
        if match:
            content = match.group(1).strip()  # Extract FROM clause content

            # Split while keeping AND/OR and preserving quotes & [[brackets]]
            parts = re.split(r'\s+(AND|OR)\s+', content, flags=re.IGNORECASE)
            
            # if is_path(parts[0]): result["folder"] = parts[0].replace('"', '')  # Extract the folder name
            rel_path = parts[0].replace('"', '').replace("'", "").replace("/", "\\")
            
            m = re.match(r'^#\S', rel_path)
            result["tag"] = None
            if m is not None:
                if m[0]:
                    result["tag"] = rel_path
                else:
                    if os.path.exists(vault_folder+rel_path): 
                        result["folder"] = parts[0].replace('"', '')  # Extract the folder name
            else:
                if os.path.exists(vault_folder+rel_path): 
                    result["folder"] = parts[0].replace('"', '')  # Extract the folder name

            if result["tag"] is None:
                if len([p for p in parts[0::2] if is_path(p)]) > 1:
                    raise ValueError("Multiple paths detected in FROM clause. Haven't included this case yet.")
            
                if len(parts)>0:
                    result["folder"] = [part for part in parts[0::2] if is_path(part)][0]
                    # for part in parts[0::2]:
                    
            else:
                # get the list of notes that contain the tag
                tagged_notes_file = get_fields_from_Obsidian_note(this_note_path, ["search_results_if_necessary:: "])[0][0]
                tagged_notes_file = get_embedded_reference_path(tagged_notes_file, PATHS)
                with open(tagged_notes_file, encoding='utf8') as f:
                    result['files_with_the_tag'] = f.readlines()

            other_from_filters = parts[2::2]
            result["other__from__filters"] = other_from_filters
    else:
        raise notImplementedError("Code version not implemented")
        
    # Step 4: Extract sorting (sort + field + order)
    sort_match = re.search(r'sort\s+([^\s]+)\s+(asc|desc)', query)#re.search(r'sort\s+(\w+)\s+(asc|desc)', query)
    if sort_match:
        result["sort"] = {"field": sort_match.group(1), "order": sort_match.group(2)}
    
    # Step 5: Extract 'contains' filters (after 'where')
    where_match = re.search(r'(?mi)^\s*where\s+([^\n\r]+)', query)
    if where_match:
        where_clause = where_match.group(1)
        
        # We now want to handle both "AND" and "OR" within the where clause
        # Split by "AND" and "OR", and also capture the operator
        filter_pattern = r'(\w+\([^\)]+\s*,\s*"[^"]*"\)|\w+)|\s+(AND|OR)'

        matches = list(re.finditer(filter_pattern, where_clause))
        filters = []

        prev_filter = None  # To track previous expression

        for match in matches:
            filter_expr = match.group(1)  # Condition (function or standalone word)
            logic = match.group(2)  # Logical operator (AND/OR)

            if filter_expr:
                # This is a condition (function or standalone field)
                if prev_filter:
                    filters.append(prev_filter)  # Save the previous filter before moving on
                prev_filter = {
                    "type": "function" if "(" in filter_expr else "standalone",
                    "field": filter_expr,
                    "logic": "AND"  # Default logic, will be updated if followed by AND/OR
                }
            elif logic and prev_filter:
                # This is an AND/OR operator, update the last saved filter
                prev_filter["logic"] = logic

        # Add the last saved filter
        if prev_filter:
            filters.append(prev_filter)

        # Post-process to extract function details
        filters_1 = []
        for filter_entry in filters:
            if filter_entry["type"] == "function":
                contains_pattern = r'(\w+)\(([^,]+),\s*"([^"]+)"\)'
                contains_match = re.match(contains_pattern, filter_entry["field"])
                if contains_match:
                    filter_entry.update({
                        "function": contains_match.group(1),
                        "field": contains_match.group(2).strip(),
                        "value": contains_match.group(3).strip()
                    })
                    
            filters_1.append(filter_entry)
                
        result["filters"] = filters_1
    
    return result


def apply_filter_logic(filters, fields, file_content, other_from_filters):
    # We will evaluate the filter logic in sequence, respecting the logic operators (AND, OR)
    result = True  # Default result for AND logic
    for i, filter in enumerate(filters):
        field_value = fields[i]
        filter_pass = False

        # Check if the filter function is contains (as an example)
        if filter['type'] == 'function':
            if filter['function'] == 'contains':
                filter_pass = any(filter['value'] in value for value in field_value)
            else:
                raise NotImplementedError(f"Filter function '{filter['function']}' not implemented")
        elif filter['type'] == 'standalone':
            # raise NotImplementedError(f"Filter type 'standalone' not implemented")
            if field_value:
                if field_value[0].strip().replace(":: ", "")=='true':
                    filter_pass = True
            

        # Add more conditional functions here as needed, like startswith, etc.

        # Handle logic for the current filter (AND, OR)
        if filter['logic'] == 'OR':
            result = result or filter_pass
        else:  # Default is 'AND'
            result = result and filter_pass

        # If at any point we know the result is False and it's an AND operation, we can short-circuit
        if not result and filter['logic'] == 'AND':
            break

    # # New: Check "other_from_filters" in file_content (All must be present)
    # for filter_value in other_from_filters:
    #     if filter_value not in file_content:
    #         return False  # If any filter is missing, return False


    return result

def filter_files_with_logic(parsed_query, files):
    filtered_files = []

    # Loop through each file
    for file in files:
        # Extract the fields from the file
        fields = get_fields_from_Obsidian_note(file, [filter['field'] for filter in parsed_query['filters']])
        # fields_1 = []

        
        # for f in fields:
        #     for f_i  in f:
        #         fields_1.append(f_i.replace(":: ", ""))
        # fields = fields_1
        
        # if file.split('\\')[-1].startswith('p112'):
        #     print('debug')
        
        try:
            with open(file, 'r', encoding='utf-8') as f:
                file_content = f.read()  # Read the entire file content as a string
        except Exception as e:
            print(f"Error reading file {file}: {e}")
            continue  # Skip this file if there's an error
        # Check if the file matches all the filters based on their logic
        if apply_filter_logic(parsed_query['filters'], fields, file_content, parsed_query['other__from__filters']):
            filtered_files.append(file)

    return filtered_files

def apply_replace(expression):
    """
    Correctly handles nested `replace()` calls by processing them from inside out.
    
    Example:
    replace(replace(topic, "#Topic/ML", "ML"), "#Topic/", "")  
    → (topic).replace("#Topic/ML", "ML").replace("#Topic/", "")
    """
    expressions_to_carry = []
    z=0
    while "replace(" in expression:
        start_idx = expression.rfind("replace(")  # Find the innermost replace
        end_idx = start_idx + expression[start_idx:].find(")")  # Match closing bracket
        
        # Extract the replace function
        replace_call = expression[start_idx:end_idx + 1]
        
        # Match "replace(field, old, new)" within the extracted call
        match = re.fullmatch(r'replace\(\s*([\w\.\+\-*/()]+)\s*,\s*"([^"]*)"\s*,\s*"([^"]*)"\s*\)', replace_call)
        if not match:
            break  # No valid replace pattern found
        
        field, old, new = match.groups()
        
        # Construct Python-compatible replace expression
        replacement = f"({field}).replace(\"{old}\", \"{new}\")"
        mask_expr = f'expr{z}'
        expressions_to_carry.append([mask_expr, replacement])
        # Replace the innermost `replace(...)` with its equivalent Python expression
        expression = expression[:start_idx] + mask_expr + expression[end_idx + 1:]
        z+=1
    
    return expression, expressions_to_carry


def evaluate_expression(expression, fields, file_path):
    """
    Evaluates an expression by replacing field names with their values and processing nested replace functions.
    
    Args:
    - expression (str): The expression to evaluate.
    - fields (dict): A dictionary of field values (field_name -> value).
    - file_path (str): Path to the file to extract values for fields.
    
    Returns:
    - The result of the evaluated expression.
    """
    expression_0 = copy.copy(expression)
    
    # Extract the field names used in the expression
    field_names = extract_fields_from_query_0(expression)
    
    # Create the list of fields to be extracted
    look_for_fields = [field + ":: " for field in field_names]
    
    # Get field values from the Obsidian note
    field_values = get_fields_from_Obsidian_note(file_path, look_for_fields)
    
    # Create a dictionary of field names and their corresponding values
    # fields_dict = {field_name: '- '*(len(value)>0) + '<br>- '.join(value) if value else '' for field_name, value in zip(field_names, field_values)}
    fields_dict = dict()
    for field_name, value in zip(field_names, field_values):
        if value:
            if len(value) > 1:
                fields_dict[field_name] = '- ' + '<br>- '.join(value)
            else:
                fields_dict[field_name] = value[0]
        else:
            fields_dict[field_name] = ''
        
    
    
    
    # Apply `replace` transformations first
    expression, expressions_to_carry = apply_replace(expression)
    
    # Store replacement expressions in `fields_dict`
    for expr_c in expressions_to_carry:
        fields_dict[expr_c[0]] = expr_c[1]

    # Replace field names with actual values
    for field_name, field_value in reversed(fields_dict.items()):
        if field_value.startswith("(") and field_value.endswith(")"):
            # If the value is already a valid Python expression, insert it as-is
            expression = expression.replace(field_name, field_value)
        else:
            # Otherwise, treat it as a string
            expression = expression.replace(field_name, repr(field_value))  

    # Now we need to evaluate the final expression
    try:
        result = eval(expression)
    except Exception as e:
        # result = f"Error evaluating expression: {e}"
        result = '-'

    return result


def evaluate_expression_0(expression, fields, file_path):
    """
    Evaluates an expression by replacing field names with their values 
    and supporting `contains` and `replace` functions.
    
    Args:
    - expression (str): The expression to evaluate.
    - fields (dict): A dictionary of field values (field_name -> value).
    - file_path (str): Path to the file to extract values for fields.
    
    Returns:
    - The result of the evaluated expression.
    """
    # Extract the field names used in the expression
    field_names = extract_fields_from_query_0(expression)
    
    # Create the list of fields to be extracted
    look_for_fields = [field + ":: " for field in field_names]
    
    # Get field values from the Obsidian note
    field_values = get_fields_from_Obsidian_note(file_path, look_for_fields)
    
    # Create a dictionary of field names and their corresponding values
    fields_dict = {field_name: value[0] if value else '' for field_name, value in zip(field_names, field_values)}
    
    # Replace field names with values in the expression
    for field_name, field_value in fields_dict.items():
        expression = expression.replace(field_name, repr(field_value))  # Ensure proper string handling

    # Replace contains(field, value) with Python `"value" in field` logic
    expression = re.sub(r'contains\(([^,]+),\s*([^)]+)\)', r'\2 in \1', expression)
    
    # Replace replace(field, old, new) with Python `.replace(old, new)`
    def replace_match(match):
        field, old, new = match.groups()
        return f"{field}.replace({old}, {new})"
    
    expression = re.sub(r'replace\(([^,]+),\s*([^,]+),\s*([^)]+)\)', replace_match, expression)

    # Now we need to evaluate the expression
    try:
        # Evaluate the expression using eval, assuming it's a safe expression
        result = eval(expression)
    except Exception as e:
        result = f"Error evaluating expression: {e}"

    return result

def evaluate_fields(parsed_query, file_path):
    """
    Evaluates all fields in parsed_query['fields'] using the file data for field values.
    
    Args:
    - parsed_query (dict): The parsed query, which contains field expressions.
    - file_path (str): The file path for the note to extract fields from.
    
    Returns:
    - A list of evaluated fields (with expression and alias).
    """
    evaluated_fields = []
    
    for field in parsed_query['fields']:
        expression = field['expression']
        alias = field['alias']
        
        # Evaluate the expression
        evaluated_value = evaluate_expression(expression, {}, file_path)
        evaluated_value = remove_markdown_comments(evaluated_value)
        evaluated_fields.append({
            'expression': evaluated_value,
            'alias': alias
        })
    
    return evaluated_fields


def sort_evaluated_fields(all_evaluated_fields, files, parsed_query):
    """
    Sorts the evaluated fields based on parsed_query['sort'].

    Args:
        all_evaluated_fields (list of dict): List of dictionaries containing evaluated field values.
        parsed_query (dict): Parsed query containing sorting instructions.

    Returns:
        list: Sorted list of evaluated fields.
    """
    sort_instructions = parsed_query.get('sort', [])  # List of sorting conditions
    if not sort_instructions:
        return all_evaluated_fields, files  # No sorting needed

    # Apply sorting with ascending/descending order
    reverse_order = sort_instructions['order']=='desc'
    # sorted_fields = sorted(all_evaluated_fields, key=sort_key, reverse=any(reverse_order))

    if not sort_instructions['field']=='file.name':
        fields = []
        for file in files:
            extracted_field = get_fields_from_Obsidian_note(file, [s + ":: " for s in [sort_instructions['field']]])
            if extracted_field[0]:
                fields.append(extracted_field[0][0])
            else:
                fields.append('')
    else:
        fields = [files.split('\\')[-1].replace('.md', '') for files in files]

    try:
        # Convert to numeric if possible
        numeric_fields = np.array([float(x) if x else float('-inf') for x in fields])
        # Sort numerically using np.argsort() and return the sorted list
        indices = np.argsort(numeric_fields)
    except ValueError:
        # If there's a ValueError, it means not all elements are numeric, so sort alphabetically
        indices = np.argsort(fields)
    
    if reverse_order: indices = indices[::-1]
    
    sorted_fields = [all_evaluated_fields[i] for i in indices]
    files = [files[i] for i in indices]
        
    return sorted_fields, files


def write_Obsidian_table_from_dataview_query(query_text, PATHS, this_file_path, datav__file_column_name='File Name', exclude_columns=[]):
    
    query = query_text
    vault_folder = PATHS['vault']
    parsed_query = parse_dataview_query(query, PATHS, this_file_path)
    
    if parsed_query['tag'] is None:
        parsed_query['folder'] = parsed_query['folder'].replace('/', '\\').strip('"')
        
        files = get_all_files_in_folder(vault_folder, parsed_query['folder'])
        files = [f for f in files if f.endswith('.md')]
    else:
        files = [PATHS['vault']+x.strip().replace('/','\\') for x in parsed_query['files_with_the_tag']]

    for filter in parsed_query.get('other__from__filters', []):
        print("⚠️WARNING: ASSUMING THAT THE 'AND' OPERATOR IS USED IN THE 'FROM' CLAUSE FILTERS. PLEASE CHECK IF THIS IS CORRECT.")
        if is_note(filter):
            try:
                filter_path = get_embedded_reference_path(filter, PATHS)
                res=get_fields_from_Obsidian_note(filter_path, ["links_for_latex_conversion:: "])[0][0].split(',')
                pattern = re.compile(r'\[(.*?)\]')
                linked_notes = [f'{pattern.search(t).group(1)}.md' for t in res]
                tmp1 = [f.split('\\')[-1] for f in files]
                indices = [i for i, x in enumerate(tmp1) if x in linked_notes]
                files = [files[i] for i in indices]
            except:
                None
            
    if 'filters' in parsed_query.keys():
        # Filter the files based on the 'contains' filters
        filtered_files = filter_files_with_logic(parsed_query, files)
    else:
        filtered_files = files

    # Evaluate the fields
    all_evaluated_fields = []
    for file_path in filtered_files:
        evaluated_fields = evaluate_fields(parsed_query, file_path)
        all_evaluated_fields.append(evaluated_fields)

    # Sort the evaluated fields based on parsed_query['sort']
    all_evaluated_fields, filtered_files = sort_evaluated_fields(all_evaluated_fields, filtered_files, parsed_query)

    # Prepare table data
    table_data = {}

    # Create the first row (column names) based on the aliases of the fields
    table_data[0] = {}
    table_data[0][1] = datav__file_column_name  # Add the "File Path" column
    for i, field in enumerate(parsed_query['fields']):
        table_data[0][i + 2] = field['alias']  # Start from column 2 for the fields

    col_idx_excl = []
    if exclude_columns:
        for col in exclude_columns:
            if col:
                # TODO: that "col in item[1]" might create issues if two columns have similar names. Make sure that the trailing "'" are removed from col and item[1]
                col_idx_excl.append([item for item in table_data[0].items() if col in item[1]][0][0])

    # remove columns that the user wishes to hide
    for idx in col_idx_excl:
        table_data[0].pop(idx)


    # Populate the table rows with evaluated field values for each file
    for row_index, (file_path, file_fields) in enumerate(zip(filtered_files, all_evaluated_fields), start=1):
        table_data[row_index] = {}
        
        # patch, quick fix
        try:
            dum1 = file_path.replace(vault_folder + parsed_query['folder'] + "\\", "").split('\\')[-1]
        except:
            dum1 = file_path.split('\\')[-1]
            
        dum1 = f'[[{dum1.replace(".md", "")}]]'
        table_data[row_index][1] = dum1
        
        for col_index, field in enumerate(file_fields):
            if not col_index + 2 in col_idx_excl:
                table_data[row_index][col_index + 2] = field['expression'].replace('|', '\|')  # Start from column 2 for the fields

    # Generate the markdown table
    table_data_1 = {}
    
    for row_idx, row_data in table_data.items():
        table_data_1[row_idx] = {}
        z = 0
        for col_idx, col_data in row_data.items():
            z += 1
            table_data_1[row_idx][z] = col_data
            
    markdown_table = write_Obsidian_table(table_data_1)

    obsidian_notes = [t[1] for (_,t) in table_data.items() if is_note(t[1])]
    return markdown_table, obsidian_notes

# print(filtered_files)


# print(files)


# print(parsed_query)

# Example usage

# query_1 = '''table year+"-" + title as title, number_references as n_cit, replace(replace(topic, "#Topic/Machine-Learning/Multitask-Learning", "MTL"), "#Topic/", "") as topic, comm as 💭
# from "Literature/publication_note_objects"
# sort file.name desc
# where contains(topic, "RL") AND contains(topic, "Multit")'''

# query_2 = '''table number_references as n_cit, year+"-" + title as title, replace(topic, "#Topic/", "") as topic, comm as 💭
# from "Literature/publication_note_objects"
# sort comm desc
# where contains(type, "📜/Survey")'''

# query_3 = '''table number_references as n_cit, year+"-" + title as title, replace(topic, "#Topic/", "") as topic, comm as 💭
# from "Literature/publication_note_objects"
# where contains(type, "📜/Survey")'''

# query_4 = '''table year+"-" + title as title, number_references as n_cit, replace(topic, "#Topic/", "") as topic, has_external_note as ext_note, comm as 💭
# from "Literature/publication_note_objects"
# sort number_references desc
# where contains(topic, "Physics")'''

# query = query_2

# PATHS = {'vault': 'C:\\Users\\mariosg\\OneDrive - NTNU\\FILES\\workTips\\'}

# markdown_table = write_Obsidian_table_from_dataview_query(query, PATHS)

# with open(PATHS['vault'] + "dummy_1.md", 'w', encoding='utf-8') as file:
#     file.writelines(markdown_table)



