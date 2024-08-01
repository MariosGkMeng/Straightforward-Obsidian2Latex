import re


def conv_dict(D):
    for key in D.keys():
        if D[key] == '🟢':
            D[key] = True
        elif D[key] == '🔴':
            D[key] = False
    return D

def enum(x):
    return enumerate(x)

def is_in_table_line(x):
    if x.startswith('|') and x.endswith('|'):
        return True
    else: 
        return False

def remove_markdown_comments(S):

    # UNDER DEVELOPMENT!!!

    comment_has_started = False
    line_number__of_comment_to_close = 0


    for i, s in enum(S):
        to_delete = []
        occurences = [x.start() for x in re.finditer(r'(?<!lcmd)%%(?!lcmd)', s)]
        L = len(occurences)
        if (L > 0):

            if comment_has_started:
                idx0 = occurences[0]+2
                text_in_comment = s[:idx0]
                to_delete.append(text_in_comment)
                

                for tmp in to_delete:
                    s = s.replace(tmp, '')
                    
                    
                occurences = [x.start() for x in re.finditer('%%', s)]
                L = len(occurences)
                comment_has_started = False
                
            if L % 2 == 0:
                to_delete = []
                for j in range(int(L/2)):
                    j2 = 2*j
                    idx0 = occurences[j2]+2
                    idx1 = occurences[j2+1]
                    text_in_comment = s[idx0:idx1]
                    to_delete.append('%%'+text_in_comment+'%% ') # ⚠WARNING-2: Bad programming (sloppy way to remove additional space)                                          
                    to_delete.append(' %%'+text_in_comment+'%% ')                                         
                    to_delete.append('%%'+text_in_comment+'%%')                     


                for tmp in to_delete:
                    s = s.replace(tmp, '')
                
                
                # comment_has_started = False

            else:
                comment_has_started = True
                to_delete = []

                s0 = s # need this, since in the following loop, len(s) changes, but the two lines after the loop operate based on the initial length
                if L>1:
                    for j in range(int((L-1)/2)):
                        j2 = 2*j
                        idx0 = occurences[j2]+2
                        idx1 = occurences[j2+1]
                        text_in_comment = s[idx0:idx1]
                        to_delete.append('%%'+text_in_comment+'%% ') # ⚠WARNING-2: Bad programming (sloppy way to remove additional space)                                          
                        to_delete.append(' %%'+text_in_comment+'%% ')                                         
                        to_delete.append('%%'+text_in_comment+'%%')                     

                else:
                    idx0 = occurences[0]+2
                    text_in_comment = s[idx0:]
                    to_delete.append('%%'+text_in_comment) # ⚠WARNING-2: Bad programming (sloppy way to remove additional space)                                          
                    to_delete.append(' %%'+text_in_comment)                                         
                    to_delete.append('%%'+text_in_comment)                     

                for tmp in to_delete:
                    s = s.replace(tmp, '')



                line_number__of_comment_to_close = i

                # if not comment_has_started: comment_has_started = True



        else:
            if comment_has_started:
                # need to clear entire line
                s = ''

    
        S[i] = s

    return S
