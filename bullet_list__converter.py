
def bullet_list_converter(S):

    S = ''.join(S)

    latex = ""
    lines = S.split("\n")
    indent = 0
    intent_list_type = []
    # tab_1 = " "*4
    tab_1 = "\t"
    Lt = len(tab_1)
    beg_item = "\\begin{itemize}\n"
    beg_enum = "\\begin{enumerate}\n"

    end_type = ["\\end{itemize}\n", "\\end{enumerate}\n"]

    first_itemize = False
    number_list = 1

    for line in lines:
        if line.startswith(tab_1* indent + "- ") or line.startswith(tab_1* indent + "* "):
            
            intent_list_type.append([indent, 0])
            if not first_itemize: 
                first_itemize = True
                list_closed = False
                beg_item_i = beg_item
                Li = 1
            else:
                beg_item_i = ""
                Li = 1
            latex += tab_1* (indent)*(len(beg_item_i)>0) + beg_item_i +  tab_1* (indent+1) + "\\item " + line[2 + indent*Lt:].strip() + "\n"
        elif line.startswith(tab_1* (indent + 1) + "- ") or line.startswith(tab_1* (indent + 1) + "* "):
            latex += tab_1 * (indent+1) + beg_item
            indent += 1
            intent_list_type.append([indent, 0])
            latex += tab_1 * (indent+1) + "\\item " + line[2 + (indent+0)*Lt:].strip() + "\n"
        elif line.startswith(tab_1* (indent - 1) + "- ") or line.startswith(tab_1* (indent - 1) + "* ") and indent > 0:
            indent -= 1
            intent_list_type.append([indent, 0])
            latex += tab_1 * indent + "\\end{itemize}\n"
            latex += tab_1 * indent + "\\item " + line[2 + (indent-1)*Lt:].strip() + "\n"
        
        elif line.startswith(tab_1* (indent - 2) + "- ") or line.startswith(tab_1* (indent - 2) + "* ") and indent > 0:
            # UNDER DEV ---> need to close previous lists
            indent -= 2
            intent_list_type.append([indent, 0])
            latex += tab_1 * (indent-1) + "\\end{itemize}\n"
            latex += tab_1 * (indent-1) + "\\item " + line[2 + (indent-2)*Lt:].strip() + "\n"
        
        elif line.startswith(tab_1* (indent - 3) + "- ") or line.startswith(tab_1* (indent - 3) + "* ") and indent > 0:
            
            # UNDER DEV ---> need to close previous lists
            indent -= 3
            intent_list_type.append([indent, 0])
            latex += tab_1 * (indent-2) + "\\end{itemize}\n"
            latex += tab_1 * (indent-2) + "\\item " + line[2 + (indent-3)*Lt:].strip() + "\n"


        elif line.startswith(tab_1* indent + str(number_list) + ". "):
            intent_list_type.append([indent, 1])
            latex += tab_1* (indent) +  tab_1* (indent+1) + "\\item " + line[2 + indent*Lt:].strip() + "\n"
            number_list += 1
        
        elif line.startswith(tab_1* (indent+1) + str(number_list) + ". "):
            latex += tab_1 * (indent+1) + beg_enum
            indent += 1
            intent_list_type.append([indent, 1])
            latex += tab_1 * (indent+1) + "\\item " + line[2 + (indent+0)*Lt:].strip() + "\n"
            number_list += 1

        else:
            
            while (indent > -1) and first_itemize:
                
                latex += tab_1 * indent +  end_type[[xx[1] for xx in intent_list_type if xx[0]==indent][0]]  
                indent -= 1

            latex += line + "\n"
            first_itemize = False
            list_closed = True
            indent = 0
            number_list = 1
            intent_list_type = []


    if not list_closed: 
        # in case that the Lines end abruptly before getting the chance to close the list (rare)
        while (indent > -1) and first_itemize:
            
            latex += tab_1 * indent + end_type[intent_list_type[indent][0]]
            indent -= 1

    return latex.split("\n")
