from path_searching import *
from get_parameters import *
from pathlib import Path
import os


PARS = get_parameters()


with open(PARS['📁']['list_paths_notes'], 'r', encoding='utf8') as f:
    lines = f.readlines()
    
lines_file_exists = []
for line in lines:
    
    split_lines = line.split(':')
    if len(split_lines)!=3:
        print('deb')
    filepath = Path((':'.join(line.split(':')[1:])).strip())
    if not filepath.exists():
        continue
    lines_file_exists.append(line)
    

with open(PARS['📁']['list_paths_notes'], 'w', encoding='utf8') as f:
    f.writelines(lines_file_exists)
