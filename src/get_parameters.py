import os

def get_parameters(version = 'default'):
    
    '''
    Get the parameters for the file conversion
    '''
    
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

    # ⚠ does not work for longtblr!
    CMD__TABLE__TABULARX__CENTERING = '\\newcolumntype{Y}{>{\\centering\\arraybackslash}X}'
    #


    # USER PARAMETERS
    path_vault          = 'C:\\Users\\mariosg\\OneDrive - NTNU\\FILES\\workTips\\' 
    #'G:\\My Drive\\MARIOS_LOG\\', 
    # 'C:\\Users\\mariosg\\OneDrive - NTNU\\FILES\\workTips\\'
    path_writing        = path_vault + '✍Writing\\'
    path_templates        = path_vault + '👨‍💻Automations\\'
    path_table_block_template = path_templates + 'table_block.md'
    path_equation_block_template = path_templates + 'equation_block_single.md'

    path_equation_blocks = path_writing + 'equation blocks'
    path_table_blocks   = path_writing + 'table blocks'
    path_list_note_paths = path_vault + 'DO_NOT_DELETE__note_paths.txt'
    path_BIBTEX          = path_writing + 'BIBTEX'
    
    if not os.path.exists(path_list_note_paths):
        with open(path_list_note_paths, 'w', encoding='utf-8') as file:
            file.write('')
    
    for path in [path_writing, path_equation_blocks, path_table_blocks, path_templates]:
        if not os.path.exists(path):
            os.makedirs(path)
            
    if not os.path.exists(path_table_block_template):
        with open(path_table_block_template, 'w', encoding='utf-8') as file:
            file.write(table_block_text())
        
    if not os.path.exists(path_equation_block_template):
        with open(path_equation_block_template, 'w', encoding='utf-8') as file:
            file.write(equation_block_text())
            
    path_plugins = path_vault + '.obsidian\\plugins\\'
    path_quick_add = path_plugins+'quickadd\\'

    # if not os.path.exists(path_quick_add):
    #     shutil.copytree('\\'.join(os.path.abspath(__file__).split('\\')[0:-2]) + '\\obsidian\\.obsidian\\plugins\\quickadd', path_plugins)
    # else:
    #     raise Exception('Not implemented yet.')
                
    hyperlinkSetup="""
    \hypersetup{
    colorlinks   = true,    % Colours links instead of ugly boxes
    urlcolor     = blue,    % Colour for external hyperlinks
    linkcolor    = blue,    % Colour of internal links
    citecolor    = blue      % Colour of citations
    }
    """
    
    
    # apply parameter changes based on specific notes
        
    V__document_class = {'class': ID__DOCUMENT_CLASS__EXTARTICLE, 'fontsize': ''}
    V__author = 'Marios Gkionis'
        
    if version =='[[👆👆RL--writing--1]]':
        
        V__document_class = {'class': ID__DOCUMENT_CLASS__EXTARTICLE, 'fontsize': '9pt'}
        V__author = ''
        
    elif version =='[[✍⌛writing--FaultDiag--Drillstring--MAIN]]':
        
        V__document_class = {'class': ID__DOCUMENT_CLASS__CONFERENCE__IFAC, 'fontsize': ''}
        V__author = ''
         
    elif version =='[[✍⌛writing--THESIS--high-level-structure]]':
    # \documentclass[a4paper, 12pt, openany]{book} %chose the paper size and font size. Openany ensures that all all chapters and similar may begin at any page, not only odd pages. For the introductory pages and appendices we want openany, but for chapter pages in the main content we want chapters to begin only on odd pages (right hand side). The book class ensures that the margins are automatically adjusted such that left hand pages are slightly moved to the left and vice versa at the right, which makes the thesis very readable and good looking when printed in bound book format.
        V__document_class = {'class': '\documentclass[a4paper, 12pt, openany]{book}', 'fontsize': '12pt'}
        V__author = 'Marios Gkionis'

        
    #     #\documentclass[a4paper, 12pt, openany]{book}
    PARS = conv_dict({
        '⚙': # SETTINGS 
            {'SEARCH_IN_FILE': {'condition':'🔴', 'text_to_seach': 'w_{E_{2}}','replace_with': '\\beta_{2}'},
             'document_class': V__document_class,
            'TABLES':{
                                'package': ID__TABLES__PACKAGE__tabularx,
                    'hlines-to-all-rows': '🟢',
                    'any-hlines-at-all': '🟢',
                            'alignment':  [ID__TABLES__alignment__center,
                                            ID__TABLES__alignment__middle],
                            'rel-width': 1.2,
                            'place_table_where_it_is_written': '🟢',
                            'include_list_of_tables': '🟢',
                    },
            'margin': '0.9in',
            'use_date': '🔴',
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
                    'write_obsidian_ref_name_on_latex_comment': '🟢',
                    'special_cases': {
                                    'inlink_dataviewjs': {
                                                'condition': '🔴',  # ➕TODO: this has the issue that the embedded refs might also have the same code within them! Need to specify levels perhaps
                                                'protocol_names': ['#👨‍💻/dataviewjs/mentions/1'],
                                            }
                                    }
                    }, 
            'figures': 
                            {'reduce spacing between figures': '🔴',
                                      'put_figure_below_text': '🟢',
                                               'include_path': '🟢', # not including the path works only if all the figures are in the same folder (appropriate for Overleaf projects)
                        'use_overleaf_all_in_the_same_folder': '🔴',
                                    'include_list_of_figures': '🟢',}, 
                                                        
            'paragraph':{
                        'indent_length_of_first_line': 0,    # 0 if no indent is desired. Recommended 20 for usual indent
                        'if_text_before_first_section___place_before_table_of_contents': '🔴',
                        'insert_new_line_symbol':                                        '---',
                        'add_table_of_contents':                                        '🟢',
                        'add_new_page_before_bibliography':                             '🟢',
                        'allowdisplaybreaks':                                           '🔴',
            }, 
            'author': V__author,
            'title': '',
            'hyperlink_setup': hyperlinkSetup,
            'code_blocks': {
                            'admonition':  [
                                            ['default', ['white', 'black']],
                                            ['warning', ['red', 'white']],
                                            ['quote',   ['gray', 'black']],
                                            ['todo',    ['yellow', 'red']]
                                        ]
                },
            'formatting_rules':{  # find list of colors here: https://www.overleaf.com/learn/latex/Using_colors_in_LaTeX
                        'non_embedded_references': {'use': '🔴', # using it results in highly increased time, since the algorithm has to search inside all non embedded notes.
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
                           'vault': path_vault,
                 'equation_blocks': path_equation_blocks,
                'list_paths_notes': path_list_note_paths, # saves time from searching of the note's path
                     'bash_script': path_vault + '✍Writing\\compile_and_open.sh',
                'bibtex_file_name': 'BIBTEX',           # your bibtex file name 
            'custom_latex_commands': path_vault + '✍Writing\\custom_latex_functions.tex',
                },
        'par':
            {
                'tabular-package':
                                {
                                        'names': ['longtblr', 'tabularx'],
                                    'before-lines': ['{colspec}']
                                },
                'packages-to-load':[ # preamble packages, #exclude for doc_class  # comment (placed inside the latex file, next to the package loading)      
                                    ['hyperref',    None,                                    ''],
                                    ['graphicx',    None,                                    ''],
                                    ['subcaption',  None,                                    'for subfigures'],
                                    ['amssymb',     None,                                    'need more symbols'],
                                    ['titlesec',    ID__DOCUMENT_CLASS__CONFERENCE__IFAC,    "so that we can add more subsections (using 'paragraph')"],
                                    ['xcolor, soul',None,                                   'for the highlighter'],
                                    ['amsmath',     None,                                    ''],
                                    ['amsfonts',    None,                                    ''],
                                    ['cancel',      None,                                    ''],
                                    ['minted',      None,                                    ''],
                                    ['apacite',     None,                                    'apa citation style'],
                                    ['caption',     None,                                    'to set smaller vertical spacing between two figures'],
                                    ['cleveref',    None,                                    'for clever references'],
                                    ['tcolorbox',   None,                                    ''],
                                    ['float',       None,                                    'to make the figures stay between the text at which they are defined'],
                                    ['pdfpages',    None,                                     ''],
                                    ['totcount',    None,                                     ''],
                                    ['lipsum',      None,                                     ''],
                                    ['ragged2e',    None,                                     'can wrap text for tables in the tabularx environment'],
                                    ['natbib',      None,                                     "Such that we avoid the error (`Illegal parameter number in definition of \\reserved@a`) of not being able to add citations in captions"],
                                    ['pdfcomment',  None,                                     'for popup comments in the .pdf'],
                                    ['booktabs',    None,                                      'so that the toprule command works'],
                                    ['soul',        None,                                      'to strikeout text using \\st{}'],
									['twemojis',	None,										'for twemojis'],			
                                    ['rotating',    None,                                       'for rotating text on tables'],
                                    ['algorithm',   None,                                       ''],
                                    ['algpseudocode',None,                                      ''],
                                    ['array',       None,                                       ''],
                                    ['mdframed',    None,                                       'for framed boxes'],
					
                                    ],
            'symbols-to-replace': [       # Obsidian symbol, latex symbol,            type of replacement (1 or 2)
											['−',              '-',            1],
                                            ['✔',              '\\twemoji{check mark}',            1],
											['🟢',              '\\twemoji{green circle}',    1],
                                            ['⚫',              '\\twemoji{black circle}',    1],
											['🔴',              '\\twemoji{red circle}',            1],
                                            ['🟡',              '\\twemoji{yellow circle}',            1],
                                            ['🙄',              '\\twemoji{face with rolling eyes}',            1]        ,
                                            ['🙁',              '\\twemoji{disappointed face}',            1],
											['➕',              '\\twemoji{plus}',            1],    # Alternatives: ['$\\\\boxplus$']
											['🔗',              'LINK',                  1],
                                            ['😯',              '\\twemoji{face with open mouth}', 1],
											['\implies',        '\Rightarrow',            1],
											['❓❓',              '?',                     1],
                                            ['⁉️', '\\twemoji{exclamation question mark}',                     1],
											['❓',              '',                      1],
											['❌',              'NO',                    1],
											['🤔',               '\\twemoji{thinking face}',                     1],
                                            ['🥱',               '\\twemoji{yawning face}',                     1],
                                            ['😏',              '\\twemoji{smirking face}',                     1],
											['⚠',               '\\twemoji{warning}',                    1],
											['📚',              '\\twemoji{books}',                      1],
											['📜',              '\\twemoji{page with curl}',                      1],
											['🔭',              '\\twemoji{telescope}',                     1],
											['👆',              '\\twemoji{index pointing up}',                      1],
                                            ['☝️',             '\\twemoji{index pointing up}',                      1],
                                            ['👉',              '\\twemoji{backhand index pointing right}',                      1],
											['💭',              '\\twemoji{thought balloon}',                      1],
											['🔧',              '\\twemoji{screwdriver}', 1],
           									['⛏',				 '\\twemoji{pick}',        1],
                                            ['🧪',                  '\\twemoji{test tube}',           1],
                                            ['⭐',                  '\\twemoji{star}',           1],
                                            ['💡',                  '\\twemoji{light bulb}',           1],
											['📅',                  '\\twemoji{date}',           1],
                                            ['📍',                '\\twemoji{round pushpin}',           1],
                                            ['📜',                  '\\twemoji{scroll}',          1],
                                            ['👎',                  '\\twemoji{thumbs down}',          1],
                                            ['🪞',                    'w',                          1],
                                            ['👤',                  '\\twemoji{bust in silhouette}',           1],
                                            ['👥',                  '\\twemoji{busts in silhouette}',           1],
                                            ['🗣️',                  '\\twemoji{busts in silhouette}',           1],
                                            ['🏫',                  '\\twemoji{school}',           1],
                                            ['⚕️',                  '\\twemoji{medical symbol}',           1],
											['⚪',					'\\twemoji{white circle}',		1]
                                            ]
            },
            #                                        ['\\text',          '\\textnormal',          1],

        'EQUATIONS':
                {'convert_non_numbered_to_numbered': '🟢'} # If True, all equations are numbered
    })
       

    return PARS



def equation_block_text():
    text = """
# %%expr%%
    """
    return text

def table_block_text():
    text = """
%%
caption:: 
widths:: 
package:: #Latex/Table/package/  
use_hlines:: 
use_vlines:: 

If the table is a dataview table:
datav__file_column_name:: 

%%
# %%table%%
📣*`=this.caption`*
    """
    
    return text
    
    
def quick_add_table_block_text():
    templatePath = "👨‍💻Automations/table_block"
    destinationPath = "✍Writing/table_blocks"
    
    text = f"""
    {{
      "id": "d8dcaf45-4e62-4860-ba69-42671bac884c",
      "name": "table_block",
      "type": "Template",
      "command": true,
      "templatePath": "{templatePath}",   # ✅ Add quotes
      "fileNameFormat": {{
        "enabled": true,
        "format": "table__block_"
      }},
      "folder": {{
        "enabled": true,
        "folders": [
          "{destinationPath}"   # ✅ Add quotes
        ],
        "chooseWhenCreatingNote": false,
        "createInSameFolderAsActiveFile": false,
        "chooseFromSubfolders": false
      }},
      "appendLink": true,
      "openFileInNewTab": {{
        "enabled": true,
        "direction": "vertical",
        "focus": true
      }},
      "openFile": true,
      "openFileInMode": "default",
      "fileExistsMode": "Increment the file name",
      "setFileExistsBehavior": true
    }}
    """  

    return text
