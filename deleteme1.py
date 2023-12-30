import re


def get_file_hierarchy_old(obsidian_file):
    
    if not isinstance(obsidian_file, str):
        raise Exception('obsidian_file variable must be of type string, and specifically, a path!')

    f = open(obsidian_file, 'r', encoding='utf8')
    Lines = f.readlines()

    pattern_how_many_sections = r'^#+'
    # pattern_for_section = r'^#+\s.+$'

    sections = []
    for iL, ln_f in enumerate(Lines):
        # search_results = re.findall(pattern_for_section, ln_f)
        has_section = re.findall(pattern_how_many_sections, ln_f)

        if has_section:
            has_section = has_section[0]
            section_hierarchy = len(has_section)
            tmp_l = ln_f.replace(has_section, '').replace('%%', '').replace('\n', '').rstrip().lstrip()
            section_i = [iL, section_hierarchy, tmp_l]

            sections.append(section_i)

    f.close()

    return sections, Lines


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
        is_commented_title = re.match(comment_pattern, ln_f)

        if has_section and not is_commented_title:
            has_section = has_section[0]
            section_hierarchy = len(has_section)
            tmp_l = ln_f.replace(has_section, '').replace('\n', '').rstrip().lstrip()
            section_i = [iL, section_hierarchy, tmp_l]

            sections.append(section_i)

    f.close()

    return sections, Lines


obsidian_file = "C:\\Users\\mariosg\\OneDrive - NTNU\\FILES\\workTips\\✍Writing\\First working document.md"

print(get_file_hierarchy_old(obsidian_file)[0])
print(get_file_hierarchy(obsidian_file)[0])