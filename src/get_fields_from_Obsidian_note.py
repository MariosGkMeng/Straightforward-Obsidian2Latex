def get_fields_from_Obsidian_note(path_embedded_reference, look_for_fields):
    
    fields = ['' for _ in look_for_fields]
    
    with open(path_embedded_reference, 'r', encoding='utf8') as file:
        lines = file.readlines()

    for i, field in enumerate(look_for_fields):
        fields[i] = []
        found_field = False
        for line in lines:
            if line.startswith(field):
                fields[i].append(line.replace(field, '').replace('\n', '').strip())
                found_field = True
                # break
        if not found_field:
            fields[i] = ''                
    return fields
