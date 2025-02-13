import re
from helper_functions import *
from remove_markdown_comment import *

begin_type = ["\n\\begin{itemize}\n", "\n\\begin{enumerate}\n", "\n\\begin{todolist}\n"]
end_type = ["\\end{itemize}\n", "\\end{enumerate}\n", "\\end{todolist}\n"]

start_string = ['- ', '', '- [ ]']

def bullet_list_converter(S):

    # S = ''.join(S)
    cnd__do_not_add_new_line_if_it_already_exists = False

    latex = ""
    lines = S#.split("\n")
    tab_1 = "\t"

    INDENTATION = dict()

    for line in lines:

        match_numbered_list = re.match(r'^(\t*)\d+\.\s(.*)$', line)
        match_checkbox_list = re.match(r'^([\t ]*-\s\[\s\]\s*)(.*)$', line)
        match_bullet_list = re.match(r'^([\t ]*-\s*)(.*)$', line)

        match = False

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
            indentations = list(INDENTATION.keys())
            indentation = len(match.group(1)) - len(start_string[type_list])
            main_string = match.group(2)
            main_string_latex = tab_1 * (indentation+1) +  '\\item ' + main_string + '\n'
            if not cnd__do_not_add_new_line_if_it_already_exists:
                if main_string_latex.rstrip().endswith('\n'): 
                    main_string_latex += '\n'
                    
            if not str(indentation) in indentations:

                
                # FIX the problem when sometimes the next indentation jumps deeper than one level
                if len(indentations):
                    indentation_ceiling = int(max(indentations))+1
                    if indentation > indentation_ceiling:
                        indentation = indentation_ceiling
                #

                INDENTATION[str(indentation)] = 'open-' + str(type_list)

                pre_text = tab_1 * indentation + begin_type[type_list].replace('\n', '') + '\n'                       

            else:
                pre_text = ''

                next_indentations = [x for x in indentations if x>str(indentation)]
                next_indentations.sort(reverse=True)

                for i in next_indentations:
                    if INDENTATION[i].startswith('open'):
                        type_list_i = int(INDENTATION[i][-1])
                        pre_text += tab_1 * int(i) + end_type[type_list_i].replace('\n', '') + '\n' 
                        INDENTATION[i] = 'closed'
                        INDENTATION.pop(i)

            latex += pre_text + main_string_latex

        else:

            # close any unclosed lists
            s, INDENTATION = close_list(INDENTATION)
            latex += s

            # restart the indentation
            INDENTATION = dict()

            add_line = line
            if not cnd__do_not_add_new_line_if_it_already_exists:
                # if add_line.rstrip().endswith('\n'): 
                if not is_in_table_line(line):
                    add_line += '\n'

            latex += add_line


    s, INDENTATION = close_list(INDENTATION)
    latex += s

    LATEX = latex.split("\n")
    return get_list_of_separate_string_lines(LATEX)
    # return latex.split("\n")


def close_list(INDENTATION):

    indentations = list(INDENTATION.keys())
    indentations.sort(reverse=True)

    s = ''

    for i in indentations:
        if INDENTATION[i].startswith('open'):
            type_list_i = int(INDENTATION[i][-1])
            s += "\t" * int(i) + end_type[type_list_i]
            INDENTATION[i] = 'closed'

    return s, INDENTATION


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

