# Import packages
import re
import sys
import glob, os
import numpy as np
from os.path import exists
import subprocess
# For time profiling
from cProfile import Profile
from pstats import SortKey, Stats
#

# Add the src directory to the Python pathf
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))


from remove_markdown_comment import *
from symbol_replacements import *
from embedded_notes import *
from bullet_list__converter import *
from convert_code_blocks import *
from list_of_separate_lines import *
from equations import *
from path_searching import *
from get_parameters import *



# Global constants
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
ID__STYLE__STRIKEOUT        = 3

ID__DOCUMENT_CLASS__ARTICLE = 'article'
ID__DOCUMENT_CLASS__EXTARTICLE = 'extarticle'
ID__DOCUMENT_CLASS__CONFERENCE__IFAC = 'ifacconf'




PARS = get_parameters()

doc_classes__2_cols = ['ifacconf'] # document classes that use 2 columns


#                                         ['&',              '\&',                      1],

#

# REST OF CODE
new_table_version = False # had it as a user parameter, but it should always be fixed to False
def package_loader():

    packages_to_load    = []
    packages_to_load +=PARS['par']['packages-to-load']
    
    settings = PARS['⚙']
    
    tables_package      = settings['TABLES']['package']
    page_margin         = settings['margin']

    out = ['\\usepackage[table]{xcolor}']
    packages_to_load.append(['tabularx', None, ''])
    packages_to_load.append(['longtable', None, ''])
    packages_to_load.append(['tabularray', None, ''])
    
    doc_class = PARS['⚙']['document_class']['class']
    
    out += [f"{(pkg[1]==doc_class)*'%💀'}\\usepackage{{{pkg[0]}}}{(' % ' + pkg[2]) if len(pkg[2]) > 0 else ''}" for pkg in packages_to_load]

    out.append('\\usepackage{enumitem,amssymb}')
    out.append('\\newlist{todolist}{itemize}{2}')
    out.append('\setlist[todolist]{label=$\square$}')
    
    out.append('\\newtotcounter{citnum} %From the package documentation')
    out.append('\def\oldbibitem{} \let\oldbibitem=\\bibitem')
    out.append('\def\\bibitem{\stepcounter{citnum}\oldbibitem}')

    paragraph_indent = f"\\setlength{{\\parindent}}{{{str(settings['paragraph']['indent_length_of_first_line'])+'pt'}}}"
    out.append(paragraph_indent)
    
    if len(page_margin) > 0:
        out.append('\\usepackage[margin='+ page_margin + ']{geometry}')
 
    # out.append('\\usepackage[dvipsnames]{xcolor}') # creates bug
    out.append(settings['hyperlink_setup'])
        
    return out


def replace_hyperlinks(S):
    
    # Anything that isn't a square closing bracket
    name_regex = "[^]]+"
    # http:// or https:// followed by anything but a closing paren
    url_regex = "http[s]?://[^)]+"

    markup_regex = '\[({0})]\(\s*({1})\s*\)'.format(name_regex, url_regex)
    markup_regex_no_alias = r'(http[s]?://\S+)' # Non-greedy regex to match URLs, stopping at the first space or punctuation after the URL

    S_1 = []
    for s in S:
        s1 = s 
        matched_with_alias = False
        for match in re.findall(markup_regex, s1):
            markdown_link = '[' + match[0] + '](' + match[1] + ')'
            latex_link = "\\href{" + match[1] + "}{" + match[0] + "}"
            s1 = s1.replace(markdown_link, latex_link)
            matched_with_alias = True
        
        if not matched_with_alias:
            for match in re.findall(markup_regex_no_alias, s1):
                match = match.rstrip('.,)')  # Remove trailing punctuation like .,)
                markdown_link = match
                latex_link = "\\url{"+match+"}"
                s1 = s1.replace(markdown_link, latex_link)
                matched_with_alias = True

        S_1.append(s1)
    
    return S_1

def identify__tables(S):

    table_indexes = []
    table_has_started = False

    is_table_line_2 = False
    is_table_line = False

    new_table_version = False # had it as a user parameter, but it should always be fixed to False

    if not new_table_version:
        for i, l in enum(S):
            is_table_line = is_in_table_line(l)
            if is_table_line or is_table_line_2:
                idx__table_line = i
                if (not table_has_started):
                    table_has_started = True
                    idx__table_start = i
            # ⚠ NEVER add "or (i == len(S)-1)" to the condition below    
            elif (not is_table_line and table_has_started):
                table_has_started = False
                idx__table_end = i
                table_indexes.append(idx__table_start)
                table_indexes.append(idx__table_end)

    else:
        table_has_started = False
        table_line_idx = -1
        for i, l in enum(S):
            is_table_line_i = is_in_table_line(l)
            if is_table_line_i and not table_has_started: 
                table_has_started = True
                table_line_idx = i
                idx__table_start = i
            elif table_has_started:
                if not is_table_line_i:
                    if i+1<=len(S):
                        if not (is_in_table_line(S[i-1]) and is_in_table_line(S[i+1])):
                            idx__table_end = i
                            table_indexes.append(idx__table_start)
                            table_indexes.append(idx__table_end)
                            table_has_started = False  
                    else:
                        raise NotImplementedError


    return table_indexes



def simple_stylistic_replacements(S, type=None):


    '''
    For simple stylistic replacements. Includes conversions of:
    - Bold font
    - Highlighted font
    - Italic font
    - Strikeout (under dev.)
    
    '''

    if type == ID__STYLE__BOLD:
        style_char = '\*\*'
        replacement_func = lambda repl, string:  repl.append(['**'+string+'**', '\\textbf{' + string + '}'])
        l = 2
        is_pair = True
    
    elif type == ID__STYLE__HIGHLIGHTER:
        style_char = '\=\='
        replacement_func = lambda repl, string:  repl.append(['=='+string+'==', '\hl{' + string + '}'])
        l = 2
        is_pair = True

    elif type == ID__STYLE__ITALIC:
        style_char = '\*'
        replacement_func = lambda repl, string:  repl.append(['*'+string+'*', '\\textit{' + string + '}'])
        l = 1
        is_pair = True
    
    elif type == ID__STYLE__STRIKEOUT:
        style_char = '\~\~'
        replacement_func = lambda repl, string:  repl.append([f'~~{string}~~', f'\\st{{{string}}}'])
        l = 2
        is_pair = True



    else:
        raise NotImplementedError

    if is_pair:
        l_iter = 2
    else:
        raise NotImplementedError

    S1 = []
    for s in S:
        occurences = [x.start() for x in re.finditer(style_char, s)]
        L = len(occurences)

        if L % l == 0:
            replacements = []
            for i in range(int(L/l_iter)):
                o0 = occurences[2*i]
                o1 = occurences[2*i+1]
                replacement_func(replacements, s[o0+l:o1])
                
            for R in replacements:
                s = s.replace(R[0], R[1])
        else:
            raise Exception("You have added an odd number of the '" + style_char + "' character in the string: '" + s + "'")
        
        S1.append(s)
    
    return S1

 

def images_converter(images, PARAMETERS):

    '''
    DEPRECIATED
    Converts Images given the path of the image file
    '''

    # NOTES:
    # --- ", height=0.5\\textheight" addition causes the aspect ratio to break

    TO_PRINT = []
    for IM in images:
        path_img = '"' + IM[1].replace('\\', '/') + '"'
        label_img = IM[1].split('\\')[-1]
        caption_short = 'Caption short'
        caption_long = 'Caption long'
        figure_width = 0.7
        TO_PRINT.append(' \n'.join([
        '\\begin{figure}',
        '	\centering',
        f'	\includegraphics[width={figure_width}\linewidth]'+\
            '{"'+path_img+'"}',
        f'	\caption[{caption_short}]{{{caption_long}}}',
        '   \captionsetup{skip=-10pt} % Adjust the skip value as needed'*PARAMETERS['reduce spacing between figures'],
        '	\label{fig:'+label_img+'}',
        '\end{figure}']))

    return TO_PRINT

def get_reference_blocks(S):
    Lc = len(S)-1
    blocks = []
    for i in range(Lc+1):
        s = S[i].replace('\n', '')
        pattern = r"\^[\w\-]*$"
        link_label = re.findall(pattern, s)
        if len(link_label) > 0:
            blocks.append([i, link_label[0].replace('^', '')])    
        
    return blocks


PATHS = PARS['📁']

markdown_file = get_fields_from_Obsidian_note(PATHS['command_note'], ['convert_note:: '])[0][0]
PARS = get_parameters(version=markdown_file)



has_2_cols = (PARS['⚙']['document_class']['class'] in doc_classes__2_cols) or False

PARS['num_columns'] = int(has_2_cols*2 + (not has_2_cols)*1)

# open obsidian note

PATHS['markdown-file'] = get_embedded_reference_path(markdown_file.replace("[[", '').replace("]]", '')+'.md', PARS)
split_path=PATHS['markdown-file'].split('\\')
PATHS['tex-file'] = '\\'.join(split_path[:-1])+'\\'+split_path[-1].replace('.md', '') + '.tex'
PARS['📁']['tex-file'] = PATHS['tex-file']
with open(PATHS['markdown-file'], 'r', encoding='utf8') as f:
    content = f.readlines()

content = remove_markdown_comments(content)

# Convert bullet and numbered lists
content = bullet_list_converter(content)

[content, md_notes_embedded] = unfold_all_embedded_notes(content, PARS)

content = bullet_list_converter(content)

# Look for Appendix (in reverse order)
for i_l, line in enumerate(reversed(content)):
    if line.startswith('# Appendix'):
        # Calculate the correct index in the original list
        original_index = len(content) - 1 - i_l
        content[original_index] = content[original_index].replace('# Appendix', '\\appendix')
        break
#

# Replace headers and map sections \==================================================
Lc = len(content)-1
sections = []
for i in range(Lc+1):
    # ⚠ The sequence of replacements matters: 
    # ---- replace the lowest-level subsections first
    content_00 = content[i]

    content_0 = content[i]

    content[i] = re.sub(r'######## (.*)', r'\\paragraph{\1} \\hspace{0pt} \\\\', content[i].replace('%%', ''))
    content[i] = re.sub(r'######## (.*)', r'\\paragraph{\1} \\hspace{0pt} \\\\', content[i].replace('%%', ''))
    content[i] = re.sub(r'####### (.*)', r'\\paragraph{\1} \\hspace{0pt} \\\\', content[i].replace('%%', ''))
    content[i] = re.sub(r'###### (.*)', r'\\paragraph{\1} \\hspace{0pt} \\\\', content[i].replace('%%', ''))
    content[i] = re.sub(r'##### (.*)', r'\\paragraph{\1} \\hspace{0pt} \\\\', content[i].replace('%%', ''))
    content[i] = re.sub(r'#### (.*)', r'\\paragraph{\1} \\hspace{0pt} \\\\', content[i].replace('%%', ''))
    if content[i] != content_0:
        sections.append([i, content_0.replace('#### ', '').replace('\n', '')])

    content_0 = content[i]
    add_star = ''
    content[i] = re.sub(r'### (.*)', r'\\subsubsection{\1}', content[i].replace('%%', ''))
    if content[i] != content_0:
        sections.append([i, content_0.replace('### ', '').replace('\n', '')])

    content_0 = content[i]
    content[i] = re.sub(r'## (.*)', r'\\subsection{\1}', content[i].replace('%%', ''))
    if content[i] != content_0:
        sections.append([i, content_0.replace('## ', '').replace('\n', '')])

    content_0 = content[i]
    content[i] = re.sub(r'# (.*)', r'\\section{\1}', content[i].replace('%%', ''))
    if content[i] != content_0:
        sections.append([i, content_0.replace('# ', '').replace('\n', '')])

# \==================================================\==================================================

table_new_col_symbol = [['&',               '\&',                     1]]
content = symbol_replacement(content, table_new_col_symbol)

# find reference blocks \==================================================
#---1. they have to be at the end of the sentence (i.e. before "\n")
blocks = get_reference_blocks(content)
# \==================================================

# Find and apply internal links
internal_links = internal_links__identifier(content)
content = internal_links__enforcer(content, [sections, blocks], internal_links, PARS['⚙']['INTERNAL_LINKS'])
#

# Convert figures \==================================================

embeded_refs = embedded_references_recognizer(content, PARS['⚙']['EMBEDDED REFERENCES'], 'normal')

# ➕ add more image refs
# replace "content[line_number]" accordingly and see the result

for i, ln in enum(embeded_refs):

    line_number = ln[0]
    line_refs = ln[1]
    for lnrf in line_refs:

        converted_image_text = images_converter([[line_number, get_embedded_reference_path(lnrf[0], PARS)]], PARS['⚙']['figures'])
        
        for img_txt_cnv in converted_image_text:
            tmp1 = '![[' + lnrf[0]
            tmp2 = lnrf[2]

            reference_is_image_with_manual_resize = ('.png' in lnrf[0] or '.jpg' in lnrf[0]) and (tmp2.replace('|','')).isnumeric()
            content[line_number] = content[line_number].replace(tmp1 + tmp2*reference_is_image_with_manual_resize + ']]', img_txt_cnv)

# \==================================================
# content = add_new_line_equations(content)


md__equations_embedded_new = []
cleveref_allowed = [p for p in PARS['par']['packages-to-load'] if p[0]=='cleveref'][0][1] != PARS['⚙']['document_class']['class']
if PARS['⚙']['EMBEDDED REFERENCES']['treat_equation_blocks_separately']:
    # this means that all equation blocks were ignored, and we need to unfold them now
    [content, md__equations_embedded_new] = unfold_embedded_notes(content, [], PARS, mode='equation_blocks_only')

    # check for references in those equations, and convert to LateX system
    content = EQUATIONS__convert_equation_referencing(content, cleveref_allowed = cleveref_allowed)

content = convert_referencing(content, 'figures', cleveref_allowed = cleveref_allowed)
content = EQUATIONS__check_and_correct_aligned_equations(content)
content = convert_referencing(content, 'tables', cleveref_allowed = cleveref_allowed)

# Find sections and blocks again, since the content lines have been re-arranged
i0 = 0
for iS, sec in enumerate(sections):
    for i, s in enumerate(content[i0:]):
        tmp1 = sec[1]
        if ("section{" + tmp1 in s) or ("paragraph{" + tmp1 in s):            
            break        
    sections[iS][0] = i + i0
    i0 = i

blocks = get_reference_blocks(content)
#

# Find and apply internal links ---> repeat, in case of references within the unfolded notes``
content = internal_links__enforcer(content, [sections, blocks], internal_links__identifier(content), PARS['⚙']['INTERNAL_LINKS'])
#

if not PARS['⚙']['SEARCH_IN_FILE']['condition']:

    if PARS['EQUATIONS']['convert_non_numbered_to_numbered']:
        content = EQUATIONS__convert_non_numbered_to_numbered(content)
        # Problematic: C1 = content[2:3]

    IDX__TABLES = [0]
    TYPE_OF_CNV = [ID__CNV__IDENTICAL]
    tmp1 = identify__tables(content)
    tmp2 = [ID__CNV__TABLE_STARTED for _ in tmp1]
    tmp2[1::2] = [ID__CNV__IDENTICAL for _ in tmp1[1::2]]
    IDX__TABLES += tmp1
    TYPE_OF_CNV += tmp2

    Lc = len(content)-1
    if IDX__TABLES[-1] < Lc: 
        IDX__TABLES.append(Lc)
        TYPE_OF_CNV.append(ID__CNV__IDENTICAL)

    LATEX_TABLES = []

    if new_table_version: 
        step = 2
    else:
        step = 1
    
    table_new_col_symbol_reverse = [['\&',               '&',                     1]]
    

    for i in range(int(len(tmp1)/2)):
        raise Exception("You have tables outside the table note format! Please fix that!")
        new_table = symbol_replacement(convert__tables(content[tmp1[2*i]:tmp1[2*i+1]:step]), table_new_col_symbol_reverse)
        LATEX_TABLES.append(new_table)

    # for i, L in enum(content):

    #     for idx_table in IDX__TABLES:
    #         LATEX_TABLES.append(convert__tables(content[idx_table[0]:idx_table[1]]))
        
    cnd_choice_cmd_found = True
    while cnd_choice_cmd_found:
        content, cnd_choice_cmd_found = convert_inline_commands_with_choice(content, PARS)


    if PARS['⚙']['EMBEDDED REFERENCES']['convert_non_embedded_references']:        
        content = non_embedded_references_converter(content, PARS) 

    # Replace "#" with "" (temporary patch ➕)
    content = [x.replace("#", "") for x in content]

    LATEX = []
    i0 = IDX__TABLES[0]
    i_tables = 0
    for j, i in enum(IDX__TABLES[1:]):
        if TYPE_OF_CNV[j] == ID__CNV__IDENTICAL:
            LATEX += content[i0:i]
        elif TYPE_OF_CNV[j] == ID__CNV__TABLE_STARTED:
            LATEX += LATEX_TABLES[i_tables]
            i_tables += 1
        
        i0 = i


    LATEX = symbol_replacement(LATEX, PARS['par']['symbols-to-replace'])
    styles_replacement = [ID__STYLE__BOLD, ID__STYLE__HIGHLIGHTER, ID__STYLE__ITALIC]#, ID__STYLE__STRIKEOUT]
    
    for style in styles_replacement:
        LATEX = simple_stylistic_replacements(LATEX, type=style)
    

    LATEX = code_block_converter(LATEX, PARS)
    LATEX = symbol_replacement(LATEX, [['\#&', '&', 1]])


    # Replace "%" with "\%" (after having replaced obsidian comments of course)
    # LATEX = [x.replace("%", "\%") for x in LATEX]

    LATEX = replace_hyperlinks(LATEX)


    # get text before section, so that it is added after the title, before the table of contents
    text_before_first_section = ''

    for i, s in enum(content):
        if s.startswith('\\section'):
            line_first_section = i
            break

    paragraph = PARS['⚙']['paragraph']
    if paragraph['if_text_before_first_section___place_before_table_of_contents']:
        # BUG2: anything that needs special conversion will not be converted!!
        if len(sections)>0:
            text_before_first_section = '\n\n'.join([s for s in content[:line_first_section] if len(s)>0])
            content = content[line_first_section:]

    #

    # LATEX = symbol_replacement(LATEX, [['_', '\_', 1]]) # DON'T UNCOMMENT!
    # title = PARS['⚙']['title'] if PARS['⚙']['title'] else symbol_replacement(path_file.split('\\')[-1].replace('_', '\_'), PARS['par']['symbols-to-replace'])[0]
    title = PARS['⚙']['title'] if PARS['⚙']['title'] else ''
    LATEX = symbol_replacement(LATEX, [[paragraph['insert_new_line_symbol'] , '\\clearpage', 1]])

    LATEX = convert_inline_code(LATEX)
    
    document_class = PARS['⚙']['document_class']


    doc_class_fontsize = f'[{document_class["fontsize"]}]' if len(document_class['fontsize'])>0 else ''

    is_ifac = document_class['class'] == 'ifacconf'
    
    PREAMBLE = [f"\\documentclass{doc_class_fontsize}{{{document_class['class']}}}"] +\
            [is_ifac*'\\newcounter{part} % fix the issue in the class'] +\
            [is_ifac*'\counterwithin*{section}{part}'] +\
            ['% Loading packages that were defined in `src\get_parameters.py`'] +\
            package_loader() +\
            ['\n'] + ['\sethlcolor{yellow}'] + ['\n'] + ['\n'*2] +\
            ['\setcounter{secnumdepth}{4}'] +\
            ['\setlength{\parskip}{7pt} % paragraph spacing'] +\
            ['\let\oldmarginpar\marginpar'] +\
            ['\\renewcommand\marginpar[1]{\oldmarginpar{\\tiny #1}} % Change "small" to your desired font size]'] + ['\n'*2] +\
            ['\\newcommand{\ignore}[1]{}']+\
            ['\n'*3] + ['\\begin{document}']+\
            ['\\allowdisplaybreaks' if paragraph['allowdisplaybreaks'] else '']+\
            ['\date{}'*PARS['⚙']['use_date']]+\
            [f"\\author{{{PARS['⚙']['author']}}}"*(len(PARS['⚙']['author'])>0)]+\
            [f'\\title{title}\n\maketitle'*(len(title)>0)]+\
            [text_before_first_section]+\
            ['\\tableofcontents \n \\newpage'*paragraph['add_table_of_contents']]

    # LATEX = symbol_replacement(LATEX, [['_', '\_', 0]])
    LATEX1 = []
    for line in LATEX:
        LATEX1.append(escape_underscores_in_texttt(line))

    LATEX = PREAMBLE + LATEX1 + ['\\newpage \n '*paragraph['add_new_page_before_bibliography'] + '\n'*5 + '\\bibliographystyle{apacite}']+\
        ['\\bibliography{' + PATHS['bibtex_file_name'] + '}'] + ['\end{document}']

    if '[[✍⌛writing--FaultDiag--Drillstring--MAIN]]' in markdown_file:
        LATEX_1 = []
        for l in LATEX:
            LATEX_1.append(l.replace('C:/Users/mariosg/OneDrive - NTNU/FILES/workTips/Analyses/PINNs+MTL/FaultDiag/FaultDiag/simulation results/plots/', ''))
            
        LATEX = LATEX_1
        


    with open(PATHS['tex-file'], 'w', encoding='utf8') as f:
        for l in LATEX:
            if not l.endswith('\n'): l+='\n'
            f.write(l)


    # Print Messages
    print__what_was_converted = 'Converted note: ' + PATHS['markdown-file'] + ' into ' + PATHS['tex-file']

    MESSAGES_TO_PRINT = [print__what_was_converted]

    [print(msg) for msg in MESSAGES_TO_PRINT]
    clickable_files = f'[📁tex file](<file:///{PARS["📁"]["tex-file"]}>), [📁.pdf file](<file:///{PARS["📁"]["tex-file"].replace(".tex", "")}.pdf>)'
    replace_fields_in_Obsidian_note(PATHS['command_note'], ['files:: '], [clickable_files])

        
    # # Run the bash script (somehow it is not working from python for now 🤔)
    # try:
    #     result = subprocess.run(PATHS['bash_script'], shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #     print("Output:", result.stdout.decode())
    #     print("Errors:", result.stderr.decode())
    # except subprocess.CalledProcessError as e:
    #     print("Error:", e.stderr.decode())


else:
    
    text_to_seach = PARS['⚙']['SEARCH_IN_FILE']['text_to_seach']
    replace_with = PARS['⚙']['SEARCH_IN_FILE']['replace_with']
    
    ALL_EMBEDDED_NOTES = md__equations_embedded_new + md_notes_embedded
    MATCHES = []
    for note in ALL_EMBEDDED_NOTES:
        note_path = get_embedded_reference_path(note, PARS, search_in = 'vault')
        with open(note_path, 'r', encoding='utf8') as file: content_i = '\n'.join(file.readlines())
        has_the_search_text = text_to_seach in content_i
        if has_the_search_text: 
            MATCHES.append(note_path)

        
    if replace_with:
        for note in MATCHES:
            with open(note, 'r', encoding='utf8') as file:
                content_i = ''.join(file.readlines())
                content_i = content_i.replace(text_to_seach, replace_with)
            
            with open(note, 'w', encoding='utf8') as file:
                file.write(content_i)    


    print("Finished Searching")
#
