import re
import os
import numpy as np

# For recognizing file names, section names, block names
SPECIAL_CHARACTERS = " ,'%💬⚠💼🟢➕❓❌🔴✔🧑☺📁⚙🔒🤔🟡🔲💊💡🤷‍♂️▶📧🔗🎾👨‍💻📞💭📖ℹ🤖🏢🧠🕒👇📚👉0-9\(\)\(\)\.\-\s"
from remove_markdown_comment import *
from list_of_separate_lines import *
from path_searching import *


ID__TABLES__alignment__center = 0
ID__TABLES__alignment__right  = 1
ID__TABLES__alignment__middle = 2


ID__TABLES__PACKAGE__longtblr   = 0
ID__TABLES__PACKAGE__tabularx   = 1
ID__TABLES__PACKAGE__long_table = 2

ID__CNV__TABLE_STARTED      = 0
ID__CNV__TABLE_ENDED        = 1
ID__CNV__IDENTICAL          = 2

ID__STYLE__BOLD             = 0
ID__STYLE__HIGHLIGHTER      = 1
ID__STYLE__ITALIC           = 2


# ⚠ does not work for longtblr!
CMD__TABLE__TABULARX__CENTERING = '\\newcolumntype{Y}{>{\\centering\\arraybackslash}X}'


# def regex_patterns_for_equations():
    

def get_start_and_end_indexes(strings, S):
    indexes_start = []
    indexes_end = []
    for i, line in enum(S):
        if strings[0] in line:
            indexes_start.append(i)
        elif strings[1] in line:
            indexes_end.append(i)        
            
    if len(indexes_start) != len(indexes_end):
        raise Exception('Some Latex code line is missing!')

    return indexes_start, indexes_end


def find_label_in_equation(input_string):
    label_pattern = re.compile(r'\\label\s*{\s*(?:eq__block_)([^}]+)\s*}')
    label_match = label_pattern.search(input_string)
    return label_match


def EQUATIONS__convert_non_numbered_to_numbered(S0):
        
    """
    Converts equations from the format "$$equation_here$$\\label{label}" to:
    "\begin{equation} \\label{label} \n \t equation_here \n \end{equation}"
    """

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

                # Bad programming patch (due to not being able to fix it with Regex)
                # Doing this because the equation will not be corrected when there's any between the equation body and the |"$" symbol
                for k in range(4):
                    text = text.replace(' '*k+'$', '$').replace('$'+' '*k, '$')
                #

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

    indexes_start, indexes_end = get_start_and_end_indexes(['\\begin{aligned}', '\end{aligned}'], S0)
        
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

def convert_referencing(S0, mode):
    
    # Regular expression pattern to match the specified format
    pattern = [r'\[\[table__block_(.*?)\]\]', r'\[\[figure__block_(.*?)\]\]']
    replacement = [r'\\cref{tab:\1}', r'\\cref{fig:\1}']
    
    S = S0
    if mode == 'figures':
        idx = 0
    elif mode == 'tables':
        idx = 1
    else:
        raise NotImplementedError
    
    for i, s in enum(S):
        # Using re.sub to replace the matched pattern with the desired text
        replaced_text = re.sub(pattern[idx], replacement[idx], s)
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

    add_new_line_after_label = True

    if add_new_line_after_label:
        tmp1 = '\n'
    else:
        tmp1 = ''

    content__unfold[-1] += '\label{' + equation_label + '}' + anything_after_equation_that_can_be_removed_by_rstrip + tmp1

    return content__unfold


def get_fields_from_Obsidian_note(path_embedded_reference, look_for_fields):
    
    fields = ['' for _ in look_for_fields]
    
    with open(path_embedded_reference, 'r', encoding='utf8') as file:
        lines = file.readlines()

    for i, field in enum(look_for_fields):
        for line in lines:
            if line.startswith(field):
                fields[i] = line.replace(field, '').replace('\n', '').strip()
                break
                
    return fields


def TABLES__get_table(content__unfold, embedded_ref, path_embedded_reference, PARS):
    
    fields_to_fetch = ['caption:: ', 'package:: ', 'widths:: ']
    fields_note = get_fields_from_Obsidian_note(path_embedded_reference, fields_to_fetch)
    caption = fields_note[0]
    package = fields_note[1]
    widths = [f.strip() for f in fields_note[2].split(',')]
    label = embedded_ref.replace('table__block_', '')
    embedded_tables_text = convert__tables(content__unfold, caption, package, label, widths, PARS)
    
    embedded_tables_text_1 = []
    for line in embedded_tables_text:
        if not line.endswith('\n'):
            line += '\n'
        embedded_tables_text_1.append(line)
    return embedded_tables_text_1

def FIGURES__get_figure(content__unfold, embedded_ref, path_embedded_reference, PARS):

    look_for_fields = ['size_in_latex:: ', 'caption_short:: ', 'caption_long:: ']
    fields = get_fields_from_Obsidian_note(path_embedded_reference, look_for_fields)
    extensions = ['.png', '.jpg', '.pdf']

    embedded_images_text = content__unfold[0]
    try:
        embedded_images = [x.replace(']]', '') for x in embedded_images_text.split("![[")[1:]]
    except:
        raise Exception("Probably could not find any images in your figure note file!")
    
    embedded_images_1 = []
    for image in embedded_images:
        if "|" in image: image = image[:image.find("|")+1].replace("|", "")
        embedded_images_1.append(image)
    
    embedded_images = embedded_images_1
    label = embedded_ref.replace('figure__block_', '')
    image_paths = [get_embedded_reference_path(x, PARS) for x in embedded_images]
    converted = images_converter(image_paths, PARS['⚙']['figures'], [look_for_fields, fields], label, PARS['📁']['tex-file'])

    return converted



def images_converter(images, PARAMETERS, fields, label, latex_file_path):

    '''
    Converts Images given the path of the image file
    '''

    # NOTES:
    # --- ", height=0.5\\textheight" addition causes the aspect ratio to break

    subfigure_text_width = 1/len(images)

    # get parameters of the latex figure command
    latex_figure_field = [0.7, '', ''] # the defaults

    # change defaults, if user put something
    for iF, f in enum(fields[1]):
        if len(f)>0: latex_figure_field[iF] = f 

    figure_width, caption_short, caption_long = latex_figure_field

    TO_PRINT = []


    cnd__include_subfigures = len(images) > 1
    cnd__no_subfigures = (not cnd__include_subfigures)
    begin_figure = '\\begin{figure}'*cnd__no_subfigures + '\\begin{subfigure}'*cnd__include_subfigures
    end_figure = '\end{figure}'*cnd__no_subfigures + '\end{subfigure}'*cnd__include_subfigures 
    
    fig_label = '\label{fig:'+label+'}'
    
    if PARAMETERS['put_figure_below_text']: 
        if not cnd__include_subfigures:
            begin_figure += '[H]'
        else:
            begin_figure += '[b]{'+ str(subfigure_text_width) +'\\textwidth}'

    for IM in images:
        path_img0 = IM.replace('\\', '/')

        img_directory = '/'.join(path_img0.split('/')[:-1])
        cndTmp1 = 0
        path_img = '"'*cndTmp1 + path_img0 + '"'*cndTmp1

        # check if image is in the same folder as the latex file (in which case, no need to have the absolute path)
        if (img_directory == '/'.join(latex_file_path.replace('\\', '/').split('/')[:-1])) or (not PARAMETERS['include_path']):
            path_img = path_img.replace(img_directory+'/', '')

        # label_img = IM.split('\\')[-1]
        TO_PRINT.append(' \n'.join([
        begin_figure,
        '	\centering',
        '	\includegraphics[width=' + str(figure_width)*cnd__no_subfigures + '\linewidth]' + '{"'+path_img+'"}',
        '	\caption['+caption_short+']'+('{'+caption_long+'}')*(len(caption_long)>0),
        '   \captionsetup{skip=-10pt} % Adjust the skip value as needed'*PARAMETERS['reduce spacing between figures'],
        '   '+fig_label*cnd__no_subfigures,
        end_figure]))

    y = []
    if cnd__include_subfigures:
        if PARAMETERS['put_figure_below_text']:
            begin_fig_global = '\\begin{figure}[H]\n'
        else:
            begin_fig_global = '\\begin{figure}\n'
        y.append(begin_fig_global)
        y.append('\centering\n')
        for fig_lines in TO_PRINT:
            y.append(fig_lines)
            y.append('\hfill\n')

        y.append('\caption{}\n')
        y.append(fig_label+'\n')
        y.append('\end{figure}\n')
    else:
        y = TO_PRINT

    return y


def convert__tables(S, caption, package, label, widths, PARS):
    '''
    Converts tables depending on the user's preferences    
    '''
    format_column_names_with_bold = True
    
    latex_table_prefix = '#Latex/Table/'
    latex_table_prefix_row_format_color = latex_table_prefix + 'Format/rowcolor/'
    TABLE_SETTINGS = PARS['⚙']['TABLES']
    if not package:
        package = TABLE_SETTINGS['package']
    else:
        latex_table_package_prefix = latex_table_prefix+'package/'
        if latex_table_package_prefix+'longtable' in package:
            package = ID__TABLES__PACKAGE__long_table
        elif latex_table_package_prefix+'tabularx' in package:
            package = ID__TABLES__PACKAGE__tabularx
        elif latex_table_package_prefix+'longtblr' in package:
            package = ID__TABLES__PACKAGE__longtblr
        else:
            raise NotImplementedError
        
    # Mask internal links that have aliases, otherwise the converter gets confused
    mask_alias = "--alias--"
    for i, s in enum(S):
        S[i] = s.replace("\\|", mask_alias)
    #     
        
    add_txt = ''
    if (ID__TABLES__alignment__center in TABLE_SETTINGS['alignment']) \
        and package == ID__TABLES__PACKAGE__longtblr:
        add_txt = '\centering '

    has_custom_widths = False
    if len(widths[0])>0:
        has_custom_widths = True

    if has_custom_widths:
        table_width_custom_0 = ''.join(["|p{" + w + "}" for w in widths]) + '|'

    # After having found the table
    ## We expect that the 1st line defines the columns

    iS_table_start = -1

    for iS, s in enumerate(S):
        if is_in_table_line(s):
            cols = s.split('|')
            iS_table_start = iS
            break
          
          
    if iS_table_start==-1:
        raise Exception("Did not find any tables!")
    
    cols = [[x.lstrip().rstrip() for x in cols if len(x)>0 and x!='\n']]

    if format_column_names_with_bold:
        cols = [[f'**{x}**' for x in sublist] for sublist in cols]

    data = []
    for s in S[iS_table_start+2:]:
        c = s.split('|')
        c = [x.lstrip().rstrip() for x in c if len(x.lstrip().rstrip())>0 and x!='\n']
        
        # check for table commands
        latex_command_in_row = np.any([latex_table_prefix in ci for ci in c])
        if latex_command_in_row:
            # check for latex row color command
            try: #if np.any([latex_table_prefix_row_format_color in ci for ci in c]):
                i_c, cell_with_the_command = [(i, ci) for i, ci in enumerate(c) if latex_table_prefix_row_format_color in ci][0]
                
                text = c[i_c]
                pattern = rf'{re.escape(latex_table_prefix_row_format_color)}([a-zA-Z]+)'
                # Search for the pattern in the text
                match = re.search(pattern, text)
                # Extract and print the matched text if it exists
                if match:
                    color = match.group(1)
                else:
                    raise Exception("You probably have written the syntax of latex table row color formatting wrong!")

                text_to_replace = latex_table_prefix_row_format_color+color
                replacement_text = '\\rowcolor{' + color + '}'
                cell_with_the_command = cell_with_the_command.replace(text_to_replace, replacement_text)
                # Adding the replacement text in front, because it is inside commands (cheap patch for now ➕)
                c[i_c] = (replacement_text + ' ')*0 + cell_with_the_command
                
            except:
                None
            
        data.append(c)

    y = cols + data

    # CONVERT
    N_cols = len(cols[0])

    latex_table = []
    addText = ''
    for i, c in enum(y):
        c1 = [add_txt + x for x in c]
        if i==0: 
            if TABLE_SETTINGS['any-hlines-at-all']:
                addText = ' \hline'
        else:
            if TABLE_SETTINGS['hlines-to-all-rows']:
                addText = ' \hline'
        latex_table.append('    ' + " & ".join(c1) + ' \\\\' + addText)

    lbefore = []

    if package == ID__TABLES__PACKAGE__tabularx:


        PCKG_NAME = '{tabularx}'

        if ID__TABLES__alignment__center in TABLE_SETTINGS['alignment']:
            lbefore.append(CMD__TABLE__TABULARX__CENTERING)
            colPrefix = 'Y'
        else:
            colPrefix = 'X'

        # the if-clause below was causing error with the illegal unit, therefore I commented it out
        # if (ID__TABLES__alignment__middle in TABLE_SETTINGS['alignment']):
            # lbefore.append('\\renewcommand\\tabularxcolumn[1]{m{#1}}')

        if not has_custom_widths:
            table_width = '|' + N_cols*(colPrefix+'|') 
        else:
            table_width = table_width_custom_0

        latex_before_table = lbefore + [
            '%\\begin{center}',
            '\\begin{table}[ht]',
            '\centering',
            '\caption{' + caption + '}',
            '\label{tab:' + label + '}',
            '\\begin'+PCKG_NAME+'{\\textwidth}{' + table_width + '}',
            '   \hline'
        ]

        latex_after_table = [
            '   \hline',
            '\end'+PCKG_NAME,
            '\end{table}'
        ]

        LATEX = latex_before_table + latex_table + latex_after_table

    elif package == ID__TABLES__PACKAGE__longtblr:

        PCKG_NAME = '{longtblr}'


        if not has_custom_widths:
            table_width = N_cols*'X'
        else:
            # table_width = table_width_custom_0
            raise NotImplementedError


        latex_before_table = [
            '%\\begin{center}',
            '\\begin{table}[ht]',
            '\centering',
            '\caption{' + caption + '}',
            '\label{tab:' + label + '}',
            '\\begin' + PCKG_NAME + '[',
            '\caption = {' + caption + '},',
            'entry = {},',
            'note{a} = {},',
            'note{$\dag$} = {}]',
            '   {colspec = {'+ table_width +'}, width = ' + str(TABLE_SETTINGS['rel-width']) + '\linewidth, hlines, rowhead = 2, rowfoot = 1}'
            ]  

        latex_after_table = [
            '\end' + PCKG_NAME,
            '\end{table}'
        ]

        add_hline_at_end = False # to be moved to user settings
        if add_hline_at_end:
            latex_after_table = '   \hline' + latex_after_table


        LATEX = latex_before_table + latex_table + latex_after_table


    elif package == ID__TABLES__PACKAGE__long_table:
        PCKG_NAME = '{longtable}'

        if not has_custom_widths:
            table_width = N_cols*'|p{3cm}' + '|'
        else:
            table_width = table_width_custom_0


        latex_before_table=[
        	'%\\begin{center}',
		    '\\begin{longtable}{' + table_width + '}',            
            '\caption{' + caption + '}',
            '\label{tab:' + label + '}\\\\',
			'\hline',
			''+latex_table[0],
			'\hline',
			'\endfirsthead % Use \endfirsthead for the line after the first header',
			'\hline',
			'\endfoot',
            ]

        latex_after_table = [
            '\end' + PCKG_NAME,
        ]

        LATEX = latex_before_table + ['    '+x for x in latex_table[1:]] + latex_after_table
        

        
    else:
        raise Exception('NOTHING CODED HERE!')
    
    # Unmask internal link with alias
    for i, s in enum(LATEX):
        LATEX[i] = s.replace(mask_alias, "|") 
    #
    
    return LATEX
