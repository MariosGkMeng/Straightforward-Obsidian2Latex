import re
from helper_functions import *
from remove_markdown_comment import *

# Remove leading/trailing newlines from environment commands
begin_type = [r"\begin{itemize}", r"\begin{enumerate}", r"\begin{todolist}"]
end_type = [r"\end{itemize}", r"\end{enumerate}", r"\end{todolist}"]

start_string = ['- ', '', '- [ ]']

def bullet_list_converter(S):

    # S = ''.join(S)
    cnd__do_not_add_new_line_if_it_already_exists = False # Kept for potential future use, but logic below aims for single newlines

    latex_lines = [] # Store processed lines
    lines = S # Assume S is already a list of lines
    tab_1 = "\t"

    INDENTATION = dict()
    inside_list_env = False # Track if we are inside any list environment

    for idx, line in enumerate(lines):
        original_line = line # Keep original for non-list lines
        line = line.rstrip() # Work with lines without trailing whitespace/newlines

        match_numbered_list = re.match(r'^(\t*)\d+\.\s(.*)$', line)
        match_checkbox_list = re.match(r'^([\t ]*-\s\[\s\]\s*)(.*)$', line)
        match_bullet_list = re.match(r'^([\t ]*-\s*)(.*)$', line)

        match = False
        type_list = -1

        # Determine list type if applicable
        if not line.startswith('---'): 
            if match_bullet_list and not match_checkbox_list:
                type_list = 0
                match = match_bullet_list
            elif match_numbered_list:
                type_list = 1
                match = match_numbered_list
            elif match_checkbox_list:
                type_list = 2
                match = match_checkbox_list

        if match:
            # --- Start or continue a list item ---
            current_indentations = list(INDENTATION.keys())
            indentation_str = str(len(match.group(1)) - len(start_string[type_list]))
            main_string = match.group(2)
            indentation = int(indentation_str)

            # Ensure correct indentation level (max 1 deeper than previous)
            if len(current_indentations):
                indentation_ceiling = int(max(current_indentations)) + 1
                if indentation > indentation_ceiling:
                    indentation = indentation_ceiling
                    indentation_str = str(indentation)
            
            # Close deeper levels if necessary
            levels_to_close = sorted([int(i) for i in current_indentations if int(i) > indentation], reverse=True)
            for level in levels_to_close:
                level_str = str(level)
                if INDENTATION[level_str].startswith('open'):
                    closed_type_list = int(INDENTATION[level_str][-1])
                    latex_lines.append(tab_1 * level + end_type[closed_type_list])
                    INDENTATION.pop(level_str)
            
            # Open new level if necessary
            if indentation_str not in INDENTATION:
                latex_lines.append(tab_1 * indentation + begin_type[type_list])
                INDENTATION[indentation_str] = 'open-' + str(type_list)
                inside_list_env = True
            
            # Add the item
            latex_lines.append(tab_1 * (indentation + 1) + '\\item ' + main_string)
            
        else:
            # --- Not a list item line ---
            # Close any open list environments
            if inside_list_env:
                levels_to_close = sorted([int(i) for i in INDENTATION.keys()], reverse=True)
                for level in levels_to_close:
                     level_str = str(level)
                     if INDENTATION[level_str].startswith('open'):
                        closed_type_list = int(INDENTATION[level_str][-1])
                        latex_lines.append(tab_1 * level + end_type[closed_type_list])
                INDENTATION = dict() # Reset indentation tracking
                inside_list_env = False
            
            # Add the original non-list line (preserving its original ending)
            latex_lines.append(original_line.rstrip('\n')) 

    # Final check: Close any remaining open lists at the end of the input
    if inside_list_env:
        levels_to_close = sorted([int(i) for i in INDENTATION.keys()], reverse=True)
        for level in levels_to_close:
            level_str = str(level)
            if INDENTATION[level_str].startswith('open'):
                closed_type_list = int(INDENTATION[level_str][-1])
                latex_lines.append(tab_1 * level + end_type[closed_type_list])
        INDENTATION = dict()

    # Ensure each line ends with exactly one newline for writing
    return [line + '\n' for line in latex_lines]


def close_list(INDENTATION): # This function might be redundant now with the new logic
    # Keeping it just in case, but it should not be called if the main loop is correct
    indentations = list(INDENTATION.keys())
    indentations.sort(reverse=True)

    s = ''
    lines_to_add = []

    for i in indentations:
        if INDENTATION[i].startswith('open'):
            type_list_i = int(INDENTATION[i][-1])
            lines_to_add.append("\t" * int(i) + end_type[type_list_i])
            INDENTATION[i] = 'closed'

    return lines_to_add, INDENTATION # Return lines instead of a single string


import re

def is_part_of_list(line):
    """
    Checks if the input string is part of a list (bullet or enumerated),
    including nested lists with varying indentation.

    Args:
        line (str): The input string to check.

    Returns:
        bool: True if the line is part of a list, False otherwise.
    
    # Example usage
    lines = [
        "- Top-level bullet",
        "   - Nested bullet with spaces",
        "1. Top-level enumerated",
        "   1.1 Nested enumerated",
        "a. Top-level enumerated with letters",
        "   a.1 Nested enumerated with letters and spaces",
        "       - Deeply nested bullet",
        "       1. Deeply nested enumerated",
        "Just regular text here",
        "+ Another bullet style"
    ]

    for line in lines:
        print(f"'{line}' -> {is_part_of_list(line)}")
    """
    
    # Pattern to match bullets or enumerated lists
    list_pattern = r'^\s*([-*+]\s+|\d+\.\d*|[a-zA-Z]\.|[ivxIVX]+\.)\s*.*$'
    
    return bool(re.match(list_pattern, line))

