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

    ID__DOCUMENT_CLASS__ARTICLE = 'article'
    ID__DOCUMENT_CLASS__EXTARTICLE = 'extarticle'
    ID__DOCUMENT_CLASS__CONFERENCE__IFAC = 'ifacconf'

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
    
    
    # apply parameter changes based on specific notes
    if version == 'default':
        
        V__document_class = {'class': ID__DOCUMENT_CLASS__EXTARTICLE, 'fontsize': ''}
        V__author = 'Marios Gkionis'
        
    elif version =='[[👆👆RL--writing--1]]':
        
        V__document_class = {'class': ID__DOCUMENT_CLASS__EXTARTICLE, 'fontsize': '9pt'}
        V__author = ''
        
    elif version =='[[✍⌛writing--FaultDiag--Drillstring--MAIN]]':
        
        V__document_class = {'class': ID__DOCUMENT_CLASS__CONFERENCE__IFAC, 'fontsize': ''}
        V__author = ''
         
    
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
                    },
            'margin': '',
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
                    'write_obsidian_ref_name_on_latex_comment': '🟢'}, 
            'figures': 
                            {'reduce spacing between figures': '🔴',
                                      'put_figure_below_text': '🟢',
                                               'include_path': '🟢'}, # not including the path works only if all the figures are in the same folder (appropriate for Overleaf projects)
                                                        
            'paragraph':{
                        'indent_length_of_first_line': 0,    # 0 if no indent is desired. Recommended 20 for usual indent
                        'if_text_before_first_section___place_before_table_of_contents': '🔴',
                        'insert_new_line_symbol':                                        '---',
                        'add_table_of_contents':                                        '🔴',
                        'add_new_page_before_bibliography':                             '🔴' 
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
                'packages-to-load':[ # preamble packages, #exclude for doc_class  # comment (placed inside the latex file, next to the package loading)      
                                    ['hyperref',    None,                                    ''],
                                    ['graphicx',    None,                                    ''],
                                    ['subcaption',  None,                                    'for subfigures'],
                                    ['amssymb',     None,                                    'need more symbols'],
                                    ['titlesec',    None,                                    "so that we can add more subsections (using 'paragraph')"],
                                    ['xcolor, soul',None,                                   'for the highlighter'],
                                    ['amsmath',     None,                                    ''],
                                    ['amsfonts',    None,                                    ''],
                                    ['cancel',      None,                                    ''],
                                    ['minted',      None,                                    ''],
                                    ['apacite',     None,                                    'apa citation style'],
                                    ['caption',     None,                                    'to set smaller vertical spacing between two figures'],
                                    ['cleveref',    None,    'for clever references'],
                                    ['tcolorbox',   None,                                    ''],
                                    ['float',       None,                                    'to make the figures stay between the text at which they are defined'],
                                    ['pdfpages',    None,                                     ''],
                                    ['totcount',    None,                                     ''],
                                    ['lipsum',      None,                                     ''],
                                    ['ragged2e',    None,                                     'can wrap text for tables in the tabularx environment'],
                                    ['natbib',      None,                                     "Such that we avoid the error (`Illegal parameter number in definition of \\reserved@a`) of not being able to add citations in captions"],
                                    ['pdfcomment',  None,                                     'for popup comments in the .pdf']
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
       

    return PARS
