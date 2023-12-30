import re
from list_of_separate_lines import *
def bullet_list_converter(S):

    # S = ''.join(S)

    latex = ""
    lines = S#.split("\n")
    tab_1 = "\t"

    begin_type = ["\\begin{itemize}\n", "\\begin{enumerate}\n"]
    end_type = ["\\end{itemize}\n", "\\end{enumerate}\n"]

    INDENTATION = dict()

    for line in lines:

        match_bullet_list = re.match(r'^([\t ]*-\s*)(.*)$', line)
        match_numbered_list = re.match(r'^(\t*)\d+\.\s(.*)$', line)

        if match_bullet_list:
            type_list = 0
            match = match_bullet_list

        elif match_numbered_list:
            type_list = 1
            match = match_numbered_list

        else:
            match = False

        if match:
            indentations = list(INDENTATION.keys())
            indentation = len(match.group(1))
            main_string = match.group(2)
            main_string_latex = tab_1 * (indentation+1) +  '\\item ' + main_string + "\n"
            if not str(indentation) in indentations:

                
                # FIX the problem when sometimes the next indentation jumps deeper than one level
                if len(indentations):
                    indentation_ceiling = int(max(indentations))+1
                    if indentation > indentation_ceiling:
                        indentation = indentation_ceiling
                #

                INDENTATION[str(indentation)] = 'open-' + str(type_list)

                pre_text = tab_1 * indentation + begin_type[type_list]                        

            else:
                pre_text = ''

                next_indentations = [x for x in indentations if x>str(indentation)]
                next_indentations.sort(reverse=True)

                for i in next_indentations:
                    if INDENTATION[i].startswith('open'):
                        type_list_i = int(INDENTATION[i][-1])
                        pre_text += tab_1 * int(i) + end_type[type_list_i]
                        INDENTATION[i] = 'closed'

            latex += pre_text + main_string_latex

        else:

            # close any unclosed lists
            s, INDENTATION = close_list(INDENTATION)
            latex += s

            # restart the indentation
            INDENTATION = dict()

            latex += line + '\n'


    s, INDENTATION = close_list(INDENTATION)
    latex += s

    LATEX = latex.split("\n")
    return get_list_of_separate_string_lines(LATEX)
    # return latex.split("\n")


def close_list(INDENTATION):

    end_type = ["\\end{itemize}\n", "\\end{enumerate}\n"]

    indentations = list(INDENTATION.keys())
    indentations.sort(reverse=True)

    s = ''

    for i in indentations:
        if INDENTATION[i].startswith('open'):
            type_list_i = int(INDENTATION[i][-1])
            s += "\t" * int(i) + end_type[type_list_i]
            INDENTATION[i] = 'closed'

    return s, INDENTATION
