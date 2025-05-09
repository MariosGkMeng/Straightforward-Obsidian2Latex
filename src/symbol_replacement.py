import re

def symbol_replacement(content, PARS):
    """
    Replace symbols in content according to parameters.
    
    Args:
        content (str): Content to process
        PARS (dict): Parameters containing symbol replacements
        
    Returns:
        str: Processed content
    """
    if not isinstance(content, str):
        raise TypeError("content must be a string")
        
    if not isinstance(PARS, dict):
        raise TypeError("PARS must be a dictionary")
        
    try:
        symbols = PARS.get('par', {}).get('symbols-to-replace', [])
        if not isinstance(symbols, list):
            raise ValueError("symbols-to-replace must be a list")
            
        for obsidian_symbol, latex_symbol, replacement_type in symbols:
            if not isinstance(obsidian_symbol, str) or not isinstance(latex_symbol, str):
                continue
                
            if replacement_type == 1:
                content = content.replace(obsidian_symbol, latex_symbol)
            elif replacement_type == 2:
                pattern = re.escape(obsidian_symbol)
                content = re.sub(pattern, latex_symbol, content)
                
        return content
        
    except Exception as e:
        print(f"Error in symbol replacement: {e}")
        return content 