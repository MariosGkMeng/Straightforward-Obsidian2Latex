import os

def escape_underscore(text):
    escaped = []
    inside_special = False  # Track whether we're inside a special segment
    delimiter = None  # Store the current active delimiter
    
    i = 0
    while i < len(text):
        char = text[i]
        
        # Toggle inside_special state when encountering special characters
        if char in {"$", "`"}:
            if inside_special and char == delimiter:
                inside_special = False  # Closing the special segment
                delimiter = None
            elif not inside_special:
                inside_special = True  # Opening a special segment
                delimiter = char
        
        # Escape underscores only when NOT inside special characters
        if char == "_" and not inside_special:
            escaped.append(r"\_")
        else:
            escaped.append(char)
        
        i += 1

    return "".join(escaped)

def get_start_and_end_indexes(strings, S):
    indexes_start = []
    indexes_end = []
    for i, line in enum(S):
        if strings[0] in line:
            indexes_start.append(i)
        elif strings[1] in line:
            indexes_end.append(i)
        elif strings[0] in line and strings[1] in line:
            indexes_start.append(i)
            indexes_end.append(i)
            
    if len(indexes_start) != len(indexes_end):
        raise Exception('Some Latex code line is missing!')

    return indexes_start, indexes_end

def replace_fields_in_Obsidian_note(path_embedded_reference, look_for_fields, new_values):
	"""
	Replace the values of specified fields in an Obsidian note with new values.

	:param path_embedded_reference: Path to the Obsidian note file.
	:param look_for_fields: A list of field names to search for.
	:param new_values: A list of new values to replace the field values with.
	"""
	
	# Ensure we have the same number of fields and values to replace
	if len(look_for_fields) != len(new_values):
		raise ValueError("The number of fields and new values must be the same.")
	
	# Read the content of the file
	with open(path_embedded_reference, 'r', encoding='utf8') as file:
		lines = file.readlines()

	# Modify the lines where the fields are found
	for i, field in enumerate(look_for_fields):
		for j, line in enumerate(lines):
			if line.startswith(field):
				# Replace the field value with the new one
				lines[j] = f"{field} {new_values[i]}\n"
				break

	# Write the updated content back to the file
	with open(path_embedded_reference, 'w', encoding='utf8') as file:
		file.writelines(lines)

def get_fields_from_Obsidian_note(path_embedded_reference, look_for_fields):
    
    fields = ['' for _ in look_for_fields]
    
    with open(path_embedded_reference, 'r', encoding='utf8') as file:
        lines = file.readlines()

    for i, field in enumerate(look_for_fields):
        fields[i] = []
        found_field = False
        for line in lines:
            if line.startswith(field):
                fields[i].append(line.replace(field, '').replace('\n', '').strip())
                found_field = True
                # break
        if not found_field:
            fields[i] = ''                
    return fields

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
