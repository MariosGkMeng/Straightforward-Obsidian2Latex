import os
import numpy as np
import re
import datetime


def remove_emojis(text: str) -> str:
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags
        "\U00002700-\U000027BF"  # dingbats
        "\U0001F900-\U0001F9FF"  # supplemental symbols and pictographs
        "\U0001FA70-\U0001FAFF"  # symbols & pictographs extended-A
        "\U00002600-\U000026FF"  # misc symbols
        "\U00002B00-\U00002BFF"  # arrows
        "]+",
        flags=re.UNICODE
    )
    return emoji_pattern.sub("", text)


def remove_inlink_code_format(text: str) -> str:
    # Remove backticks around inline code in the format `code`
    return re.sub(r'`([^`]+)`', r'\1', text)


def detect_code_snippet(strings):
    code_detected = False
    language_detected = None
    
    code_languages = ['python', 'dataviewjs', 'dataview', 'javascript', 'java', 'c++', 'c#', 'html', 'css', 'bash', 'ruby', 'go', 'php']
    
    for s in strings:
        # Check for Markdown-style code block
        code_block_match = re.search(r'```\s*(\w+)?\n', s)
        if code_block_match:
            code_detected = True
            lang = code_block_match.group(1)            
            if lang and lang.lower() in code_languages:
                language_detected = lang.lower()
            break
        
        # Check for inline code-like syntax
        if any(kw in s for kw in ['def ', 'class ', 'function ', 'console.log', '<html>', '#include']):
            code_detected = True
            # Try to guess language based on keywords
            if 'def ' in s or 'class ' in s:
                language_detected = 'python'
            elif 'function ' in s or 'console.log' in s:
                language_detected = 'javascript'
            elif '<html>' in s:
                language_detected = 'html'
            elif '#include' in s:
                language_detected = 'c/c++'
            break

    return code_detected, language_detected


def get_file_cday(file_path):
    """
    Returns the creation date of the given file as a formatted string (YYYY-MM-DD).
    """
    if not os.path.exists(file_path):
        return "Unknown"

    # On Windows, use creation time
    if os.name == 'nt':
        ctime = os.path.getctime(file_path)
    else:
        # On Unix-like systems, use birth time if available; otherwise, fallback to modification time
        stat = os.stat(file_path)
        ctime = getattr(stat, 'st_birthtime', stat.st_mtime)

    return datetime.datetime.fromtimestamp(ctime).strftime('%Y/%m/%d')


def replace_outside_brackets(s, replace_list, replacement_list):
    replace_map = dict(zip(replace_list, replacement_list))
    
    def replacer(match):
        if match.group(1):  # Text inside [[ ]], return as is
            return match.group(1)
        else:  # Text outside [[ ]], replace characters
            return ''.join(replace_map.get(c, c) for c in match.group(2))
    
    pattern = r'(\[\[.*?\]\])|([^\[\]]+)'
    return re.sub(pattern, replacer, s)

def escape_underscore(text, ignore_brackets=False):
    escaped = []
    inside_special = False  # Track whether we're inside a special segment
    inside_brackets = False  # Track whether we're inside [[ ]]
    delimiter = None  # Store the current active delimiter
    
    i = 0
    while i < len(text):
        char = text[i]
        
        # Track [[ ]] sections
        if text[i:i+2] == "[[":
            inside_brackets = True
        elif text[i:i+2] == "]]":
            inside_brackets = False
        
        # Toggle inside_special state when encountering special characters
        if char in {"$", "`"} and not inside_brackets:
            if inside_special and char == delimiter:
                inside_special = False  # Closing the special segment
                delimiter = None
            elif not inside_special:
                inside_special = True  # Opening a special segment
                delimiter = char
        
        # Escape underscores only when NOT inside special characters or (unless ignore_brackets) brackets
        if char == "_" and not inside_special and (ignore_brackets or not inside_brackets):
            escaped.append(r"\_")
        else:
            escaped.append(char)
        
        i += 1

    return "".join(escaped)

def get_start_and_end_indexes(strings, S):
    indexes_start = []
    indexes_end = []
    for i, line in enumerate(S):
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
    
    fields = [[] for _ in look_for_fields]
    
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

def write_Obsidian_table(table, return_lines=True, fill_empty_cells_with_dash=True):
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
    
    # Column titles
    if 0 in keys:
        lines.append('| ' + ' | '.join([f'**{escape_underscore(table[0][key], ignore_brackets=True)}**' for key in table[0].keys()]) + ' |')
    else:
        lines.append(''.join('| ' * cols) + '|')

    # Separator
    lines.append(''.join('| --- ' * cols) + '|')

    # Table rows
    for i in keys:
        if i != 0:
            row_cells = []
            for col in range(1, cols + 1):
                if col in table[i].keys():
                    str_append = escape_underscore(table[i][col], ignore_brackets=True) if len(table[i][col])>0 else ('-' if fill_empty_cells_with_dash else '')
                    # print(escape_underscore(table[i][col]))
                    row_cells.append(str_append)
                else:
                    row_cells.append('-' if fill_empty_cells_with_dash else '')
            lines.append('| ' + ' | '.join(row_cells) + ' |')
    
    if return_lines:
        return [l + '\n' for l in lines]
    return '\n'.join(lines)


def get_list_of_separate_string_lines(S):

    result_list = []

    for string in S:
        # Check if the string contains line breaks
        if "\n" in string:
            # Split the string into separate lines
            lines = string.split("\n")
            # Extend the result list with the separated lines
            result_list.extend(lines)
        else:
            # If no line break, add the string as it is
            result_list.append(string)

    return result_list


def is_note(s):
    if s.strip().startswith('[[') and s.strip().endswith(']]'):
        return True
    return False

def is_path(path: str) -> bool:
    """
    Checks if a string is likely a folder path, including support for emojis and special Unicode.
    """
    INVALID_PATH_CHARS = r'<>:"|?*'

    if not path or not isinstance(path, str):
        return False

    # Remove quotes and trim
    path = path.strip().strip('"').strip("'")

    # Must contain a slash or backslash to look like a path
    if not any(sep in path for sep in ('/', '\\')):
        return False

    # Reject if it contains invalid filesystem characters
    if any(char in path for char in INVALID_PATH_CHARS):
        return False

    # Heuristic: Reject if it looks like a filename with extension
    if re.search(r'\.[a-zA-Z0-9]{1,5}$', os.path.basename(path)):
        return False

    return True

def is_obsidian_note(s):
    if s.strip().startswith('[[') and s.strip().endswith(']]'):
        return True
    return False
        
def replace_markdown_headers(content):
    """
    Replace Markdown headers in content with LaTeX equivalents,
    and return a list of detected sections as [index, title].
    """
    sections = []

    header_map = [
        (r'######## (.*)', r'\\paragraph{\1} \\hspace{0pt} \\\\'),
        (r'####### (.*)', r'\\paragraph{\1} \\hspace{0pt} \\\\'),
        (r'###### (.*)', r'\\paragraph{\1} \\hspace{0pt} \\\\'),
        (r'##### (.*)', r'\\paragraph{\1} \\hspace{0pt} \\\\'),
        (r'#### (.*)', r'\\paragraph{\1} \\hspace{0pt} \\\\'),
        (r'### (.*)', r'\\subsubsection{\1}'),
        (r'## (.*)', r'\\subsection{\1}'),
        (r'# (.*)', r'\\section{\1}')
    ]

    for i, line in enumerate(content):
        original_line = line
        line = line.replace('%%', '')  # Remove '%%' before replacements

        for md_pattern, latex_repl in header_map:
            new_line = re.sub(md_pattern, latex_repl, line)
            if new_line != line:
                # Save the section if header changed
                header_title = re.sub(md_pattern, r'\1', line).strip()
                sections.append([i, header_title])
                line = new_line  # update line for next iteration

        content[i] = line

    return content, sections


# # Example usage:
# s = "Hello [[keep this ☺]] world! ☺😀"
# replace_list = ["☺", "😀"]
# replacement = "X"
# print(replace_outside_brackets(s, replace_list, replacement))
