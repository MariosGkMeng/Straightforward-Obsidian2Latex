import re
import os

# For recognizing file names, section names, block names
SPECIAL_CHARACTERS = " ,'%💬⚠💼🟢➕❓❌🔴✔🧑☺📁⚙🔒🤔🟡🔲💊💡🤷‍♂️▶📧🔗🎾👨‍💻📞💭📖ℹ🤖🏢🧠🕒👇📚👉0-9\(\)\(\)\.\-\s"
from remove_markdown_comment import *
from list_of_separate_lines import *


def find_label_in_equation(input_string):
    label_pattern = re.compile(r'\\label\s*{\s*(?:eq__block_)([^}]+)\s*}')
    label_match = label_pattern.search(input_string)
    return label_match


def EQUATIONS__convert_non_numbered_to_numbered(S0):


    S = S0
    pattern = re.compile(r'(\$\$)(.*?)(\$\$)')

    for i, s in enumerate(S):
        matches = pattern.findall(s)
        text = s

        if matches:
            for match in matches:
                equation = match[1].strip()
                
                
                # Check for label in the text after equation
                label_match = find_label_in_equation(s)

                if label_match:
                    label_name = label_match.group(1)
                    
                    modified_equation = f'\n\\begin{{equation}} \\label{{eq:{label_name}}} \n\t{equation}'
                    
                    equation = equation.replace(label_match.group(), '')  # Remove the label in the equation


                else:
                    modified_equation = f'\n\\begin{{equation}}\n\t{equation}'
                
                modified_equation += f'\n\\end{{equation}}\n'
            
            # Check and add newline before "\begin{equation}" if it's not at the beginning of a line
            text = modified_equation 

            # Add a new line after \end{equation} if there's any text after it
            text = re.sub(r'\\end{equation}(\S)', r'\\end{equation}\n\1', text)

        S[i] = text.strip()

    return S


def add_new_line_equations(S0):

    # This function assumes that the '\n' symbol hasn't been added yet

    method = 2 # 1 or 2

    S = S0

    if method==1:

        # under dev.
        S = [s for s in S]
         
    elif method==2:

        for i, s in enum(S):

            if not s.endswith('$$') and s.endswith('$'):
                if i<len(S):
                    # add new line after the equation
                    S[i+1] = '\n' + S[i+1]

            if not s.startswith('$$') and s.startswith('$'):
                if i>0: 
                    if not S[i-1].endswith('\n'):
                        S[i-1] = S[i-1] + '\n'*2
                    else:
                        S[i-1] = S[i-1] + '\n'

            # if not s.endswith('$$') and s.endswith('$'):
            #     if i<len(S):


    else:
        raise Exception("Nothing coded for this case!")

    return S


import re

def EQUATIONS__correct_aligned_equation(latex_equations):

    """

    Aligned equations in obsidian are written in the format:
    $$ \begin{aligned}
    E_{g}(t)&=\frac{1}{N} \sum_{i} \big< (\bar{z}_{i}-z_{i})^{2} \big>  + \sigma_{\epsilon}^{2}  \\
    &= \frac{1}{N} \sum_{i}\left[(\sigma_{\bar{w}}^{2}+(\sigma_{w}^{0})^{2})e^{- \frac{2\lambda_{i}t}{\tau}} 
    +\frac{\sigma_{\epsilon}^{2}}{\lambda_{i}}(1-e^{- \frac{\lambda_{i}t}{\tau}})^{2} \right] &&
    \end{aligned}$$

    However, this is not the exact format that works with LateX.

    THe desired format would be:

    \begin{equation}
        \begin{split}
            E_{g}(t)&=\frac{1}{N} \sum_{i} \big< (\bar{z}_{i}-z_{i})^{2} \big>  + \sigma_{\epsilon}^{2}  \\
            &= \frac{1}{N} \sum_{i}\left[(\sigma_{\bar{w}}^{2}+(\sigma_{w}^{0})^{2})e^{- \frac{2\lambda_{i}t}{\tau}} 
            +\frac{\sigma_{\epsilon}^{2}}{\lambda_{i}}(1-e^{- \frac{\lambda_{i}t}{\tau}})^{2} \right] &&
        \end{split}
    \end{equation}

    """

    complete_equation = ''.join(latex_equations)

    pattern = r'\$\$\s*\\begin{aligned}\s*(.*?)\s*\\end{aligned}(\s*\$\$\\label\{(eq__block_[^}]+)\})?'

    equation_match = re.search(pattern, complete_equation, re.DOTALL)

    if equation_match:
        equation_content = equation_match.group(1)
        equation_content = equation_content.split('\\\\')
        equation_content = ('\\\\' + '\n' + '\t'*1).join(equation_content)

        label_match = equation_match.group(2)

        label_name = ""
        if label_match:
            label_name = re.search(r'\\label\{(eq__block_([^}]+))\}', label_match).group(1)
            label_name = label_name.replace("eq__block_", "")

        label_statement = rf"\label{{eq:{label_name}}}" if label_name else ""

        new_equation = rf"""
\begin{{equation}}{label_statement}
    \begin{{aligned}}
        {equation_content.strip()}
    \end{{aligned}}
\end{{equation}}
"""

        new_equation = new_equation.split('\n')
        new_equation = new_equation[1:-1]
        return new_equation

    else:
        return None




def EQUATIONS__check_and_correct_aligned_equations(S0):

    indexes_start = []
    indexes_end = []

    for i, line in enum(S0):
        if '\\begin{aligned}' in line:
            indexes_start.append(i)
        elif '\end{aligned}' in line:
            indexes_end.append(i)

    if len(indexes_start) != len(indexes_end):
        raise Exception('Some Latex code line is missing!')
    

    INDEXES = [0]
    for i, idx in enum(indexes_start):
        INDEXES.append(idx)
        INDEXES.append(indexes_end[i])

    INDEXES.append(len(S0))

    LISTS = []
    for i, idx in enum(INDEXES[:-1]):
        j = idx
        j1 = INDEXES[i+1]
        if i%2==0:
            # no need for modification
            LISTS.append(S0[j+1:j1])
        else:
            # need modification
            LISTS.append(EQUATIONS__correct_aligned_equation(S0[j:j1+1]))

    S0_modified = []
    for list in LISTS:
        S0_modified += list

    return S0_modified


def EQUATIONS__convert_equation_referencing(S0):


    """
    Converts the note linking of the format "[[eq__block_equationName]]" to "\\ref{eq:equationName}"
    """


    # Regular expression pattern to match the specified format
    pattern = r'\[\[eq__block_(.*?)\]\]'
    
    S = S0
    for i, s in enum(S):
        # Using re.sub to replace the matched pattern with the desired text
        replaced_text = re.sub(pattern, r'\\ref{eq:\1}', s)

        S[i] = replaced_text
    

    return S