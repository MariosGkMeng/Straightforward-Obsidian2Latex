import re

def internal_links__identifier(content, PARS):
    """
    Process internal links in content.
    
    Args:
        content (str): Content to process
        PARS (dict): Parameters
        
    Returns:
        str: Processed content
    """
    if not isinstance(content, str):
        raise TypeError("content must be a string")
        
    if not isinstance(PARS, dict):
        raise TypeError("PARS must be a dictionary")
        
    try:
        # Get link settings
        link_settings = PARS.get('⚙', {}).get('INTERNAL_LINKS', {})
        add_section_number = link_settings.get('add_section_number_after_referencing', False)
        
        # Find all internal links
        pattern = r'\[\[(.*?)\]\]'
        matches = re.finditer(pattern, content)
        
        for match in matches:
            link_text = match.group(1)
            try:
                # Process the link
                processed_link = process_internal_link(link_text, PARS, add_section_number)
                if processed_link:
                    content = content.replace(match.group(0), processed_link)
            except Exception as e:
                print(f"Warning: Could not process link '{link_text}': {e}")
                continue
                
        return content
        
    except Exception as e:
        print(f"Error processing internal links: {e}")
        return content

def process_internal_link(link_text, PARS, add_section_number):
    """
    Process a single internal link.
    
    Args:
        link_text (str): Link text to process
        PARS (dict): Parameters
        add_section_number (bool): Whether to add section numbers
        
    Returns:
        str: Processed link text
    """
    try:
        # Split link text and display text if present
        parts = link_text.split('|')
        ref = parts[0].strip()
        display = parts[1].strip() if len(parts) > 1 else ref
        
        # Create LaTeX link
        if add_section_number:
            return f"\\hyperref[{ref}]{{{display}}}: \\autoref{{{ref}}}"
        else:
            return f"\\hyperref[{ref}]{{{display}}}"
            
    except Exception as e:
        print(f"Error processing link '{link_text}': {e}")
        return None 