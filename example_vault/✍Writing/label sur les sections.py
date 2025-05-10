import re

def create_latex_label(title):
    """Convert a section title to a valid LaTeX label"""
    # Remove special characters and lowercase
    label = re.sub(r'[^a-zA-Z0-9 ]', '', title).lower()
    # Replace spaces with hyphens
    label = re.sub(r' +', '-', label)
    return f"sec:{label}"

def process_latex_sections(content):
    """Add labels to all sections in LaTeX content"""
    # Pattern to match section commands with or without existing label
    section_pattern = re.compile(
        r'(\\(?:section|subsection|subsubsection|paragraph)\*?)\{([^}]*)\}'
        r'(?!.*\\label\{sec:[^}]*\})',  # Negative lookahead for existing label
        re.DOTALL
    )
    
    def add_label(match):
        command = match.group(1)
        title = match.group(2)
        label = create_latex_label(title)
        return f"{command}{{{title}}} \\label{{{label}}}"
    
    # Process only section commands without existing labels
    return section_pattern.sub(add_label, content)

# Example usage
if __name__ == "__main__":
    with open('example_writing.tex', 'r', encoding='utf-8') as f:
        content = f.read()

    processed_content = process_latex_sections(content)

    with open('example_writing.tex', 'w', encoding='utf-8') as f:
        f.write(processed_content)