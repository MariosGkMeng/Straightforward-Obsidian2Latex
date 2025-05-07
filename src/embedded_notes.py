import re
import os
import copy
# For recognizing file names, section names, block names
# SPECIAL_CHARACTERS =  = get_special_characters()
                     
from remove_markdown_comment import *
from equations import *
from path_searching import *
from special_characters import *
from bullet_list__converter import *
# from

special_cases = ['eq__block', 'figure__block', 'table__block']

def write_link_in_obsidian_format(s, link_type, is_embedded = False):

    link_section_or_block = s[1]
    L1 = (len(link_section_or_block)>0)
    if link_type == 'section':
        link_prefix = '#'*L1
    elif link_type == 'block':
        link_prefix = '#^'*L1
    else:
        raise Exception('Nothing coded here')

    note_name = s[0]
    alias = '|'*(len(s[2])>0) + s[2].replace('|', "")
    text_inside_obsidian_link = note_name + link_prefix + link_section_or_block.replace('#', '') + alias
    return is_embedded*'!' + '[[' + text_inside_obsidian_link + ']]'

def internal_links__identifier(S):

    '''
    Identifies internal links in the document, in the form of '[[notename^linkname|name of reference]]'
    '''

    if not isinstance(S, list):
        raise Exception('Input of the function must be a list of strings!')
        return np.nan

    # OLD
    # pattern_sections = '\[\[([\w\s-]+)\#([\w' + SPECIAL_CHARACTERS + '\-]+)(\|[\w' + SPECIAL_CHARACTERS + '\-]+)?\]\]'
    # pattern_blocks = r'\[\[([\w\s-]+)\#\^([\w' + SPECIAL_CHARACTERS + '\-]+)(\|[\w' + SPECIAL_CHARACTERS + '\-]+)?\]\]'

    # NEW (from ChatGPT)
    pattern_sections = r'\[\[\s*([\w\s-]+)\s*#\s*([\w' + re.escape(SPECIAL_CHARACTERS) + r'\-]+)(\|[\w' + re.escape(SPECIAL_CHARACTERS) + r'\-]+)?\s*\]\]'
    pattern_blocks = r'\[\[\s*([\w\s-]+)\s*#\^\s*([\w' + re.escape(SPECIAL_CHARACTERS) + r'\-]+)(\|[\w' + re.escape(SPECIAL_CHARACTERS) + r'\-]+)?\s*\]\]'

    SPECIAL_CHARACTERS_1 = get_special_characters()
    pattern_sections_1 = r'\[\[\s*([\w\s-]+)\s*#\s*([\w' + re.escape(SPECIAL_CHARACTERS_1) + r'\-]+)(\|[\w' + re.escape(SPECIAL_CHARACTERS_1) + r'\-]+)?\s*\]\]'

    # Even more recent, from: https://chat.openai.com/c/25974e18-74d7-4d0f-a772-9c570c016c4b

    SPECIAL_CHARACTERS_2 =  get_special_characters()
    # pattern_sections_1 = r'\[\[\s*([^\[\]#]+)\s*#\s*([^\[\]|]+)(?:\|([^\[\]]+))?\s*\]\]'
    pattern_sections_1 = r'(?<!\!)\[\[\s*([^\[\]#]+)\s*#\s*([^\[\]|]+)(?:\|([^\[\]]+))?\s*\]\]'

    MATCHES = []
    for i, s in enum(S):
        
        # match_sections = re.findall(pattern_sections, s)
        match_sections_1 = re.findall(pattern_sections_1, s)
        match_blocks = re.findall(pattern_blocks, s)
        if len(match_sections_1) != 0 or len(match_blocks) != 0:
            MATCHES.append([i, match_sections_1, match_blocks])
    
    return MATCHES
# def external_links__identifier(S):
#     '''
#     Identifies external links in the document, in the form of '[[notename^linkname|name of reference]]'
#     '''

def unfold_all_embedded_notes(S, PARS):
    
    """
    Unfolds the content of all embedded notes (Like when it is written in the form: "![[note#section]] or ![[note^block]]")
    """
    md__files_embedded_prev0 = []
    md__files_embedded_prev = md__files_embedded_prev0.copy()

    lambda__unfold_embedded_notes = lambda x, y: unfold_embedded_notes(x, y, PARS, mode='normal')

    [S, md__files_embedded_new] = lambda__unfold_embedded_notes(S, md__files_embedded_prev)

    CND__LIST_OF_EMBEDDED_NOTES_IS_CHANGING = md__files_embedded_prev0 != md__files_embedded_new

    # unfold notes until there is nothing to unfold (loop is needed because there is "depth" in the embedded notes)
    while CND__LIST_OF_EMBEDDED_NOTES_IS_CHANGING:
        md__files_embedded_prev0 = md__files_embedded_new.copy()
        md__files_embedded_prev = md__files_embedded_prev0.copy()

        [S, md__files_embedded_new] = lambda__unfold_embedded_notes(S, md__files_embedded_prev)
        # Convert bullet and numbered lists
        # S = bullet_list_converter(S)

        CND__LIST_OF_EMBEDDED_NOTES_IS_CHANGING = md__files_embedded_prev0 != md__files_embedded_new

    return S, md__files_embedded_new

def search_in_embedded_notes(S, PARS):

    # Get all embedded references
    [_, md__files_embedded_new] = unfold_all_embedded_notes(S, PARS)

def char_replacement_sections(section):
    section_character_replacements = [':']
    for repl in section_character_replacements:
        section = section.replace(repl, "")

    return section

def internal_links__enforcer(S, sections_blocks, internal_links, options):

    '''
    Converts the Obsidian internal links to Latex internal links
    '''

    ADD_HYPERTARGET_AT_THE_END_OF_BLOCK = True

    type_of_link = ['sec:', '']
    type_ref = ['section', 'block']

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
            is_section_block = iS==0
            is_internal_ref_block = iS==1
            Ii_sb = I[iS+1]

            if len(Ii_sb) != 0:
                
                line_number = I[0]
                for Ii_sb_i in Ii_sb:
                    section_i = Ii_sb_i[1]
                    
                    idx = [j for j in range(len(sections_blocks[iS])) if char_replacement_sections(sections_blocks[iS][j][1]) == section_i] # index of the section in the section list
                    found_section = len(idx)>0
                    if found_section: 
                        
                        # Found match between existing sections and blocks of the file and the referenced section. 
                        # If there are many sections with the same name, the second (third, and so on) will just be ignored
                        idx=idx[0]

                        label_latex_format = type_of_link[iS] + section_i.replace(' ', '-')
                        hyperref_text = Ii_sb_i[-1].replace('|', '')

                        latex_cmd = '\hypertarget' if type_of_link[iS]!='sec:' else '\label'
                        label_of_source = f'{latex_cmd}{{{label_latex_format}}}'

                        hyperref_text = '{' + hyperref_text + '}' if len(hyperref_text) != 0 else '{' + 'ADD\\_NAME' + '}'
                            
                        has_already_been_replaced = label_of_source.strip() in S[sections_blocks[iS][idx][0]]
                        if not has_already_been_replaced:
                            # Has not already been replaced

                            label__in_line = S[sections_blocks[iS][idx][0]].replace('\n', '')
                            add__S_repl = ' \label{' + type_of_link[iS] + section_i.replace(' ', '-') + '}'

                            # Perform replacements on the label
                            if is_section_block:
                                S[sections_blocks[iS][idx][0]] = label__in_line + add__S_repl
                            else:
                                S[sections_blocks[iS][idx][0]] = label__in_line.replace('^' + label_latex_format, '') + add__S_repl

                        cnd__use_hyperref = (label_latex_format.startswith("sec:")) or (is_section_block)
                        cnd__use_hyperhyperlink = (is_internal_ref_block) and (not (cnd__use_hyperref))

                        if cnd__use_hyperref:
                            hyperref = f'\hyperref[{label_latex_format}]{hyperref_text}'
                            if options['add_section_number_after_referencing']:
                                hyperref += f" (\\autoref{{{label_latex_format}}})"
                        elif cnd__use_hyperhyperlink:
                            # for blocks, better write "hyperlink"
                            hyperref = f'\hyperlink{{{label_latex_format}}}{hyperref_text}'
                        else:
                            raise NotImplementedError
                        
                        obsidian_hyperref = write_link_in_obsidian_format(Ii_sb_i, type_ref[iS])
                        S[line_number] = S[line_number].replace(obsidian_hyperref, hyperref)
                        
                    else:
                        # did not find anything, therefore leaving the name only

                        link_name = Ii_sb_i[2].replace('|', "")
                        if len(link_name)>0:
                            if is_section_block:
                                type_of_link_write = 'section'
                            else:
                                type_of_link_write = 'block'
                            text_to_replace = write_link_in_obsidian_format(Ii_sb_i, type_of_link_write)
                            S[line_number] = S[line_number].replace(text_to_replace, link_name)
                        
    return S

def embedded_references_recognizer(S, options, mode):

    # BUG2: SOMEHOW THE "SPECIAL_CHARACTERS" VARIABLE IS NOT GLOBALLY CORRECT. CHANGES IN THE GLOBAL VARIABLE NOT APPLIED IN THE FUNCTION, THEREFORE WRITING IT HERE FOR NOW
    SPECIAL_CHARACTERS = get_special_characters()

    # repeated conditions
    cnd__mode_is__normal                = mode=='normal'

    all_chars = '\w' + SPECIAL_CHARACTERS + '\-'
    if not isinstance(S, list):
        raise Exception('Input of the function must be a list of strings!')
        return np.nan

    pattern_embedded_with_section_0 = '!\[\[([\.'+all_chars+']+)(\#['+all_chars+']+)?(\|[' + all_chars + ']+)?\]\]'

    # Pattern recognizing text starting with "[[eq__block"
    pattern_eq_block = r'\[\[eq__block.*'

    discard_special_cases = (cnd__mode_is__normal) and options['treat_equation_blocks_separately']
    pattern_embedded_with_section = pattern_embedded_with_section_0
    

    # The following commented if clause was commented because both me and ChatGPT can't find a proper regex expression
    # Replaced that with a dirty patch starting from `if discard_special_cases:`
    # if cnd__mode_is__normal: 

    #     if not options['treat_equation_blocks_separately']:
    #         pattern_embedded_with_section = pattern_embedded_with_section_0
    #     else:

    #         # Adjusted regex pattern to exclude strings containing "[[eq__block and any other character]]"
    #         # pattern_embedded_with_section = '!(?!\[\[eq__block).*\[\[([\.'+all_chars+']+)(\#['+all_chars+']+)?(\|[' + all_chars + ']+)?\]\]'

    #         pattern_embedded_with_section = '!(?!\[\[eq__block)(?!\[\[figure__block).*\[\[([\.' + all_chars + ']+)(\#[' + all_chars + ']+)?(\|[' + all_chars + ']+)?\]\]'

    
    # elif cnd__mode_is__equation_blocks_only or cnd__mode_is__figure_blocks_only:
    #     # Combined pattern
    #     pattern_embedded_with_section = pattern_embedded_with_section_0

    #     # The following pattern doesn't work:
    #     # pattern_embedded_with_section = r'!\[\[(eq__block[^\[\]\|]+)(#[^\[\]\|]+)?(\|[^\[\]\|]+)?\]\]' 
    #     # output = [('eq__block_single__23#expr', '', '')]
    #     # desired_output = [('eq__block_single__23', '#expr', '')]
    #     # ChatGPT cannot correct it! 
    #     # Therefore, I am making a patch

    # else:
    #     raise Exception('Nothing coded for this case!')

    MATCHES = []
    for i, s in enum(S):
        match_pattern_embedded = re.findall(pattern_embedded_with_section, s)
        
        # adding a dirty patch, cause both me and ChatGPT can't find a proper regex expression
        if not "![[" in s: match_pattern_embedded = []
    
        # adding a dirty patch, cause both me and ChatGPT can't find a proper regex expression
        if discard_special_cases:
            match_pattern_embedded_tmp = []
            if len(match_pattern_embedded) != 0:
                for m in match_pattern_embedded:
                    for sp in special_cases:
                        is_not_special_case = True
                        if m[0].startswith(sp):
                            is_not_special_case = False
                            break
                        
                    if is_not_special_case: match_pattern_embedded_tmp.append(m)

            match_pattern_embedded = match_pattern_embedded_tmp

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

    '''
    ⚠ Note that this does not pertain to internal links with sections!
    '''

    # BUG2: SOMEHOW THE "SPECIAL_CHARACTERS" VARIABLE IS NOT GLOBALLY CORRECT. CHANGES IN THE GLOBAL VARIABLE NOT APPLIED IN THE FUNCTION, THEREFORE WRITING IT HERE FOR NOW
    SPECIAL_CHARACTERS = get_special_characters()

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

    """
    Converts citation style according to the following example:

    Obsidian Text: "In [[p23]], the authors mention that ..."
    Latex Text:    "In \cite{p23}, the authors mention that ..."
    """

    pattern = r'\[\[p(\d+)\]\]'  # Updated regular expression pattern with capturing group
    replaced_string = re.sub(pattern, r'\\cite{p\1}', s)
    return replaced_string


def non_embedded_references_converter(S, PARS):

    links = non_embedded_references_recognizer(S)
    options = PARS['⚙']['EMBEDDED REFERENCES']
    formatting_rules = PARS['⚙']['formatting_rules']['non_embedded_references']
    

    if options['treat_citations']:
        # change citations, like: "[[p110]]" to "\cite{p110}"
        for i, s in enum(S):
            S[i] = replace_obsidian_bibliography_link_with_cite(s)

    formatting_rules_keys = formatting_rules.keys()
    
    formatting_rules_to_check = ['notes_with_tags']

    for link in links:
        line = link[0]  
        for link1 in link[1]:
            tmp1 = link1
            note_name = tmp1[0]
            if len(tmp1[2]) == 0:
                text_to_replace = f'[[{note_name}]]'
                replacement_text = note_name
            else:
                text_to_replace = f'[[{note_name+tmp1[2]}]]'
                replacement_text = tmp1[2][1:]

            f = formatting_rules_to_check[0]
            if f in formatting_rules_keys:
                note_path = get_embedded_reference_path(note_name, PARS, search_in = 'vault')
                formatting_notes = formatting_rules[f]
                replacement_text = formatting_rule__notes_with_tags(note_path, replacement_text, formatting_notes)
                        
            S[line] = S[line].replace(text_to_replace, replacement_text)

    return S

def search_note_for_tag(note_path, tag):
    
    with open(note_path, 'r', encoding='utf8') as f: Lines = f.readlines()
    for line in Lines: 
        if tag in line:
            return True
        
    return False

def formatting_rule__notes_with_tags(note_path, initial_text, formatting_parameters):
    
    for format in formatting_parameters:
        it_has_the_tag = search_note_for_tag(note_path, format[0])
        if it_has_the_tag:
            color = format[1]
            return f'\\textcolor{{{color}}}{{{initial_text}}}'

    return initial_text

def content_filter_2_name_latex_command(s, x, mref):
    if not is_part_of_list(s):
        return ['\n% Start obsidian ref:\n\t%' + mref.replace("![[", "").replace("]]", "").replace("#", "\##")] + ['\n'] + x + ['\n% End obsidian ref\n']
    else:
        return x

def content_filter_inline_code_snippets(S, note_path):
    S1 = []
    for s in S:
        if '`=this.file.cday' in s:
            s = s.replace('`=this.file.cday`', get_file_cday(note_path))
        S1.append(s)
    return S1

def unfold_embedded_notes(S, md__files_embedded, PARS, mode='normal'):
    
    '''
    Unfolds the content of embedded notes in the given list of notes.

    ---------
    Arguments
    ---------

        1. S (List): the content of the note (including so-far conversions)
        2. md__files_embedded(List): a list that contains all embedded references. It is needed to ensure that we do not reach an infinite loop of unfolding notes

    '''

    mode__collection_of_new_content = 'LISTS' # 'LISTS' or 'ELEMENTWISE'

    # repeated conditions
    cnd__mode_is__normal                = mode=='normal'
    cnd__mode_is__equation_blocks_only  = mode=='equation_blocks_only'
    cnd__mode_is__figure_blocks_only    = mode=='figure_blocks_only'
    cnd__mode_is__table_blocks_only     = mode=='table_blocks_only'
    
    if cnd__mode_is__normal:
        where_to_search_for_embedded_notes = 'vault'
    elif cnd__mode_is__equation_blocks_only:
        where_to_search_for_embedded_notes = 'equation_blocks'
    elif cnd__mode_is__figure_blocks_only:
        where_to_search_for_embedded_notes = 'figure_blocks'
    elif cnd__mode_is__table_blocks_only:
        where_to_search_for_embedded_notes = 'table_blocks'
    else:
        raise NotImplementedError

    is_in_normal_case =\
            (not cnd__mode_is__equation_blocks_only) and\
            (not cnd__mode_is__figure_blocks_only) and\
            (not cnd__mode_is__table_blocks_only)

    if not isinstance(md__files_embedded, list):
        raise Exception('md__files_embedded variable must be of type list!')

    if mode__collection_of_new_content == 'LISTS':
        LISTS_S = []

    file_types = ['.png', '.pdf', '.jpg']
    PARS_EMBEDDED_REFS = PARS['⚙']['EMBEDDED REFERENCES']
    all_embedded_refs = embedded_references_recognizer(S, PARS_EMBEDDED_REFS, mode)


    if PARS_EMBEDDED_REFS['adapt_section_hierarchy']:
        content_filter_1 = lambda x, Lines, lNum: change_section_hierarchy(x, Lines, lNum)
    else:
        content_filter_1 = lambda x, Lines, lNum: (x)

    if PARS_EMBEDDED_REFS['write_obsidian_ref_name_on_latex_comment']:    
        content_filter_2 = lambda s, x, mref: content_filter_2_name_latex_command(s, x, mref)
    else:
        content_filter_2 = lambda s, x, mref: (x)

    line_numbers_unfolded_notes = [ln[0] for ln in all_embedded_refs]

    for embedded_ref_info in all_embedded_refs:
        line_number = embedded_ref_info[0]
        line_embed = embedded_ref_info[1]             
        embedded_ref = line_embed[0][0]
        section = line_embed[0][1]
        markdown_ref = write_link_in_obsidian_format([embedded_ref, section, line_embed[0][2]], 'section', is_embedded=True)
        has_extension = False
        for file_type in file_types:
            if file_type in embedded_ref:
                has_extension = True
                break

        if not has_extension: 
            # means that it is a .md file, which we need to unfold
            # BUG_2 (line below): the following condition has the problem: 
            # if there's multiple times that the embedded_ref appears, but with a different section/block, then it will be ignored! 
            # We can use CONDITION_2, that allows all embedded notes to be inserted, with the risk of allowing infinite loops
            # To solve that, we could track the "parent" of an embedded reference
            CONDITION_1 = not embedded_ref in md__files_embedded
            CONDITION_2 = True
            if CONDITION_2:
                # Unfold this note ONLY when it hasn't already been unfolded
                
                md__files_embedded.append(embedded_ref)

                try:
                    path_embedded_reference = get_embedded_reference_path(embedded_ref, PARS, search_in=where_to_search_for_embedded_notes)
                except:
                    raise Exception("Error")

                if len(path_embedded_reference) == 0: raise Exception(f'File: {embedded_ref} cannot be found in {PARS["📁"][where_to_search_for_embedded_notes]}')

                section_name = section.lstrip('#')
                content__unfold = extract_section_from_file(path_embedded_reference, section_name)
                content__unfold = content_filter_1(content__unfold, S, line_number)
                content__unfold = content_filter_inline_code_snippets(content__unfold, path_embedded_reference)
                    
                if is_in_normal_case:
                    # since we don't expect to have comments in the single block (code optimization)
                    content__unfold = remove_markdown_comments(content__unfold)
                else:
                    if cnd__mode_is__equation_blocks_only:                  
                        # ➕ there is an unclear method here: 
                        # for now I am using the `cnd__mode_is__equation_blocks_only` for anything that is a specific block (equations, figures, tables)
                        # will correct in the future                       
                        if embedded_ref.startswith('eq__block'):
                            content__unfold = EQUATIONS__prepare_label_in_initial_Obsidian_equation(content__unfold, embedded_ref)
                        elif embedded_ref.startswith('figure__block'):
                            content__unfold = FIGURES__get_figure(content__unfold, embedded_ref, path_embedded_reference, PARS)
                        elif embedded_ref.startswith('table__block'):
                            content__unfold = TABLES__get_table(content__unfold, embedded_ref, path_embedded_reference, PARS)
                        else:
                            content__unfold = ''
                    elif cnd__mode_is__figure_blocks_only: 
                        raise NotImplementedError
                    else:
                        raise NotImplementedError
                
                if len(content__unfold) > 0: 
                    content__unfold = content_filter_2(S[line_number], content__unfold, markdown_ref)
                    
                # S[line_number] = get_unfolded_and_converted_embedded_content(embedded_ref, where_to_search_for_embedded_notes, line_number, is_in_normal_case, cnd__mode_is__equation_blocks_only, content_filter_2, PARS)

                S[line_number] = S[line_number].replace(markdown_ref, ''.join(content__unfold))

    if not cnd__mode_is__normal:
        S = get_list_of_separate_string_lines(S)
    else:
        if mode__collection_of_new_content == "LISTS":
            # we perform this, since the bullet_list_converter function would not work if the bullet points don't appear in new lines (list elements)
            z = 0
            S1 = []
            for i in line_numbers_unfolded_notes:
                S1.append(S[z:i] + S[i].split('\n'))
                z=i+1
            
            S1.append(S[z:])
            S2 = []
            for s in S1: S2+=s

            S = S2
    return S, md__files_embedded

def get_unfolded_and_converted_embedded_content(embedded_ref, where_to_search_for_embedded_notes, is_in_normal_case, cnd__mode_is__equation_blocks_only, PARS):
    
    embedded_ref = embedded_ref.replace('[[', '').replace(']]', '')
    
    try:
        path_embedded_reference = get_embedded_reference_path(embedded_ref, PARS, search_in=where_to_search_for_embedded_notes)
    except:
        raise Exception("Error")

    if len(path_embedded_reference) == 0: raise Exception(f'File: {embedded_ref} cannot be found in {PARS["📁"][where_to_search_for_embedded_notes]}')

    section = ''
    content_filter_1 = lambda x, Lines, lNum: (x)
    content_filter_2 = lambda s, x, mref: (x)
    section_name = section.lstrip('#')
    content__unfold = extract_section_from_file(path_embedded_reference, section_name)
    content__unfold = content_filter_1(content__unfold, '', '')
        
    if is_in_normal_case:
        # since we don't expect to have comments in the single block (code optimization)
        content__unfold = remove_markdown_comments(content__unfold)
    else:
        if cnd__mode_is__equation_blocks_only:                  
            # ➕ there is an unclear method here: 
            # for now I am using the `cnd__mode_is__equation_blocks_only` for anything that is a specific block (equations, figures, tables)
            # will correct in the future                       
            if embedded_ref.startswith('eq__block'):
                content__unfold = EQUATIONS__prepare_label_in_initial_Obsidian_equation(content__unfold, embedded_ref)
            elif embedded_ref.startswith('figure__block'):
                content__unfold = FIGURES__get_figure(content__unfold, embedded_ref, path_embedded_reference, PARS)
            elif embedded_ref.startswith('table__block'):
                content__unfold = TABLES__get_table(content__unfold, embedded_ref, path_embedded_reference, PARS)
            else:
                content__unfold = ''
        else:
            raise NotImplementedError

    return content__unfold


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
            if section_i[1] <= level:
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

    with open(obsidian_file, 'r', encoding='utf8') as f: Lines = f.readlines()
    return get_hierarcy_from_lines(Lines), Lines

def get_hierarcy_from_lines(Lines):
    comment_pattern = r'^\s*#+\s*%%.*%%.*$'  # Pattern to detect commented titles

    sections = []
    for iL, ln_f in enumerate(Lines):
        has_section = extract_section_from_line(ln_f)
        #is_commented_title = re.match(comment_pattern, ln_f)

        if has_section: # and not is_commented_title:
            has_section = has_section[0]
            section_hierarchy = len(has_section)
            
            # set section hierarchy to zero, if we are in the Appendix
            if ln_f.startswith('# Appendix'): section_hierarchy = 0
            
            tmp_l = ln_f.replace(has_section, '').replace('\n', '').rstrip().lstrip()
            section_i = [iL, section_hierarchy, tmp_l]

            sections.append(section_i)

    return sections

def change_section_hierarchy(content__unfold, S, line_number):

    # get file hierarchy of how lines are right now
    secs = get_hierarcy_from_lines(S)
    try:
        idx = [i for i, j in enumerate(secs) if j[0]<line_number][-1]
    except:
        return content__unfold

    level = secs[idx][1]
    content__unfold_modified = []

    for c in content__unfold:
        has_section = extract_section_from_line(c)
        if has_section:
            has_section[0] = has_section[0].strip()
            previous_level = len(has_section[0])
            c1 = has_section[0] + level*'#' + ' ' + c[previous_level:].lstrip()
        else:
            c1 = c

        content__unfold_modified.append(c1)

    return content__unfold_modified

def extract_section_from_line(line):
    return re.findall(r'^#+\s+', line)
