import os

def count_calls(func):
    def wrapper(*args, **kwargs):
        wrapper.calls += 1
        # print(f"Function '{func.__name__}' has been called {wrapper.calls} times.")
        return func(*args, **kwargs)
    wrapper.calls = 0
    return wrapper

@count_calls
def search_embedded_reference_in_vault(u, PARS, search_in = 'vault'):

    '''
    Finds the paths of embedded references in the vault (by far the most time-consuming process)
    '''
    # global has_come_here_at_least_once
    files = []
    vault_path = PARS['📁'][search_in]
    os.chdir(vault_path)    
    
    if search_embedded_reference_in_vault.calls == 1: 
        search_embedded_reference_in_vault.calls = 0 # gotta reset the decorator count, cause jupyter notebook keeps the count from the previous run
        msg1 = "Searching within the vault for (⚠NOTE: Searching within the vault for a note takes time, but then this note will not have to be searched again!): "
        print(msg1)
        print('-'*len(msg1))
    
    print('\t' + u + '. ')
    # for root, dirs, files in os.walk(vault_path):
    #     if u in files: return os.path.join(root,u)
    u_lower = u.lower()
    for root, dirs, files in os.walk(vault_path):
        for file in files:
            if u_lower == file.lower():
                return os.path.join(root, file)

    
    return ''

def get_embedded_reference_path(fileName, PARS, search_in = 'vault'):

    '''
    Because searching within the vault takes quite a bit of time for large vaults, this function first
    searches in the textfile (PARS['📁']['list_paths_notes']) for the path. 
    If it does not exist, it uses the `search_embedded_reference_in_vault` function to find it in the vault.
    '''

    path_list_of_notes = PARS['📁']['list_paths_notes'] # search in that list first, and if the file doesn't exist, then search the entire vault (which is time-consuming)
    
    # Read the text file
    with open(path_list_of_notes, 'r', encoding='utf8') as file:
        lines = file.readlines()
    
    # Search for the fileName in the lines and retrieve associated paths
    fileName = fileName.strip().replace('.md', '')
    matching_paths = [line.strip() for line in lines if line.startswith(fileName+":")]


    found_extension_that_is_not_md = False
    extensions = ['.png', '.jpg', '.pdf']
    for extension in extensions:
        if fileName.endswith(extension):
            found_extension_that_is_not_md = True
            fileNameWithExtension = fileName
            break

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
        fileName = fileName.replace('/', '\\').strip()
        is_entire_path = '\\' in fileName
        if not is_entire_path:
            path_found = search_embedded_reference_in_vault(fileNameWithExtension, PARS, search_in='vault')
            if path_found: 
                update_list_of_embedded_note_paths(fileName, path_found, path_list_of_notes)
                return path_found
            else:
                raise Exception(f"No information found for '{fileName}' in the provided text file and unable to find an alternative path.")
        else:
            path_found = PARS['📁']['vault'] + fileName
            update_list_of_embedded_note_paths(fileName, path_found, path_list_of_notes)
            return path_found
        
def update_list_of_embedded_note_paths(filename, path, path_list_of_notes):
    with open(path_list_of_notes, 'a', encoding='utf-8') as file:
        # update path_list_of_notes for the next time
        file.write(f"{filename}: {path}\n")
        # print(f"Path for '{fileName}' appended as a new line in the text file.")
