#!/bin/bash

# Set working directory to script location
cd "$(dirname "$0")"

# Run pdflatex with shell-escape for minted package and nonstopmode to continue on errors
pdflatex -interaction=nonstopmode -shell-escape example_writing.tex
bibtex example_writing
pdflatex -interaction=nonstopmode -shell-escape example_writing.tex
pdflatex -interaction=nonstopmode -shell-escape example_writing.tex

# Check if PDF was created
if [ -f "example_writing.pdf" ]; then
    echo "PDF generated successfully!"
    if [ "$(uname)" == "Darwin" ]; then
        open example_writing.pdf
    elif [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
        xdg-open example_writing.pdf
    fi
else
    echo "Error: PDF generation failed!"
    exit 1
fi
