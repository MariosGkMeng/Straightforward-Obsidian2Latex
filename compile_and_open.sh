#!/bin/bash
# This file compiles the latex file to .pdf

# Set base path and file name
BASE_PATH="C:/Users/mariosg/OneDrive - NTNU/FILES/workTips/✍Writing"
FILE_NAME="file_to_be_converted.md"
TEXFILE="$BASE_PATH/$FILE_NAME.tex"
PDFFILE="$BASE_PATH/$FILE_NAME.pdf"

# Print paths for debugging
echo "TEXFILE: $TEXFILE"
echo "PDFFILE: $PDFFILE"

# Compile the LaTeX file
pdflatex -interaction=nonstopmode -shell-escape "$TEXFILE"
if [ $? -ne 0 ]; then
    echo "pdflatex compilation failed."
    exit 1
fi

# Open the resulting PDF file
xdg-open "$PDFFILE"
