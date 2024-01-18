import re
import os

# For recognizing file names, section names, block names
SPECIAL_CHARACTERS = " ,'%💬⚠💼🟢➕❓❌🔴✔🧑☺📁⚙🔒🤔🟡🔲💊💡🤷‍♂️▶📧🔗🎾👨‍💻📞💭📖ℹ🤖🏢🧠🕒👇📚👉0-9\(\)\(\)\.\-\s"
from remove_markdown_comment import *
from list_of_separate_lines import *
from path_searching import *

def find_label_in_equation(input_string):
    label_pattern = re.compile(r'\\label\s*{\s*(?:eq__block_)([^}]+)\s*}')
    label_match = label_pattern.search(input_string)
    return label_match


def EQUATIONS__convert_non_numbered_to_numbered(S0):
    S = S0

    # with the following pattern, the equation label will only be identified if it starts with "eq__block_"
    pattern = re.compile(r'\$\$\s*(.*?)\s*\$\$(?:\s*\\label\{(eq__block_)([^}]+)\})?')

    for i, s in enumerate(S):
        matches = pattern.findall(s)
        text = s

        if matches:

            # put a new line between any text before the equation and the equation
            i_eq = text.find("$$")
            if i_eq > 0:
                text = text[:i_eq] + "\n" + text[i_eq+1:]
            #

            for match in matches:
                equation = match[0].strip()
                label_prefix = match[1] if match[1] else ""
                label_name = match[2] if match[2] else ""

                # Create the modified equation with the label if present
                modified_equation = f'\\begin{{equation}}' + (f' \\label{{eq:{label_name}}}' if label_name else '') + f'\n\t{equation}\n\\end{{equation}}'

                # Replace the original equation with the modified one
                text = text.replace(f'${match[0]}$', modified_equation)

                # Remove the extra label after the end{equation}
                text = re.sub(r'\$\s*\\label\{eq__block_[^\}]+\}', '', text)

        S[i] = text.strip()


    # Sometimes we still have unwanted "$" symbol before "\\begin{equation}", therefore need to remove it
    pattern_remove_unwanted_previous_dollar = r'\$\s*(\\begin{equation})'
    S = [re.sub(pattern_remove_unwanted_previous_dollar, r'\1', s) for s in S]

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
    
    if len(indexes_start) == 0:
        return S0

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


            # Check if there is any text before the "$$ \\begin{aligned}" text, so we create a separate line with it
            match_equation = re.search(r'^(.*?)\$\$\s*\\begin{aligned}', S0[j])
            if match_equation:
                text_before_equation_that_was_on_same_line = match_equation.group(1)

                if len(text_before_equation_that_was_on_same_line) > 0:
                    LISTS.append([text_before_equation_that_was_on_same_line])
                    S0[j] = S0[j].replace(text_before_equation_that_was_on_same_line, "") # removing it for good measure
            #


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
        replaced_text = re.sub(pattern, r'\\cref{eq:\1}', s)

        S[i] = replaced_text
    

    return S

def FIGURES__convert_figure_referencing(S0):


    """
    Converts the note linking of the format "[[figure__block_figureName]]" to "\\ref{fig:figureName}"
    """


    # Regular expression pattern to match the specified format
    pattern = r'\[\[figure__block_(.*?)\]\]'
    
    S = S0
    for i, s in enum(S):
        # Using re.sub to replace the matched pattern with the desired text
        replaced_text = re.sub(pattern, r'\\cref{\1}', s)

        S[i] = replaced_text
    

    return S


def EQUATIONS__prepare_label_in_initial_Obsidian_equation(content__unfold, embedded_ref):
    
    """
    For an equation of the format '$$equation$$', it adds the label at the end, so that 
    other functions in this file recognize it and place it in the correct LateX manner.
    """


    block_prefix = "eq__block_"

    # get the label of the equation from the note name
    equation_label = embedded_ref.replace(block_prefix,"").replace(".md", "")
    if len(equation_label)==0 or equation_label == "_":
        equation_label = block_prefix+'empty_label'
    else:
        equation_label = block_prefix+equation_label

    # add the equation label afterwards, so that later it is integrated in the latex file
    anything_after_equation_that_can_be_removed_by_rstrip = content__unfold[-1].replace(content__unfold[-1].rstrip(), "")    
    
    content__unfold[-1] = content__unfold[-1].rstrip()
    content__unfold[-1] += '\label{' + equation_label + '}' + anything_after_equation_that_can_be_removed_by_rstrip

    return content__unfold


def FIGURES__get_figure(content__unfold, embedded_ref, path_embedded_reference, PARS):


    look_for_fields = ['size_in_latex:: ', 'caption_short:: ', 'caption_long:: ']
    fields = ['' for x in look_for_fields]

    extensions = ['.png', '.jpg', '.pdf']

    with open(path_embedded_reference, 'r', encoding='utf8') as file:
        lines = file.readlines()

    for i, field in enum(look_for_fields):
        for line in lines:
            if line.startswith(field):
                fields[i] = line.replace(field, '').replace('\n', '').strip()

        
    #converted_image_text = images_converter([[0, get_embedded_reference_path(cc, PARS)]], PARS['⚙']['figures'])
    cc=content__unfold[0].replace('![[',"").replace(']]', '')
    for extension in extensions:
        if extension in cc:
            ii=cc.find(extension)
            break
    
    try:
        cc = cc[:ii]
    except:
        raise Exception('Did not find any extension among: ' + ', '.join(extensions))
    

    label = embedded_ref.replace('figure__block_', '')
    converted = images_converter([[0, get_embedded_reference_path(cc + extension, PARS)]], PARS['⚙']['figures'], [look_for_fields, fields], label)

    return converted



def images_converter(images, PARAMETERS, fields, label):

    '''
    Converts Images given the path of the image file
    '''

    # NOTES:
    # --- ", height=0.5\\textheight" addition causes the aspect ratio to break

    caption_short = 'Caption short'
    caption_long = 'Caption long'

    if len(fields[1][0]) > 0: 
        figure_width = fields[1][0]
    else:
        figure_width = 0.7

    if len(fields[1][1]) > 0: 
        caption_short = fields[1][1]
    else:
        caption_short = ''

    if len(fields[1][2]) > 0: 
        caption_long = fields[1][2]
    else:
        caption_long = ''


    TO_PRINT = []
    for IM in images:
        path_img = '"' + IM[1].replace('\\', '/') + '"'
        # label_img = IM[1].split('\\')[-1]
        TO_PRINT.append(' \n'.join([
        '\\begin{figure}' + '\label{fig:'+label+'}',
        '	\centering',
        '	\includegraphics[width=' + str(figure_width) + '\linewidth]'+\
            '{"'+path_img+'"}',
        '	\caption['+caption_short+']{'+caption_long+'}',
        '   \captionsetup{skip=-10pt} % Adjust the skip value as needed'*PARAMETERS['reduce spacing between figures'],
        '\end{figure}']))

    return TO_PRINT
