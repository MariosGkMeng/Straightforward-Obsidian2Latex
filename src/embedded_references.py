import re

def get_unfolded_and_converted_embedded_content(content, PARS, depth=0):
    """
    Get unfolded and converted embedded content.
    
    Args:
        content (str): Content to process
        PARS (dict): Parameters
        depth (int): Current recursion depth
        
    Returns:
        str: Processed content
    """
    # Check depth limit
    max_depth = PARS['⚙']['EMBEDDED REFERENCES'].get('max_depth', 10)
    if depth >= max_depth:
        print(f"Warning: Maximum recursion depth ({max_depth}) reached")
        return content
        
    try:
        # Find all embedded references
        pattern = r'!\[\[(.*?)\]\]'
        matches = re.finditer(pattern, content)
        
        for match in matches:
            ref = match.group(1)
            try:
                # Get referenced content
                ref_content = get_referenced_content(ref, PARS)
                if ref_content:
                    # Process the referenced content recursively
                    processed_ref = get_unfolded_and_converted_embedded_content(
                        ref_content, PARS, depth + 1
                    )
                    # Replace the reference with processed content
                    content = content.replace(match.group(0), processed_ref)
            except Exception as e:
                print(f"Warning: Could not process reference '{ref}': {e}")
                continue
                
        return content
        
    except Exception as e:
        print(f"Error processing content: {e}")
        return content 