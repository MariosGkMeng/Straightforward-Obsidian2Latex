import re
import os
import copy

# For recognizing file names, section names, block names
SPECIAL_CHARACTERS = " ,'%💬⚠💼🟢➕❓❌🔴✔🧑☺📁⚙🔒🤔🟡🔲💊💡🤷‍♂️▶📧🔗🎾👨‍💻📞💭📖ℹ🤖🏢🧠🕒👇📚👉0-9\(\)\(\)\.\-\s"
from remove_markdown_comment import *
from list_of_separate_lines import *
from equations import *

def write_link_in_obsidian_format(s, link_type, is_embedded = False):

    L1 = (len(s[1])>0)
    if link_type == 'section':
        link_prefix = '#'*L1
    elif link_type == 'block':
        link_prefix = '#^'*L1
    else:
        raise Exception('Nothing coded here')

    return is_embedded*'!' + '[[' + s[0] + link_prefix + s[1].replace('#', '') + '|'*(len(s[2])>0) + s[2].replace('|', "") + ']]'

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

    ADD_HYPERTARGET_AT_THE_END_OF_BLOCK = True

    type_of_link = ['sec:', '']
    type_of_link_obsidian = ['#', '#^']
    sections = sections_blocks[0]
    blocks = sections_blocks[1]


    # Just replace the labels, even though they are not being referenced                            ⚠WARNING--1
    if ADD_HYPERTARGET_AT_THE_END_OF_BLOCK:
        for block in blocks:
            line_of_block, block_text = block
            block_text_1 = '^' + block_text
            S[line_of_block] = S[line_of_block].replace(block_text_1, ' \hypertarget{' + block_text + '}{}')
    else:
        raise Exception("NOTHING CODED FOR THIS CASE YET!")


    for I in internal_links:
        for iS in range(2):
            Ii_sb = I[iS+1]

            # try:
            #     if Ii_sb[0][1] == 'Motivations to investigate high-dimensional neural networks':
            #         print("f")
            # except:
            #     print("")

            if len(Ii_sb) != 0:
                
                line_number = I[0]
                for i in Ii_sb:
                    section_i = Ii_sb[0][1]
                    idx = [j for j in range(len(sections_blocks[iS])) if sections_blocks[iS][j][1] == section_i] # index of the section in the section list
                    if len(idx)>0: 
                        # Found match between existing sections and blocks of the file and the referenced section
                        idx=idx[0]

                        label_latex_format = type_of_link[iS] + section_i.replace(' ', '-')
                        hyperref_text = Ii_sb[0][-1].replace('|', '')

                        if type_of_link[iS]!='sec:':
                            label_of_source = ' \hypertarget{' + label_latex_format + '}' #+ '{}' 
                        
                        else:
                            label_of_source = '\label{' + label_latex_format + '}' 

                        if len(hyperref_text) != 0:
                            hyperref_text = '{' + hyperref_text + '}'
                        else:
                            hyperref_text = '{' + 'ADD\\_NAME' + '}'
                            
                        has_already_been_replaced = label_of_source.strip() in S[sections_blocks[iS][idx][0]]
                        if not has_already_been_replaced:
                            # Has not already been replaced

                            label__in_line = S[sections_blocks[iS][idx][0]].replace('\n', '')
                            add__S_repl = ' \label{' + type_of_link[iS] + section_i.replace(' ', '-') + '}'

                            # Perform replacements on the label
                            if iS==0:
                                S[sections_blocks[iS][idx][0]] = label__in_line + add__S_repl
                            else:
                                S[sections_blocks[iS][idx][0]] = label__in_line.replace('^' + label_latex_format, '') + add__S_repl


                        if label_latex_format.startswith("sec:"):
                            hyperref = '\hyperref[' + label_latex_format + ']' + hyperref_text 
                        else:
                            hyperref = '\hyperlink{' + label_latex_format + '}' + hyperref_text 
                        # for blocks, better write "hyperlink"

                        if iS==0:
                            obsidian_hyperref = write_link_in_obsidian_format(Ii_sb[0], 'section')
                        elif iS==1:
                            obsidian_hyperref = write_link_in_obsidian_format(Ii_sb[0], 'block')
                        else:
                            raise Exception("Nothing coded here!")
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


def embedded_references_recognizer(S, options, mode):


    all_chars = '\w' + SPECIAL_CHARACTERS + '\-'
    if not isinstance(S, list):
        raise Exception('Input of the function must be a list of strings!')
        return np.nan

    pattern_embedded_with_section_0 = '!\[\[([\.'+all_chars+']+)(\#['+all_chars+']+)?(\|[' + all_chars + ']+)?\]\]'

    if mode=='normal': 

        if not options['treat_equation_blocks_separately']:
            pattern_embedded_with_section = pattern_embedded_with_section_0
        else:
            # Adjusted regex pattern to exclude strings containing "[[eq__block and any other character]]"
            pattern_embedded_with_section = '!(?!\[\[eq__block).*\[\[([\.'+all_chars+']+)(\#['+all_chars+']+)?(\|[' + all_chars + ']+)?\]\]'
    
    elif mode=='equation_blocks_only':
        pattern_embedded_with_section = pattern_embedded_with_section_0

    else:
        raise Exception('Nothing coded for this case!')

    MATCHES = []
    for i, s in enum(S):
        match_pattern_embedded = re.findall(pattern_embedded_with_section, s)
        if len(match_pattern_embedded) != 0:

            # Extract text starting with '%%lcmd' and ending with 'lcmd%%'
            match_latex_command_from_obsidian = re.search(r'%%lcmd(.*?)lcmd%%', s)

            extracted_latex_command_from_obsidian = ''
            if match_latex_command_from_obsidian:
                extracted_latex_command_from_obsidian = match_latex_command_from_obsidian.group(0)  # Get the entire matched text


            MATCHES.append([i, match_pattern_embedded, extracted_latex_command_from_obsidian])
            # path-finder

    # to see the names of the embedded files: `[m[1][0][0] for m in MATCHES]`
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


def replace_obsidian_bibliography_link_with_cite(s):
    pattern = r'\[\[p(\d+)\]\]'  # Updated regular expression pattern with capturing group
    replaced_string = re.sub(pattern, r'\\cite{p\1}', s)
    return replaced_string


def non_embedded_references_converter(S, options):

    links = non_embedded_references_recognizer(S)

    if options['treat_citations']:
        # change citations, like: "[[p110]]" to "\cite{p110}"
        for i, s in enum(S):
            S[i] = replace_obsidian_bibliography_link_with_cite(s)


    for link in links:
        line = link[0]  
        for link1 in link[1]:
            tmp1 = link1

            if len(tmp1[2]) == 0:
                S[line] = S[line].replace('[[' + tmp1[0] +  ']]', tmp1[0])

            else:
                S[line] = S[line].replace('[[' + tmp1[0]+tmp1[2] +  ']]', tmp1[2][1:])


    return S


def search_embedded_reference_in_vault(u, PARS, search_in = 'vault'):

    '''
    Finds the paths of embedded references in the vault
    '''
    files = []
    vault_path = PARS['📁'][search_in]
    # for folder, subfolders, files in os.walk(PARS['📁']['vault']):
    #    for f in files:
    #     if f.endswith('.md'): files_md.append(f)
    os.chdir(vault_path)
    for root, dirs, files in os.walk(vault_path):
        if u in files: return os.path.join(root,u)
    return ''


def get_embedded_reference_path(fileName, PARS, search_in = 'vault'):



    path_list_of_notes = PARS['📁']['list_paths_notes'] # search in that list first, and if the file doesn't exist, then search the entire vault (which is time-consuming)
    
    # Read the text file
    with open(path_list_of_notes, 'r', encoding='utf8') as file:
        lines = file.readlines()
    
    # Search for the fileName in the lines and retrieve associated paths
    matching_paths = [line.strip() for line in lines if line.startswith(fileName+":")]


    found_extension_that_is_not_md = False
    extensions = ['.png', '.jpg', '.pdf']
    for extension in extensions:
        if fileName.endswith(extension):
            found_extension_that_is_not_md = True
            fileNameWithExtension = fileName

    if not found_extension_that_is_not_md:
        fileNameWithExtension = fileName + '.md'

    if matching_paths:
        # Process retrieved paths
        for path_line in matching_paths:
            path = path_line.split(': ')[1].strip()
            PATH_DOES_NOT_EXIST = not os.path.exists(path)
            if PATH_DOES_NOT_EXIST:
                new_path = search_embedded_reference_in_vault(fileNameWithExtension, PARS, search_in=search_in)
                if new_path:
                    # update path_list_of_notes for the next time
                    updated_line = f"{fileName}: {new_path}\n"
                    lines[lines.index(path_line+'\n')] = updated_line
                    with open(path_list_of_notes, 'w', encoding='utf-8') as file:
                        file.writelines(lines)
                    return new_path
                else:
                    raise Exception(f"Path '{path}' not found. Also, unable to find an alternative path for '{fileName}'.")
            else:
                return path

    else:

        path_found = search_embedded_reference_in_vault(fileNameWithExtension, PARS, search_in='vault')
        if path_found:
            with open(path_list_of_notes, 'a', encoding='utf-8') as file:
                # update path_list_of_notes for the next time
                file.write(f"{fileName}: {path_found}\n")
            # print(f"Path for '{fileName}' appended as a new line in the text file.")
            return path_found
        else:
            raise Exception(f"No information found for '{fileName}' in the provided text file and unable to find an alternative path.")



def unfold_embedded_notes(S, md__files_embedded, PARS, mode='normal'):

    '''
    Unfolds the content of embedded notes.

    ---------
    Arguments
    ---------

        1. S (List): the content of the note (including so-far conversions)
        2. md__files_embedded(List): a list that contains all embedded references. It is needed to ensure that we do not reach an infinite loop of unfolding notes

    '''

    mode__collection_of_new_content = 'LISTS' # 'LISTS' or 'ELEMENTWISE'

    if mode=='normal':
        where_to_search_for_embedded_notes = 'vault'
    elif mode=='equation_blocks_only':
        where_to_search_for_embedded_notes = 'equation_blocks'
    else:
        raise Exception("Nothing coded for this case!")

    if not isinstance(md__files_embedded, list):
        raise Exception('md__files_embedded variable must be of type list!')

    if mode__collection_of_new_content == 'LISTS':
        LISTS_S = []

    file_types = ['.png', '.pdf', '.jpg']
    ss1 = embedded_references_recognizer(S, PARS['⚙']['EMBEDDED REFERENCES'], mode)

    line_numbers_unfolded_notes = [ln[0] for ln in ss1]

    for ln in ss1:
        line_number = ln[0] #
        line_embed = ln[1]

        has_extension = False

        embedded_ref = line_embed[0][0]
        section=line_embed[0][1]
        markdown_ref = write_link_in_obsidian_format([line_embed[0][0], section, line_embed[0][2]], 'section',is_embedded=True)
        for file_type in file_types:
            if file_type in embedded_ref:
                has_extension = True
                # break

        if not has_extension: 
            # means that it is a .md file, which we need to unfold
            # BUG_2 (line below): the following condition has the problem: if there's multiple times that the embedded_ref appears, but with a different section/block, then it will be ignored! 
            # We can use CONDITION_2, that allows all embedded notes to be inserted, with the risk of allowing infinite loops
            # To solve that, we could track the "parent" of an embedded reference
            CONDITION_1 = not embedded_ref in md__files_embedded
            CONDITION_2 = True
            if CONDITION_2:
                # Unfold this note ONLY when it hasn't already been unfolded
                md__files_embedded.append(embedded_ref)
                
                path_embedded_reference = get_embedded_reference_path(embedded_ref, PARS, search_in=where_to_search_for_embedded_notes)

                if len(path_embedded_reference) == 0:
                    raise Exception('File: ' + embedded_ref + ' cannot be found in ' + PARS['📁'][where_to_search_for_embedded_notes])

                section_name = section.lstrip('#')
                content__unfold = extract_section_from_file(path_embedded_reference, section_name)

                if mode!='equation_blocks_only':
                    # since we don't expect to have comments in the single block (code optimization)
                    content__unfold = remove_markdown_comments(content__unfold)
                else:
                    content__unfold = EQUATIONS__prepare_label_in_initial_Obsidian_equation(content__unfold, embedded_ref)

                S[line_number] = S[line_number].replace(markdown_ref, ''.join(content__unfold))

    if mode!='normal':
        S = get_list_of_separate_string_lines(S)
    else:
        if mode__collection_of_new_content == "LISTS":
            # we perform this, since the bullet_list_converter function would not work if the bullet points don't appear in new lines (list elements)
            z = 0
            S1 = []
            for i in line_numbers_unfolded_notes:
                S1.append(S[z:i] + S[i].split('\n'))
                z=i+1
            
            S1.append(S[z+1:])
            S2 = []
            for s in S1: S2+=s

            S = S2


    return S, md__files_embedded


def extract_section_from_file(obsidian_file, section):

    file_hierarchy, Lines = get_file_hierarchy(obsidian_file)
    if section == '':
        return Lines

    L = len(Lines)
    have_found_the_section = False
    have_found_the_end_of_section = False
    for section_i in file_hierarchy:
        if not have_found_the_section:
            if section_i[2].replace("%%", "").replace('[[', "").replace(']]', "").strip()==section.replace("%%", ""):
                have_found_the_section = True
                level = section_i[1]

                line_number_start = section_i[0]+1
        else:
            if section_i[1] == level:
                have_found_the_end_of_section = True
                line_number_end = section_i[0]
                break

    if have_found_the_section:
        if not have_found_the_end_of_section:
            line_number_end = L
    else:
        line_number_start = 0
        line_number_end = L


    extracted_text = Lines[line_number_start:line_number_end]


    return extracted_text

    
def get_file_hierarchy(obsidian_file):
    
    if not isinstance(obsidian_file, str):
        raise Exception('obsidian_file variable must be of type string, and specifically, a path!')

    f = open(obsidian_file, 'r', encoding='utf8')
    Lines = f.readlines()

    pattern_how_many_sections = r'^#+'
    comment_pattern = r'^\s*#+\s*%%.*%%.*$'  # Pattern to detect commented titles

    sections = []
    for iL, ln_f in enumerate(Lines):
        has_section = re.findall(pattern_how_many_sections, ln_f)
        #is_commented_title = re.match(comment_pattern, ln_f)

        if has_section: # and not is_commented_title:
            has_section = has_section[0]
            section_hierarchy = len(has_section)
            tmp_l = ln_f.replace(has_section, '').replace('\n', '').rstrip().lstrip()
            section_i = [iL, section_hierarchy, tmp_l]

            sections.append(section_i)

    f.close()

    return sections, Lines


# file = 'C:\\Users\\mariosg\\OneDrive - NTNU\\FILES\\workTips\\Literature\\Theory\\Theory\\Math\\Equations\\Lyapunov Stability.md'
# pp=get_file_hierarchy(file)
# oo = extract_section_from_file(file, 'Stability Definitions')
# print('d')
