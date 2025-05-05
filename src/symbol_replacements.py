import re


def escape_underscores_in_sections(text):
    """
    Escapes underscores in section-related LaTeX commands such as \\section, \\subsection, etc.
    
    Parameters:
        text (str): A single line of LaTeX code.
    
    Returns:
        str: The line with underscores escaped if it's a section-related command.
    """
    # List of LaTeX sectioning commands to check
    section_commands = ['section', 'subsection', 'subsubsection', 'paragraph', 'subparagraph']
    
    for command in section_commands:
        # Match lines like \section{Some_text_here}
        pattern = rf'(\\{command}\*?\s*\{{)([^}}]*)(\}})'
        match = re.search(pattern, text)
        if match:
            before, content, after = match.groups()
            # Escape underscores in the content part
            escaped_content = content.replace('_', r'\_')
            return f"{before}{escaped_content}{after}"
    
    return text
    

def symbol_replacement(S, SYMBOLS_TO_REPLACE):
    
    S_1 = []
    for s in S:
        s1 = s
        for symbol in SYMBOLS_TO_REPLACE:
            obsidian_symbol, latex_replacement, replacement_type = symbol
            # Escape the replacement string for re.sub
            escaped_latex_replacement = re.escape(latex_replacement)
            
            if replacement_type == 0:
                # Simple string replacement, re.sub not strictly needed but used for consistency
                s1 = re.sub(re.escape(obsidian_symbol), escaped_latex_replacement, s1)
            elif replacement_type == 1:
                # Use re.sub with escaped replacement + space
                s1 = re.sub(re.escape(obsidian_symbol), escaped_latex_replacement + ' ', s1)
            elif replacement_type == 2:
                # Use re.sub with regex pattern for obsidian_symbol and escaped replacement + space
                # Note: This assumes obsidian_symbol is a valid regex pattern if type is 2
                s1 = re.sub(obsidian_symbol, escaped_latex_replacement + ' ', s1)
            else:
                raise Exception("Nothing coded for this case!")
        
        S_1.append(s1)

    return S_1


def escape_underscores_in_texttt(text):
    """
    Replaces underscores with \\_ inside the brackets of \texttt{}.

    Args:
        text (str): The input LaTeX string.

    Returns:
        str: The modified LaTeX string with escaped underscores inside \texttt{},
             or the original string if no match is found.
    """
    def replace_underscores(match):
        # Escape underscores in the matched text (inside \texttt{})
        return match.group(0).replace('_', r'\_')

    # Regex pattern to find \texttt{...}
    pattern = r'\\texttt\{.*?\}'
    
    # Replace underscores only within \texttt{...} if any matches exist
    replaced_text = re.sub(pattern, replace_underscores, text)
    
    return replaced_text
