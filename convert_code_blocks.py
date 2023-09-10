import re
import os
from remove_markdown_comment import *


def code_block_converter(S):

    if not isinstance(S, list):
        raise Exception('The input needs to be a list!')
    

    counter = 0
    S1 = []
    code_block_obsidian = '```' 
    for i, s in enum(S):
        s1 = s
        if s1.startswith(code_block_obsidian):
            if counter%2 == 0:
                language = s1.replace(code_block_obsidian, '').lstrip().rstrip()
                if language:
                    language_additive = '{' + language + '}'
                else:
                    language_additive = ''
                s1 = '\\begin{minted}'+language_additive
            else:
                s1 = '\end{minted}'

            counter += 1

        S1.append(s1)

    return S1


