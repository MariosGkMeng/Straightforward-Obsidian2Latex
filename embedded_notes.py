import re
import os

# For recognizing file names, section names, block names
SPECIAL_CHARACTERS = ' %💬⚠💼🟢➕❓🔴✔🧑☺📁⚙🔒🟡🔲💊💡🤷‍♂️▶📧🔗🎾👨‍💻📞💭📖ℹ🤖🏢🧠🕒👇📚👉0-9'
from remove_markdown_comment import *


def internal_links__identifier(S):

    '''
    Identifies internal links in the document, in the form of '[notename^linkname|name of reference]'
    '''


    if not isinstance(S, list):
        raise Exception('Input of the function must be a list of strings!')
        return np.nan


    pattern_sections = '\[\[([\w-]+)\#([\w' + SPECIAL_CHARACTERS + '\-]+)(\|[\w' + SPECIAL_CHARACTERS + '\-]+)?\]\]'
    pattern_blocks = '\[\[([\w-]+)\#\^([\w' + SPECIAL_CHARACTERS + '\-]+)(\|[\w' + SPECIAL_CHARACTERS + '\-]+)?\]\]'
    
    MATCHES = []
    for i, s in enum(S):
        match_sections = re.findall(pattern_sections, s)
        match_blocks = re.findall(pattern_blocks, s)
        if len(match_sections) != 0 or len(match_blocks) != 0:
            MATCHES.append([i, match_sections, match_blocks])
    
    return MATCHES

def internal_links__enforcer(S, sections_blocks, internal_links):

    '''
    Converts the Obsidian internal links to Latex internal links
    '''

    type_of_link = ['sec:', '']
    type_of_link_obsidian = ['#', '#^']
    sections = sections_blocks[0]
    blocks = sections_blocks[1]


    # Just replace the labels, even though they are not being referenced                            ⚠WARNING--1
    for block in blocks:
        line_of_block, block_text = block
        block_text_1 = '^' + block_text
        S[line_of_block] = S[line_of_block].replace(block_text_1, ' \label{' + block_text + '}')


    for I in internal_links:
        for iS in range(2):
            Ii_sb = I[iS+1]
            if len(Ii_sb) != 0:
                
                for i in Ii_sb:
                    section_i = Ii_sb[0][1]
                    idx = [j for j in range(len(sections_blocks[iS])) if sections_blocks[iS][j][1] == section_i]
                    if len(idx)>0: 
                        idx=idx[0]

                        label = type_of_link[iS] + section_i.replace(' ', '-')
                        label_of_source = ' \label{' + label + '}'
                        hyperref_text = Ii_sb[0][-1].replace('|', '')
                        if len(hyperref_text) != 0:
                            hyperref_text = '{' + hyperref_text + '}'
                        else:
                            hyperref_text = '{' + 'ADD_NAME' + '}'

                        if not label_of_source in S[sections_blocks[iS][idx][0]]:
                            # Has not already been replaced

                            label__in_line = S[sections_blocks[iS][idx][0]].replace('\n', '')
                            add__S_repl = ' \label{' + type_of_link[iS] + section_i.replace(' ', '-') + '}'

                            # Perform replacements on the label
                            if iS==0:
                                S[sections_blocks[iS][idx][0]] = label__in_line + add__S_repl
                            else:
                                S[sections_blocks[iS][idx][0]] = label__in_line.replace('^' + label, '') + add__S_repl


                        hyperref = '\hyperref[' + label + ']' + hyperref_text

                        obsidian_hyperref = '[[' + Ii_sb[0][0] + type_of_link_obsidian[iS] + Ii_sb[0][1] + Ii_sb[0][2] + ']]'
                        S[I[0]] = S[I[0]].replace(obsidian_hyperref, hyperref)


                    # else:
                    #     # Just replace the labels, even though they are not being referenced
                    #     for block in blocks:
                    #         line_of_block, block_text = block
                    #         block_text_1 = '^' + block_text
                    #         S[line_of_block] = S[line_of_block].replace(block_text_1, ' \label{' + block_text + '}')




    return S




def embedded_references_recognizer(S):


    all_chars = '\w' + SPECIAL_CHARACTERS + '\-'
    if not isinstance(S, list):
        raise Exception('Input of the function must be a list of strings!')
        return np.nan

    pattern_embedded = '!\[\[([\.'+all_chars+']+)(\|[\w' + SPECIAL_CHARACTERS + '\-]+)?\]\]'
    MATCHES = []
    for i, s in enum(S):
        match_pattern_embedded = re.findall(pattern_embedded, s)
        if len(match_pattern_embedded) != 0:
            MATCHES.append([i, match_pattern_embedded])
            # path-finder

    
    return MATCHES


def embedded_references_path_finder(u):

    '''
    Finds the paths of embedded references in the vault
    '''
    files = []
    vault_path = PARS['📁']['vault']
    # for folder, subfolders, files in os.walk(PARS['📁']['vault']):
    #    for f in files:
    #     if f.endswith('.md'): files_md.append(f)
    os.chdir(vault_path)
    for root, dirs, files in os.walk(vault_path):
        if u in files: return os.path.join(root,u)
    return ''




def unfold_embedded_notes(S, md__files_embedded):

    '''
    Unfolds the content of embedded notes.

    ---------
    Arguments
    ---------

        1. S (List): the content of the note (including so-far conversions)
        2. md__files_embedded(List): a list that contains all embedded references. It is needed to ensure that we do not reach an infinite loop of unfolding notes

    '''


    if not isinstance(md__files_embedded, list):
        raise Exception('md__files_embedded variable must be of type list!')

    ss1 = embedded_references_recognizer(S)

    file_types = ['.png', '.pdf', 'jpg']

    for ln in ss1:
        line_number = ln[0]
        line_embeds = ln[1]
        for line_embed in line_embeds:

            has_extension = False

            embedded_ref = line_embed[0]
            markdown_ref = '![[' + line_embed[0] + line_embed[1]    +    ']]'
            for file_type in file_types:
                if file_type in embedded_ref:
                    has_extension = True
                    # break

            if not has_extension: 
                # means that it is a .md file, which we need to unfold

                if not embedded_ref in md__files_embedded:
                    # Unfold this note ONLY when it hasn't already been unfolded
                    md__files_embedded.append(embedded_ref)

                    embedded_ref += '.md'

                    path = embedded_references_path_finder(embedded_ref)

                    if len(path) == 0:
                        raise Exception('File: ' + embedded_ref + ' cannot be found in ' + PARS['📁']['vault'])

                    try:
                        with open(path, 'r', encoding='utf8') as f:
                            content__embedded_notes = f.readlines()
                    except:
                        raise Exception('File: ' + embedded_ref + ' cannot be found in ' + PARS['📁']['vault'])


                    S[line_number] = S[line_number].replace(markdown_ref, ''.join(content__embedded_notes))
 
    return S, md__files_embedded