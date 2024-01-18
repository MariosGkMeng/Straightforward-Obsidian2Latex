import re
import os
from remove_markdown_comment import *


def code_block_converter(S):

    if not isinstance(S, list):
        raise Exception('The input needs to be a list!')
    
    begin_text_0 = '\\begin{minted}'
    end_text_0 = '\end{minted}'

    counter = 0
    S1 = []
    code_block_obsidian = '```' 
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
                        kind_of_block = language.replace('ad-', '').strip()
                        if kind_of_block == 'warning':
                            color = 'red'
                            colupper = 'white'
                        else:
                            color = 'white'
                            colupper = 'black'

                        title = kind_of_block

                        begin_text = '\\begin{'+'tcolorbox'+'}[width=\\textwidth,colback={' + color + '},title={' + title + '},outer arc=0mm,colupper='+colupper+']'
                        end_text = '\end{'+'tcolorbox'+'}'
                else:
                    language_additive = ''
                    begin_text = begin_text_0


                s1 = begin_text+language_additive
            else:
                s1 = end_text

            counter += 1

        S1.append(s1)

    return S1


