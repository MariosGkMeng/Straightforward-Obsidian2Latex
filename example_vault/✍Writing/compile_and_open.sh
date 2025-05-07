#!/bin/bash
# This file compiles the latex file to .pdf

# Set base path and file name
BASE_PATH="c:/Users/dvrch/Desktop/Straightforward-Obsidian2Latex/Straightforward-Obsidian2Latex/example_vault/✍Writing"
FILE_NAME="example_writing"
TEXFILE="$BASE_PATH/$FILE_NAME.tex"
PDFFILE="$BASE_PATH/$FILE_NAME.pdf"

# # Print paths for debugging
# echo "TEXFILE: $TEXFILE"
# echo "PDFFILE: $PDFFILE"

# # Compile the LaTeX file
# pdflatex -interaction=nonstopmode -shell-escape "$TEXFILE"
# if [ $? -ne 0 ]; then
#     echo "pdflatex compilation failed."
#     exit 1
# fi

# # Open the resulting PDF file
# xdg-open "$PDFFILE"

# -------------------
# Change to the directory of the script
cd "$BASE_PATH"

# Replace \begin{tabularx} with \begin{tabularx}{1.0\textwidth}
sed -i "s/\\\\begin{tabularx}{p/\\\\begin{tabularx}{1.0\\\\textwidth}{p/g" "$TEXFILE"


# # Clean auxiliary files
rm -f "$FILE_NAME.aux" "$FILE_NAME.log" "$FILE_NAME.bbl" "$FILE_NAME.blg" "$FILE_NAME.toc"

# # Compile the bibliography
bibtex "$FILE_NAME.aux"
if [ $? -ne 0 ]; then
    echo "bibtex compilation failed. pdf OK, mais pas de bibliographie."
    exit 1
fi

# Compile the LaTeX file
# pdflatex -interaction=nonstopmode -shell-escape "$TEXFILE"
if [ $? -ne 0 ]; then
    echo "pdflatex compilation failed."
    exit 1
fi
#

# # Compile the LaTeX file again for references
pdflatex -interaction=nonstopmode -shell-escape "$TEXFILE"
pdflatex -interaction=nonstopmode -shell-escape "$TEXFILE"

# Open the resulting PDF file
# Use 'start' on Windows (Git Bash) and 'xdg-open' on Linux/macOS
if [[ "$OSTYPE" == "msys" ]]; then
  start "$PDFFILE"
else
  xdg-open "$PDFFILE"
fi