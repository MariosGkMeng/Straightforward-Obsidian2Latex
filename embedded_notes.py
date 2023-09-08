import re
import os

# For recognizing file names, section names, block names
SPECIAL_CHARACTERS = " '%💬⚠💼🟢➕❓🔴✔🧑☺📁⚙🔒🟡🔲💊💡🤷‍♂️▶📧🔗🎾👨‍💻📞💭📖ℹ🤖🏢🧠🕒👇📚👉0-9\(\)\(\)\.\-\s"
from remove_markdown_comment import *


def write_link_in_obsidian_format(s, link_type):

    L1 = (len(s[1])>0)
    if link_type == 'section':
        link_prefix = '#'*L1
    elif link_type == 'block':
        link_prefix = '#^'*L1
    else:
        raise Exception('Nothing coded here')

    return '[[' + s[0] + link_prefix + s[1] + '|'*(len(s[2])>0) + s[2].replace('|', "") + ']]'

def internal_links__identifier(S):

    '''
    Identifies internal links in the document, in the form of '[[notename^linkname|name of reference]]'
    '''


    if not isinstance(S, list):
        raise Exception('Input of the function must be a list of strings!')
        return np.nan


    pattern_sections = '\[\[([\w\s-]+)\#([\w' + SPECIAL_CHARACTERS + '\-]+)(\|[\w' + SPECIAL_CHARACTERS + '\-]+)?\]\]'
    pattern_blocks = r'\[\[([\w\s-]+)\#\^([\w' + SPECIAL_CHARACTERS + '\-]+)(\|[\w' + SPECIAL_CHARACTERS + '\-]+)?\]\]'
    MATCHES = []
    for i, s in enum(S):
        match_sections = re.findall(pattern_sections, s)
        match_blocks = re.findall(pattern_blocks, s)
        if len(match_sections) != 0 or len(match_blocks) != 0:
            MATCHES.append([i, match_sections, match_blocks])
    
    return MATCHES

# def external_links__identifier(S):
#     '''
#     Identifies external links in the document, in the form of '[[notename^linkname|name of reference]]'
#     '''



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
                
                line_number = I[0]
                for i in Ii_sb:
                    section_i = Ii_sb[0][1]
                    idx = [j for j in range(len(sections_blocks[iS])) if sections_blocks[iS][j][1] == section_i]
                    if len(idx)>0: 
                        # Found match between existing sections and blocks of the file and the referenced section
                        idx=idx[0]

                        label_latex_format = type_of_link[iS] + section_i.replace(' ', '-')
                        label_of_source = ' \label{' + label_latex_format + '}'
                        hyperref_text = Ii_sb[0][-1].replace('|', '')
                        if len(hyperref_text) != 0:
                            hyperref_text = '{' + hyperref_text + '}'
                        else:
                            hyperref_text = '{' + 'ADD_NAME' + '}'

                        has_already_been_replaced = label_of_source in S[sections_blocks[iS][idx][0]]
                        if not has_already_been_replaced:
                            # Has not already been replaced

                            label__in_line = S[sections_blocks[iS][idx][0]].replace('\n', '')
                            add__S_repl = ' \label{' + type_of_link[iS] + section_i.replace(' ', '-') + '}'

                            # Perform replacements on the label
                            if iS==0:
                                S[sections_blocks[iS][idx][0]] = label__in_line + add__S_repl
                            else:
                                S[sections_blocks[iS][idx][0]] = label__in_line.replace('^' + label_latex_format, '') + add__S_repl


                        hyperref = '\hyperref[' + label + ']' + hyperref_text

                        obsidian_hyperref = '[[' + Ii_sb[0][0] + type_of_link_obsidian[iS] + Ii_sb[0][1] + Ii_sb[0][2] + ']]'
                        S[line_number] = S[line_number].replace(obsidian_hyperref, hyperref)
                    else:
                        # did not find anything, therefore leaving the name only

                        link_name = Ii_sb[0][2].replace('|', "")
                        if len(link_name)>0:
                            if iS==0:
                                type_of_link = 'section'
                            else:
                                type_of_link = 'block'
                            text_to_replace = write_link_in_obsidian_format(Ii_sb[0], type_of_link)
                            S[line_number] = S[line_number].replace(text_to_replace, link_name)
                        
    return S


def embedded_references_recognizer(S):


    all_chars = '\w' + SPECIAL_CHARACTERS + '\-'
    if not isinstance(S, list):
        raise Exception('Input of the function must be a list of strings!')
        return np.nan

    # pattern_embedded = '!\[\[([\.'+all_chars+']+)(\|[' + all_chars + ']+)?\]\]'
    pattern_embedded_with_section = '!\[\[([\.'+all_chars+']+)(\#['+all_chars+']+)?(\|[' + all_chars + ']+)?\]\]'
    MATCHES = []
    for i, s in enum(S):
        match_pattern_embedded = re.findall(pattern_embedded_with_section, s)
        if len(match_pattern_embedded) != 0:
            MATCHES.append([i, match_pattern_embedded])
            # path-finder

    
    return MATCHES


def non_embedded_references_recognizer(S):


    all_chars = '\w' + SPECIAL_CHARACTERS + '\-'
    if not isinstance(S, list):
        raise Exception('Input of the function must be a list of strings!')

    # pattern_embedded = '\[\[([\.'+all_chars+']+)(\|[' + all_chars + ']+)?\]\]'
    pattern_embedded_with_section = '\[\[([\.'+all_chars+']+)(\#['+all_chars+']+)?(\|[' + all_chars + ']+)?\]\]'
    MATCHES = []
    for i, s in enum(S):
        match_pattern_embedded = re.findall(pattern_embedded_with_section, s)
        if len(match_pattern_embedded) != 0:
            MATCHES.append([i, match_pattern_embedded])
            # path-finder

    return MATCHES


def non_embedded_references_converter(S):
    links = non_embedded_references_recognizer(S)

    for link in links:
        line = link[0]  
        tmp1 = link[1][0]

        if len(tmp1[2]) == 0:
            S[line] = S[line].replace('[[' + tmp1[0] +  ']]', tmp1[0])

        else:
            S[line] = S[line].replace('[[' + tmp1[0]+tmp1[2] +  ']]', tmp1[2][1:])


    return S




def embedded_references_path_finder(u, PARS):

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




def unfold_embedded_notes(S, md__files_embedded, PARS):

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

    file_types = ['.png', '.pdf', '.jpg']

    for ln in ss1:
        line_number = ln[0]
        line_embed = ln[1]

        has_extension = False

        embedded_ref = line_embed[0][0]
        section=line_embed[0][1]
        markdown_ref = '![[' + line_embed[0][0] + section + line_embed[0][2]    +    ']]'
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

                path = embedded_references_path_finder(embedded_ref, PARS)

                if len(path) == 0:
                    raise Exception('File: ' + embedded_ref + ' cannot be found in ' + PARS['📁']['vault'])

                # try:
                with open(path, 'r', encoding='utf8') as f:
                    i_section_start = 0
                    section_started = False
                    i_section_end = -1
                    content__embedded_notes = f.readlines()
                    maybe_found_section = section.startswith('#')
                    if maybe_found_section:
                        # has section
                        pattern_how_many_sections = r'^#+'
                        pattern_for_section = r'^#+\s\w+$' 
                        for iL, ln_f in enum(content__embedded_notes):
                            tmp_l = ln_f.replace('%% ', '').replace('%%', '').replace('\n', '').rstrip()
                            search_results = re.findall(pattern_for_section, tmp_l)
                            has_section = re.findall(pattern_how_many_sections, ln_f)
                            if has_section:
                                has_section = has_section[0]
                                tmp_l = ln_f.replace(has_section, '').replace('%%', '').replace('\n', '').rstrip().lstrip()

                                if not section_started:
                                    section_started = True
                                    i_section_start = iL+1
                                    
                                    try:
                                        txt_find = search_results[0]
                                    except:
                                        print("") # Embedded-Section-Error
                                    # section_hierarcy = len(re.findall(pattern_how_many_sections, txt_find)[0])
                                    section_hierarcy = len(has_section)


                                else:
                                    if len(has_section) == section_hierarcy:
                                        # section ended, since we found a new section with the same hierarchy
                                        i_section_end = iL
                                        break

                    if i_section_end==-1:
                        content__unfold = content__embedded_notes[i_section_start:]
                    else:
                        content__unfold = content__embedded_notes[i_section_start:i_section_end]

                # except:
                    # raise Exception('File: ' + embedded_ref + ' cannot be found in ' + PARS['📁']['vault'])


                S[line_number] = S[line_number].replace(markdown_ref, ''.join(content__unfold))
 
    return S, md__files_embedded