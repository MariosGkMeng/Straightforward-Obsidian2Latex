import re

def symbol_replacement(S, PARS):
    
    SYMBOLS_TO_REPLACE = PARS['par']['symbols-to-replace']
    
    S_1 = []
    for s in S:
        s1 = s
        for symbol in SYMBOLS_TO_REPLACE:
            if symbol[2] == 1:
                s1 = s1.replace(symbol[0], symbol[1] + ' ')
            elif symbol[2] == 2:
                s1 = re.sub(symbol[0], symbol[1] + ' ', s1)
            else:
                raise Exception("Nothing coded for this case!")
        
        S_1.append(s1)

    return S_1
