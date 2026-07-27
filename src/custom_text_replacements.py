


def final_text_replacements(LATEX, markdown_file):
    
    
    
    if '✍⌛writing--THESIS--Paper-3' in markdown_file:
        LATEX_4 = []
        for line in LATEX:
            LATEX_4.append(line.replace('begin{figure}[H]', 'begin{figure}[htbp]'))
            
        LATEX = LATEX_4
        
        LATEX_4 = []
        for line in LATEX:
            LATEX_4.append(line.replace('\begin{subfigure}[b]{0.5', '\begin{subfigure}[t]{0.48'))

        LATEX = LATEX_4
        
        LATEX_4 = []
        for line in LATEX:
            LATEX_4.append(line.replace('{figure}[htbp]', '{figure}[h!tbp]'))

        LATEX = LATEX_4
        
        LATEX_4 = []
        for line in LATEX:
            LATEX_4.append(
                line.replace(
                    r'\nameref{alg:data-gen-modified}',
                    r'\hyperref[alg:data-gen-modified]{i.i.d. data sampling algorithm}'
                )
            )

        LATEX = LATEX_4

        LATEX_4 = []
        for line in LATEX:
            LATEX_4.append(
                line.replace(
                    r'\nameref{alg:data-gen-original}',
                    r'\hyperref[alg:data-gen-original]{block-based data sampling algorithm}'
                )
            )

        LATEX = LATEX_4


    return LATEX