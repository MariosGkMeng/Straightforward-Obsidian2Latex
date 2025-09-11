import re


def escape_underscores_in_sections(text):
    """
    Escapes underscores in LaTeX section-related commands, preserving nested braces.
    
    Parameters:
        text (str): A single line of LaTeX code.
    
    Returns:
        str: Line with underscores escaped in section titles.
    """
    import re

    section_commands = ['section', 'subsection', 'subsubsection', 'paragraph', 'subparagraph']

    for command in section_commands:
        pattern = rf'(\\{command}\*?\s*)\{{'
        match = re.search(pattern, text)
        if match:
            start_idx = match.end()  # index after the opening brace
            brace_count = 1
            i = start_idx
            while i < len(text) and brace_count > 0:
                if text[i] == '{':
                    brace_count += 1
                elif text[i] == '}':
                    brace_count -= 1
                i += 1

            content = text[start_idx:i - 1]
            escaped_content = content.replace('_', r'\_')
            return text[:start_idx] + escaped_content + text[i - 1:]

    return text

    

import re

def symbol_replacement(S, SYMBOLS_TO_REPLACE, protect_note_blocks=False):
    S_1 = []

    for s in S:
        if protect_note_blocks:
            parts = []
            last_end = 0
            protected_pattern = re.compile(r'\[\[.*?\]\]')

            for match in protected_pattern.finditer(s):
                start, end = match.span()
                unprotected_text = s[last_end:start]

                # Apply replacements only on unprotected text
                for symbol in SYMBOLS_TO_REPLACE:
                    s2 = symbol[2]
                    if s2 == 0:
                        unprotected_text = unprotected_text.replace(symbol[0], symbol[1])
                    elif s2 == 1:
                        unprotected_text = unprotected_text.replace(symbol[0], symbol[1] + ' ')
                    elif s2 == 2:
                        unprotected_text = re.sub(symbol[0], symbol[1] + ' ', unprotected_text)
                    else:
                        raise Exception("Nothing coded for this case!")

                parts.append(unprotected_text)
                parts.append(s[start:end])  # Keep protected block as-is
                last_end = end

            # Handle any remaining unprotected text
            remaining_text = s[last_end:]
            for symbol in SYMBOLS_TO_REPLACE:
                s2 = symbol[2]
                if s2 == 0:
                    remaining_text = remaining_text.replace(symbol[0], symbol[1])
                elif s2 == 1:
                    remaining_text = remaining_text.replace(symbol[0], symbol[1] + ' ')
                elif s2 == 2:
                    remaining_text = re.sub(symbol[0], symbol[1] + ' ', remaining_text)
                else:
                    raise Exception("Nothing coded for this case!")
            parts.append(remaining_text)

            S_1.append("".join(parts))
        else:
            # Old behavior: replace everywhere
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
    Escapes underscores inside \texttt{...}, with better performance.
    Handles nested braces and only processes if \texttt{ is present.
    Prints original and modified text if 'add_explanation' is present.
    """
    if r'\texttt{' not in text:
        return text

    result = ''
    i = 0
    while True:
        start_idx = text.find(r'\texttt{', i)
        if start_idx == -1:
            result += text[i:]
            break

        # Add text before \texttt{
        result += text[i:start_idx]

        # Find matching closing brace
        brace_start = start_idx + len(r'\texttt{')
        brace_count = 1
        j = brace_start
        while j < len(text) and brace_count > 0:
            if text[j] == '{':
                brace_count += 1
            elif text[j] == '}':
                brace_count -= 1
            j += 1

        # Extract and escape
        inner = text[brace_start:j-1]
        escaped_inner = inner.replace('_', r'\_')
        result += r'\texttt{' + escaped_inner + '}'

        i = j  # continue from after the closing brace

    return result


def escape_underscores_in_texttt__old(text):
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


