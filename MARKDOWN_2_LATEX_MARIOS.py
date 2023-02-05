# TASKS
# --- 1. some latex commands are written twice



import re

SPECIAL_CHARACTERS = ' 👀💊💁🏼✔️🤬🎾😧🏠⚠️😊❓🏫💡🟢🔴%'

def match_pattern(text):
    # pattern = r'\[\[([\w-]+)\#([\w-]+)\|([\w-]+)\]\]'
    pattern_sections = '\[\[([\w-]+)\#([\w' + SPECIAL_CHARACTERS + '\-]+)(\|[\w' + SPECIAL_CHARACTERS + '\-]+)?\]\]'
    pattern_blocks = '\[\[([\w-]+)\^([\w' + SPECIAL_CHARACTERS + '\-]+)(\|[\w' + SPECIAL_CHARACTERS + '\-]+)?\]\]'
    match_sections = re.findall(pattern_sections, text)
    match_blocks = re.findall(pattern_blocks, text)
    return [match_sections, match_blocks]



print(match_pattern('Please refer to [[logfile#section1|thisnote]] or [[logfile^💡 section1|thatnote]]'))


def conv_dict(D):
    for key in D.keys():
        if D[key] == '🟢':
            D[key] = True
        elif D[key] == '🔴':
            D[key] = False
    return D


is_in_table_line = lambda x: x.startswith('|') and x.endswith('|')


ID__TABLES__table_alignment__center = 0
ID__TABLES__table_alignment__right  = 1
ID__TABLES__table_alignment__middle = 2


ID__TABLES__PACKAGE__longtblr = 0
ID__TABLES__PACKAGE__tabularx = 1

ID__CNV__TABLE_STARTED      = 0
ID__CNV__TABLE_ENDED        = 1
ID__CNV__IDENTICAL          = 2

# ⚠ does not work for longtblr!
CMD__TABLE__TABULARX__CENTERING = '\\newcolumntype{Y}{>{\\centering\\arraybackslash}X}'




path0 = 'C:\\Users\\mariosg\\OneDrive - NTNU\\FILES\\AUTOMATIONS\\'


PARS = conv_dict(dict({
    '⚙': 
        conv_dict(dict({'TABLES':  
                conv_dict(dict({
                                  'package': ID__TABLES__PACKAGE__longtblr,
                       'hlines-to-all-rows': '🔴',
                        'any-hlines-at-all': '🔴',
                                'alignment': [
                                                ID__TABLES__table_alignment__center,
                                                ID__TABLES__table_alignment__middle],
                                'rel-width': 1.2
                }))})),
    '📁':
         dict({
                'markdown-file': path0 + 'example.md',
                     'tex-file': path0 + 'example.tex'
            }),
    'par':
        dict({
            'tabular-package':
                            dict({
                                       'names': ['longtblr', 'tabularx'],
                                'before-lines': ['{colspec}']
                            })
        })
}))


def identify__tables(S):

    table_indexes = []
    table_has_started = False
    for i, l in enumerate(S):
        lstr = l.lstrip().rstrip()
        is_table_line = is_in_table_line(lstr)        
        if is_table_line and (not table_has_started):
            table_has_started = True
            idx__table_start = i
        # ⚠ NEVER add "or (i == len(S)-1)" to the condition below    
        elif (not is_table_line and table_has_started):
            table_has_started = False
            idx__table_end = i
            table_indexes.append(idx__table_start)
            table_indexes.append(idx__table_end)


    return table_indexes
            

            



def convert__tables(S):
    '''
    Converts tables    
    '''

    TABLE_SETTINGS = PARS['⚙']['TABLES']
    package = TABLE_SETTINGS['package']
    add_txt = ''
    if (ID__TABLES__table_alignment__center in TABLE_SETTINGS['alignment']) \
        and package == ID__TABLES__PACKAGE__longtblr:
        add_txt = '\centering '


    # After having found the table
    ## We expect that the 1st line defines the columns

    cols = S[0].split('|')
    cols = [[x.lstrip().rstrip() for x in cols if len(x)>0 and x!='\n']]

    C = []
    for s in S[2:]:
        c = s.split('|')
        c = [x.lstrip().rstrip() for x in c if len(x)>0 and x!='\n']
        C.append(c)

    y = cols + C

    # CONVERT
    N_cols = len(cols[0])

    latex_table = []
    addText = ''
    for i, c in enumerate(y):
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

        if ID__TABLES__table_alignment__center in TABLE_SETTINGS['alignment']:
            lbefore.append(CMD__TABLE__TABULARX__CENTERING)
            colPrefix = 'Y'
        else:
            colPrefix = 'X'

        if (ID__TABLES__table_alignment__middle in TABLE_SETTINGS['alignment']):
            lbefore.append('\\renewcommand\\tabularxcolumn[1]{m{#1}}')

        latex_before_table = lbefore + [
            '\\begin{center}',
            '\\begin'+PCKG_NAME+'{\\textwidth}{' + '|' + N_cols*(colPrefix+'|') + '}',
            '   \hline'
        ]

        latex_after_table = [
            '   \hline',
            '\end'+PCKG_NAME,
            '\end{center}'
        ]



    elif package == ID__TABLES__PACKAGE__longtblr:

        PCKG_NAME = '{longtblr}'

        latex_before_table = [
            '\\begin{center}',
            '\\begin' + PCKG_NAME + '[',
            'caption = {},',
            'entry = {},',
            'label = {},',
            'note{a} = {},',
            'note{$\dag$} = {}]',
            '   {colspec = {'+ N_cols*'X' +'}, width = ' + str(TABLE_SETTINGS['rel-width']) + '\linewidth, hlines, rowhead = 2, rowfoot = 1}'
            ]  

        latex_after_table = [
            '\end' + PCKG_NAME,
            '\end{center}'
        ]

        add_hline_at_end = False # to be moved to user settings
        if add_hline_at_end:
            latex_after_table = '   \hline' + latex_after_table


    else:
        raise Exception('NOTHING CODED HERE!')


    LATEX = latex_before_table + latex_table + latex_after_table


    return LATEX


def internal_links__identifier(S):

    pattern_sections = '\[\[([\w-]+)\#([\w' + SPECIAL_CHARACTERS + '\-]+)(\|[\w' + SPECIAL_CHARACTERS + '\-]+)?\]\]'
    pattern_blocks = '\[\[([\w-]+)\^([\w' + SPECIAL_CHARACTERS + '\-]+)(\|[\w' + SPECIAL_CHARACTERS + '\-]+)?\]\]'
    match_sections = re.findall(pattern_sections, S)
    match_blocks = re.findall(pattern_blocks, S)
    return [match_sections, match_blocks]



def package_loader():

    packages_to_load = []


    if PARS['⚙']['TABLES']['package'] == ID__TABLES__PACKAGE__longtblr:
        packages_to_load.append('\\usepackage{tabularray}')
        packages_to_load.append('\\usepackage{longtable}')
    elif PARS['⚙']['TABLES']['package'] == ID__TABLES__PACKAGE__tabularx:
        packages_to_load.append('\\usepackage{tabularx}')

    return packages_to_load

PATHS = PARS['📁']

with open(PATHS['markdown-file'], 'r') as f:
    content = f.readlines()


# Replace headers \==================================================
Lc = len(content)-1
for i in range(Lc+1):
    # ⚠ The sequence of replacements matters: 
    # ---- replace the lowest-level subsections first
    content[i] = re.sub(r'### (.*)', r'\\subsubsection{\1}', content[i])
    content[i] = re.sub(r'## (.*)', r'\\subsection{\1}', content[i])
    content[i] = re.sub(r'# (.*)', r'\\section{\1}', content[i])
# \==================================================\==================================================

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
for i in range(int(len(tmp1)/2)):
    LATEX_TABLES.append(convert__tables(content[tmp1[2*i]:tmp1[2*i+1]]))


# for i, L in enumerate(content):

#     for idx_table in IDX__TABLES:
#         LATEX_TABLES.append(convert__tables(content[idx_table[0]:idx_table[1]]))

LATEX = []
i0 = IDX__TABLES[0]
i_tables = 0
for j, i in enumerate(IDX__TABLES[1:]):
    if TYPE_OF_CNV[j] == ID__CNV__IDENTICAL:
        LATEX += content[i0:i]
    elif TYPE_OF_CNV[j] == ID__CNV__TABLE_STARTED:
        LATEX += LATEX_TABLES[i_tables]
        i_tables += 1
        print('')
    
    i0 = i
    
    

PREAMBLE = ['\documentclass{article}'] + package_loader() + ['\\begin{document}']


LATEX = PREAMBLE + LATEX + ['\end{document}']
with open(PATHS['tex-file'], 'w') as f:
    for l in LATEX:
        if not l.endswith('\n'): l+='\n'
        f.write(l)

