import re
import os
from remove_markdown_comment import *


def code_block_converter(S, PARS):

    if not isinstance(S, list):
        raise Exception('The input needs to be a list!')
    
    begin_text_0 = '\\begin{minted}'
    end_text_0 = '\end{minted}'

    counter = 0
    S1 = []
    code_block_obsidian = '```' 

    settings__admonition = PARS['⚙']['code_blocks']['admonition']
    for i, s in enum(S):
        s1 = s
        if s1.startswith(code_block_obsidian):
            if counter%2 == 0:
                # we are at the start
                language = s1.replace(code_block_obsidian, '').lstrip().rstrip()

                if language:

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
                            '}[width=\\textwidth,colback={' +\
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

        S1.append(s1)

    return S1
