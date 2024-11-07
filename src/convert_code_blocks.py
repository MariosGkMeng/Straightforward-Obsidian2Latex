import re
import os
from remove_markdown_comment import *
from path_searching import *
from embedded_notes import non_embedded_references_recognizer
from equations import get_fields_from_Obsidian_note

def convert_inline_code_of_line(text):
    # Regular expression to find inline code enclosed in backticks
    pattern = r'`([^`]+)`'
    
    # Replace the inline code with \texttt{} format
    latex_text = re.sub(pattern, r'\\texttt{\1}', text)
    
    return latex_text


def convert_inline_code(S):
    S1 = []
    for s in S: S1.append(convert_inline_code_of_line(s))
    return S1
        
def convert_inline_commands_with_choice(S, PARS):
    
    pattern = r"`= *choice\(.*?`"
    pattern2 = r"\]\]\.[a-zA-Z0-9_.-]+"

    pp=[(i, l) for i, l in enumerate(S) if 'choice(' in l]

    for p_i in pp:
        p = p_i[1]
        mm = re.findall(pattern, p)
        for m in mm:
            ee = non_embedded_references_recognizer([m])
            field = re.search(pattern2, m)[0].replace(']].', '') + ':: '
            filePath = get_embedded_reference_path(f'{ee[0][1][0][0]}', PARS, search_in = 'vault')
            fields_res = get_fields_from_Obsidian_note(filePath, [field])[0]
            if fields_res[0] == 'true':
                replace_with = fields_res[1]
                if replace_with.startswith(2*' '): replace_with = replace_with[1:]
            else:
                replace_with = ''
                
            S[p_i[0]] = S[p_i[0]].replace(m, replace_with)
            
    return S

def code_block_converter(S, PARS):

    if not isinstance(S, list):
        raise Exception('The input needs to be a list!')
    
    begin_text_0 = '\\begin{minted}'
    end_text_0 = '\end{minted}'

    counter = 0
    S1 = []
    code_block_obsidian = '```' 
    language = ''
    settings__admonition = PARS['⚙']['code_blocks']['admonition']
    for i, s in enum(S):
        s1 = s
        if s1.startswith(code_block_obsidian):
            language = ''
            code_block_has_started = counter%2 == 0
            if code_block_has_started:
                language = s1.replace(code_block_obsidian, '').lstrip().rstrip()

                if len(language)>0:
                    if language=='latex':
                        language_additive = ''
                        begin_text = ''
                        end_text = ''
                    else:
                        
                        IS_ADMONITION_BLOCK = language.startswith('ad-')
                        
                        if not IS_ADMONITION_BLOCK:
                            language_additive = '{' + language + '}'
                            begin_text =  begin_text_0
                            end_text = end_text_0
                        else:
                            language_additive = ''
                            idx_kind_default = 0


                            kind_of_block = language.replace('ad-', '').strip()
                            block_kinds = [x[0] for x in settings__admonition]

                            idx_kind = -10
                            for j, b in enumerate(block_kinds):
                                if kind_of_block == b:
                                    idx_kind = j
                                    break

                            if idx_kind==-10:
                                idx_kind = idx_kind_default
                            
                            settings__admonition_block = settings__admonition[idx_kind][1]
                            
                            color    = settings__admonition_block[0]
                            colupper = settings__admonition_block[1]
                            title = kind_of_block

                            end_text = '\end{'+'tcolorbox'+'}'

                            # Check for observation block
                            if kind_of_block == 'attention':
                                t_type = 'Observation'
                                j = i+1
                                while True:
                                    if S[j]:
                                        if not t_type in S[j]:
                                            break
                                        else:
                                            S[j] = '{\Large \\textbf{' + t_type + '}}\n\n\\newline'
                                            S[j+1] = ''
                                            title = ' '
                                            color = 'cyan'
                                            break
                            
                            begin_text =\
                                '\\begin{'+\
                                'tcolorbox'+\
                                '}[width=' + str(1/PARS['num_columns']) + '\\textwidth,colback={' +\
                                color +\
                                '},title={' +\
                                title + '},outer arc=0mm,colupper='+colupper+']'

                else:
                    language_additive = ''
                    begin_text = begin_text_0

                s1 = begin_text+language_additive
            else:
                s1 = end_text

            counter += 1

        if language=='latex': s1 = s1.replace('&', '#&')
            
        S1.append(s1)

    return S1
