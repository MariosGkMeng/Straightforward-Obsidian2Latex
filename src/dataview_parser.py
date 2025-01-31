import re
import os
import numpy as np
from get_fields_from_Obsidian_note import get_fields_from_Obsidian_note
import copy

def get_all_files_in_folder(vault_folder, target_folder):
    # Combine the base folder and target folder
    full_path = os.path.join(vault_folder, target_folder)
    
    # List to hold all files
    all_files = []
    
    # Walk through the directory and its subdirectories
    for root, dirs, files in os.walk(full_path):
        for file in files:
            # Add the full path of each file
            all_files.append(os.path.join(root, file))
    
    return all_files

def parse_dataview_query_0(query: str):
    result = {}
    
    # Step 1: Check if it's a Dataview table query
    if not query.strip().startswith("table"):
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
    word_pattern = re.compile(r'\b[a-zA-Z][^\s\d\W\[\]\(\)\/\\\U0001F300-\U0001FAD6]*')
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



def split_outside_parentheses(input_str):
    result = []
    start = 0
    paren_level = 0
    for i, char in enumerate(input_str):
        # Track parentheses
        if char == '(':
            paren_level += 1
        elif char == ')':
            paren_level -= 1
        
        # If we're not inside parentheses and find a comma, split
        if paren_level == 0 and char == ',':
            result.append(input_str[start:i].strip())
            start = i + 1
    
    # Append the last segment
    result.append(input_str[start:].strip())
    
    return result

def get_expressions_and_aliases(input_str):
    expressions = []
    aliases = []
    for part in input_str:
        parts = part.split(' as ')
        expressions.append(parts[0].strip())
        aliases.append(parts[1].strip() if len(parts) > 1 else parts[0].strip())
    return expressions, aliases



def extract_fields_from_query(query: str):
    # Remove lines starting with 'from "'
    query = re.sub(r'\n\s*from\s+".*"', '', query)
    
    # (no need) Remove words enclosed in double quotes
    # query = re.sub(r'"[^"]*"', '', query)
    
    # Extract the line starting with 'table' and trim leading whitespaces
    table_line_match = re.search(r'\btable\b(.*)', query)
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
        if expression not in reserved_words:
            fields.append({"expression": expression, "alias": alias})
    
    return fields

def parse_dataview_query(query: str):
    result = {}
    
    # Step 1: Check if it's a Dataview table query
    if not query.strip().startswith("table"):
        return {"error": "Not a Dataview table query"}
    result["query_type"] = "table"
    
    # Step 2: Extract fields using the helper function
    result["fields"] = extract_fields_from_query(query)
    
    # Step 3: Extract folder name (after 'from')
    from_match = re.search(r'from\s+"([^"]+)"', query)
    if from_match:
        result["folder"] = from_match.group(1)
    
    # Step 4: Extract sorting (sort + field + order)
    sort_match = re.search(r'sort\s+([^\s]+)\s+(asc|desc)', query)#re.search(r'sort\s+(\w+)\s+(asc|desc)', query)
    if sort_match:
        result["sort"] = {"field": sort_match.group(1), "order": sort_match.group(2)}
    
    # Step 5: Extract 'contains' filters (after 'where')
    where_match = re.search(r'where\s+(.+)', query, re.DOTALL)
    if where_match:
        where_clause = where_match.group(1)
        
        # We now want to handle both "AND" and "OR" within the where clause
        # Split by "AND" and "OR", and also capture the operator
        filter_pattern = r'(\w+\([^\)]+\s*,\s*"[^"]*"\))\s*(AND|OR)?'
        filters = []
        
        for match in re.finditer(filter_pattern, where_clause):
            filter_expr = match.group(1)
            logic = match.group(2) if match.group(2) else 'AND'  # Default logic is 'AND'
            
            # Extract field and value from the contains function
            contains_pattern = r'(\w+)\(([^,]+),\s*"([^"]+)"\)'
            contains_match = re.match(contains_pattern, filter_expr)
            
            if contains_match:
                field = contains_match.group(2).strip()
                value = contains_match.group(3).strip()
                
                filters.append({
                    "function": "contains",
                    "field": field,
                    "value": value,
                    "logic": logic
                })
        
        result["filters"] = filters
    
    return result


def apply_filter_logic(filters, fields):
    # We will evaluate the filter logic in sequence, respecting the logic operators (AND, OR)
    result = True  # Default result for AND logic
    for i, filter in enumerate(filters):
        field_value = fields[i]
        filter_pass = False

        # Check if the filter function is contains (as an example)
        if filter['function'] == 'contains':
            filter_pass = any(filter['value'] in value for value in field_value)

        # Add more conditional functions here as needed, like startswith, etc.

        # Handle logic for the current filter (AND, OR)
        if filter['logic'] == 'OR':
            result = result or filter_pass
        else:  # Default is 'AND'
            result = result and filter_pass

        # If at any point we know the result is False and it's an AND operation, we can short-circuit
        if not result and filter['logic'] == 'AND':
            break

    return result

def filter_files_with_logic(parsed_query, files):
    filtered_files = []

    # Loop through each file
    for file in files:
        # Extract the fields from the file
        fields = get_fields_from_Obsidian_note(file, [filter['field'] for filter in parsed_query['filters']])

        # Check if the file matches all the filters based on their logic
        if apply_filter_logic(parsed_query['filters'], fields):
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
    fields_dict = {field_name: value[0] if value else '' for field_name, value in zip(field_names, field_values)}
    
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
        result = f"Error evaluating expression: {e}"

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
        
        evaluated_fields.append({
            'expression': evaluated_value,
            'alias': alias
        })
    
    return evaluated_fields


def write_Obsidian_table(table, return_lines = True):
	'''
	# Example
	table = {
		0: {1: 'col_1_title',
			2: 'col_2_title',
			3: 'col_3_title',
			4: 'col_4_title'
		},
		1: {1: 'r1c1',
			2: 'r1c2',
			3: 'r1c3'
		},
		2: {1: 'r2c1',
			2: 'r2c2',
			3: 'r3c2',
			4: 'r4c2'}
	}
	write_Obsidian_table(table)
	'''
	
	if not isinstance(table, dict):
		raise Exception('`table` input must be a dict!')
	
	cols = np.max([len(list(table[i].keys())) for i in list(table.keys())])
	rows = len(table.keys())
	lines = []
	keys = list(table.keys())
	if 0 in keys:
		# has column titles
		lines.append('| '+' | '.join([f'**{table[0][key]}**' for key in table[0].keys()]) + ' |')
	else:
		lines.append(''.join('| '*cols) + '|')

	lines.append(''.join('| --- '*cols) + '|')
	
	for i in keys:
		if i!=0:
			lines.append('| '+' | '.join([table[i][key] for key in table[i].keys()]) + ' |')
			lines[-1] += ' |'*(cols-len(table[i].keys()))
	
	if return_lines: 
		return [l + '\n' for l in lines]
	return '\n'.join(lines)


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
        return all_evaluated_fields  # No sorting needed

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


def write_Obsidian_table_from_dataview_query(query_text, PATHS):
    
    query = query_text
    parsed_query = parse_dataview_query(query)

    vault_folder = PATHS['vault']
    parsed_query['folder'] = parsed_query['folder'].replace('/', '\\')
    files = get_all_files_in_folder(vault_folder, parsed_query['folder'])


    filtered_files = filter_files_with_logic(parsed_query, files)

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
    table_data[0][1] = "File Path"  # Add the "File Path" column
    for i, field in enumerate(parsed_query['fields']):
        table_data[0][i + 2] = field['alias']  # Start from column 2 for the fields

    # Populate the table rows with evaluated field values for each file
    for row_index, (file_path, file_fields) in enumerate(zip(filtered_files, all_evaluated_fields), start=1):
        table_data[row_index] = {}
        dum1 = file_path.replace(vault_folder + parsed_query['folder'] + "\\", "")
        dum1 = f'[[{dum1.replace(".md", "")}]]'
        table_data[row_index][1] = dum1
        
        for col_index, field in enumerate(file_fields):
            table_data[row_index][col_index + 2] = field['expression'].replace('|', '\|')  # Start from column 2 for the fields

    # Generate the markdown table
    markdown_table = write_Obsidian_table(table_data)

    return markdown_table

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

# markdown_table = write_Obsidian_table_from_dataview(query, PATHS)


# query_fields = extract_fields_from_query(query)
# print(query_fields)

# # Print or return the result
# # print(''.join(markdown_table))
# with open(vault_folder + "dummy_1.md", 'w', encoding='utf-8') as file:
#     file.writelines(markdown_table)


# Unit testing tasks
# - Check whether the filtered files are correct based on the query


# # Split the input string using commas outside parentheses
# input_string = 'table year+"-" + title as title, number_references as n_cit, replace(replace(topic, "#Topic/Machine-Learning/Multitask-Learning", "MTL"), "#Topic/", "") as topic, comm as 💭'
# expressions_and_aliases = get_expressions_and_aliases(split_outside_parentheses(input_string))


# print(split_result)

