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

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))


from remove_markdown_comment import *
from symbol_replacements import *
from embedded_notes import *
from bullet_list__converter import *
from convert_code_blocks import *
from list_of_separate_lines import *
from equations import *
from path_searching import *



# Helper functions
def conv_dict(D):
    for key, value in D.items():
        if value == '🟢':
            D[key] = True
        elif value == '🔴':
            D[key] = False
        elif isinstance(value, dict):
            D[key] = conv_dict(value)
    return D

def python_format_path(path, to_python = False):
    
    if not to_python:
        return path.replace('\\\\', '\\')
    else:
        return path.replace('\\', '\\\\')


# is_in_table_line = lambda x: x.startswith('|') and x.endswith('|')
# enum             = lambda x: enumerate(x)
#

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


# ⚠ does not work for longtblr!
CMD__TABLE__TABULARX__CENTERING = '\\newcolumntype{Y}{>{\\centering\\arraybackslash}X}'
#

# USER PARAMETERS
path_vault          = 'C:\\Users\\mariosg\OneDrive - NTNU\FILES\\workTips\\'
# path_vault          = 'C:\\Users\\mariosg\OneDrive - NTNU\FILES\\workTips\\' + 'Literature\\Straightforward-Obsidian2Latex\\example_vault\\'
path0               = path_vault + 'AUTOMATIONS\\'
path_file_testing   = path_vault + 'code testing\\test_2'
path_equation_blocks = path_vault + '✍Writing\\equation blocks'
path_list_note_paths = path_vault + 'DO_NOT_DELETE__note_paths.txt'
path_BIBTEX          = path_vault + '✍Writing\\BIBTEX'

path_file = 'who cares'

hyperlinkSetup="""
\hypersetup{
colorlinks   = true,    % Colours links instead of ugly boxes
urlcolor     = blue,    % Colour for external hyperlinks
linkcolor    = blue,    % Colour of internal links
citecolor    = blue      % Colour of citations
}
"""


SEARCH_IN_FILE = False
text_to_seach = 'w_{E_{2}}'
replace_with = '\\beta_{2}' 

PARS = conv_dict({
    '⚙': # SETTINGS
        {'TABLES':{
                            'package': ID__TABLES__PACKAGE__tabularx,
                'hlines-to-all-rows': '🟢',
                 'any-hlines-at-all': '🟢',
                         'alignment':  [ID__TABLES__alignment__center,
                                        ID__TABLES__alignment__middle],
                        'rel-width': 1.2,
                },
        'margin': '0.9in',
        'EXCEPTIONS': 
                    {'raise_exception__when__embedded_reference_not_found': '🔴'},
        'INTERNAL_LINKS': 
                        {'add_section_number_after_referencing': '🟢'  # if True, then we have "\hyperref[sBootstrapping-and-the-iterative-logic-in-estimation]{here}: \autoref{sBootstrapping-and-the-iterative-logic-in-estimation}". 
                        },        
        'EMBEDDED REFERENCES':  
                        {'convert_non_embedded_references': '🟢',  # if True, then references such as "[[another note]]" will be changed to "another note". If FAlse, they will remain as is
                         'treat_equation_blocks_separately': '🟢', # if True, then the equation blocks are treated separately, in order to increase speed
                                          'treat_citations': '🟢',
                                 'adapt_section_hierarchy': '🟢', # if True, then whenever there are sections in an embedded reference, their hierarchy will change, based on whether the embedded note was already in sections (so we don't break the hierarchy)
                'write_obsidian_ref_name_on_latex_comment': '🟢'}, 
        'figures': 
                        {'reduce spacing between figures': '🔴',
                                  'put_figure_below_text': '🟢',
                                           'include_path': '🟢'}, # not including the path works only if all the figures are in the same folder (appropriate for Overleaf projects)
                                                       
        'paragraph':{
                    'indent_length_of_first_line': 0,    # 0 if no indent is desired. Recommended 20 for usual indent
                    'if_text_before_first_section___place_before_table_of_contents': '🔴',
                    'insert_new_line_symbol': '---' 
        }, 
        'author': 'Marios Gkionis',
        'hyperlink_setup': hyperlinkSetup,
        'code_blocks': {
                        'admonition':  [
                                        ['default', ['white', 'black']],
                                        ['warning', ['red', 'white']],
                                        ['quote',   ['gray', 'black']]
                                       ]
            },
        'formatting_rules':{
                    'non_embedded_references': { # find list of colors here: https://www.overleaf.com/learn/latex/Using_colors_in_LaTeX
                                                'notes_with_tags': [ # add tag, color ("\textcolor{}{}" function)
                                                                    ["#Latex/Formatting/method",         "teal"],
                                                                    ["#Latex/Formatting/characteristic", "gray"],
                                                                    ["#Latex/Formatting/task",           "red"],
                                                                    ['#Latex/Formatting/math-term',      "brown"]
                                                                    ]}
        }},
    '📁': # Paths
           {
                 'command_note': path_vault+'✍Writing\\👨‍💻convert_to_latex.md',
                'markdown-file': path_file+'.md',  # Markdown (.md) file for conversion
                     'tex-file': path_file+'.tex',  # LateX (.tex) file (converted from the .md file)  
                        'vault': path_vault,
              'equation_blocks': path_equation_blocks,
             'list_paths_notes': path_list_note_paths, # saves time from searching of the note's path
                  'bash_script': path_vault + '✍Writing\\compile_and_open.sh',
             'bibtex_file_name': 'BIBTEX'           # your bibtex file name 
            },
    'par':
        {
            'tabular-package':
                            {
                                       'names': ['longtblr', 'tabularx'],
                                'before-lines': ['{colspec}']
                            },
            'packages-to-load':[ # preamble packages,# comment       
                                ['hyperref',          ''],
                                ['graphicx',          ''],
                                ['subcaption',        'for subfigures'],
                                ['amssymb',           'need more symbols'],
                                ['titlesec',           "so that we can add more subsections (using 'paragraph')"],
                                ['xcolor, soul',        'for the highlighter'],
                                ['amsmath',              ''],
                                ['amsfonts',              ''],
                                ['cancel',                ''],
                                ['minted',                 ''],
                                ['apacite',           'apa citation style'],
                                ['caption',           'to set smaller vertical spacing between two figures'],
                                ['cleveref',             ''],
                                ['tcolorbox',            ''],
                                ['float',             'to make the figures stay between the text at which they are defined'],
                                ['pdfpages',             ''],
                                ['totcount',             ''],
                                ['lipsum',               ''],
                                ['natbib',            "Such that we avoid the error (`Illegal parameter number in definition of \\reserved@a`) of not being able to add citations in captions"]
                                ],
          'symbols-to-replace': [       # Obsidian symbol, latex symbol,            type of replacement (1 or 2)
                                        ['✔',              '\\checkmark',            1],
                                        ['🟢',              '$\\\\blacklozenge$',    2],
                                        ['🔴',              '\\\maltese',            2],
                                        ['➕',              '**TODO: **',            2],    # Alternatives: ['$\\\\boxplus$']
                                        ['🔗',              'LINK',                  1],
                                        ['\implies',        '\Rightarrow',            1],
                                        ['❓❓',              '?',                     1],
                                        ['❓',              '?',                      1],
                                        ['❌',              'NO',                    1],
                                        ['🤔',               '',                     1],
                                        ['⚠',               '!!',                    1],
                                        ['📚',              '',                      1],
                                        ['⌛',               '',                     1],
                                        ['🔭',              '',                     1],
                                        ['👆',              '',                      1],
                                        ['💭',              '',                      1]
                                        ]
        },
        #                                        ['\\text',          '\\textnormal',          1],

    'EQUATIONS':
               {'convert_non_numbered_to_numbered': '🟢'} # If True, all equations are numbered

})

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
    packages_to_load.append(['tabularx', ''])
    packages_to_load.append(['longtable', ''])
    packages_to_load.append(['tabularray', ''])
    
    out += ['\\usepackage{'+pkg[0]+'}' + (' % ' + pkg[1])*(len(pkg[1])>0) for pkg in packages_to_load]

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
                latex_link = "\\href{"+match+"}"
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
            raise Exception("error for this case, for now")
        
        S1.append(s)
    
    return S1

 

def images_converter(images, PARAMETERS):

    '''
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
        '	\includegraphics[width=' + str(figure_width) + '\linewidth]'+\
            '{"'+path_img+'"}',
        '	\caption['+caption_short+']{'+caption_long+'}',
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

markdown_file = get_fields_from_Obsidian_note(PATHS['command_note'], ['convert_note:: '])[0]
# open obsidian note

PATHS['markdown-file'] = get_embedded_reference_path(markdown_file.replace("[[", '').replace("]]", '')+'.md', PARS)
split_path=PATHS['markdown-file'].split('\\')
PATHS['tex-file'] = '\\'.join(split_path[:-1])+'\\'+split_path[-1].replace('.md', '') + '.tex'
with open(PATHS['markdown-file'], 'r', encoding='utf8') as f:
    content = f.readlines()

content = remove_markdown_comments(content)

[content, md_notes_embedded] = unfold_all_embedded_notes(content, PARS)

# Convert bullet and numbered lists
content = bullet_list_converter(content)


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
if PARS['⚙']['EMBEDDED REFERENCES']['treat_equation_blocks_separately']:
    # this means that all equation blocks were ignored, and we need to unfold them now
    [content, md__equations_embedded_new] = unfold_embedded_notes(content, [], PARS, mode='equation_blocks_only')

    # check for references in those equations, and convert to LateX system
    content = EQUATIONS__convert_equation_referencing(content)

content = convert_referencing(content, 'figures')
content = EQUATIONS__check_and_correct_aligned_equations(content)
content = convert_referencing(content, 'tables')

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

if not SEARCH_IN_FILE:

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
    LATEX = simple_stylistic_replacements(LATEX, type=ID__STYLE__BOLD)
    LATEX = simple_stylistic_replacements(LATEX, type=ID__STYLE__HIGHLIGHTER)
    LATEX = simple_stylistic_replacements(LATEX, type=ID__STYLE__ITALIC)

    LATEX = code_block_converter(LATEX, PARS)

    # Replace "%" with "\%" (after having replaced obsidian comments of course)
    # LATEX = [x.replace("%", "\%") for x in LATEX]

    LATEX = replace_hyperlinks(LATEX)


    # get text before section, so that it is added after the title, before the table of contents
    text_before_first_section = ''

    for i, s in enum(content):
        if s.startswith('\\section'):
            line_first_section = i
            break

    if PARS['⚙']['paragraph']['if_text_before_first_section___place_before_table_of_contents']:
        # BUG2: anything that needs special conversion will not be converted!!
        if len(sections)>0:
            text_before_first_section = '\n\n'.join([s for s in content[:line_first_section] if len(s)>0])
            content = content[line_first_section:]

    #

    title = symbol_replacement(path_file.split('\\')[-1].replace('_', '\_'), PARS['par']['symbols-to-replace'])[0]
    
    LATEX = symbol_replacement(LATEX, [[PARS['⚙']['paragraph']['insert_new_line_symbol'] , '\\newpage', 1]])

    LATEX = convert_inline_code(LATEX)

    PREAMBLE = ['\documentclass{article}'] +\
            package_loader() +\
            ['\n'] + ['\sethlcolor{yellow}'] + ['\n'] + ['\n'*2] +\
            ['\setcounter{secnumdepth}{4}'] +\
            ['\setlength{\parskip}{7pt} % paragraph spacing'] +\
            ['\let\oldmarginpar\marginpar'] +\
            ['\\renewcommand\marginpar[1]{\oldmarginpar{\\tiny #1}} % Change "small" to your desired font size]'] +\
            ['\\begin{document}']+\
            ['\date{}']+\
            ['\\author{' + PARS['⚙']['author'] + '}']+\
            ['\\title{'+ title +'}\n\maketitle'	]+\
            [text_before_first_section]+\
            ['\\tableofcontents \n \\newpage']

    LATEX = PREAMBLE + LATEX + ['\\newpage \n \\bibliographystyle{apacite}']+\
        ['\\bibliography{' + PATHS['bibtex_file_name'] + '}'] + ['\end{document}']

    with open(PATHS['tex-file'], 'w', encoding='utf8') as f:
        for l in LATEX:
            if not l.endswith('\n'): l+='\n'
            f.write(l)


    # Print Messages
    print__what_was_converted = 'Converted note: ' + PATHS['markdown-file'] + ' into ' + PATHS['tex-file']

    MESSAGES_TO_PRINT = [print__what_was_converted]

    [print(msg) for msg in MESSAGES_TO_PRINT]
        
    # # Run the bash script (somehow it is not working from python for now 🤔)
    # try:
    #     result = subprocess.run(PATHS['bash_script'], shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #     print("Output:", result.stdout.decode())
    #     print("Errors:", result.stderr.decode())
    # except subprocess.CalledProcessError as e:
    #     print("Error:", e.stderr.decode())


else:
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
