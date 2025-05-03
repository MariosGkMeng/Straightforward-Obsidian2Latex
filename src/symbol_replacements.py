import re


def escape_underscores_in_sections(text):
    """
    Escapes underscores in section-related LaTeX commands such as \section, \subsection, etc.
    
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
            s2 = symbol[2]
            if s2 == 0:
                s1 = s1.replace(symbol[0], symbol[1])
            elif s2 == 1:
                s1 = s1.replace(symbol[0], symbol[1] + ' ')
            elif s2 == 2:
                s1 = re.sub(symbol[0], symbol[1] + ' ', s1)
            else:
                raise Exception("Nothing coded for this case!")
        
        S_1.append(s1)

    return S_1


def escape_underscores_in_texttt(text):
    """
    Replaces underscores with \_ inside the brackets of \texttt{}.

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
