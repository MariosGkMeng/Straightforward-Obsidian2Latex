%%
# ℹ Instructions
- in the "convert_note" field, link the note you wish to convert (only one note)
- in the "code_run" field, set the paths of the python script and the .bat file accordingly
- in the "files" field, set the paths accordingly

## Things that can create errors
### Package irregularities

![[table__block_latex_packages_that_should_not_be_combined#table]]


# Previous jobs
Can save previously converted notes here
%%
convert_note:: [[example_writing]]
--

---

code_run:: [1. 👨‍💻🖱convert](<file:///C:\Users\mariosg\OneDrive - NTNU\FILES\workTips\Literature\Straightforward-Obsidian2Latex\converter.py>) , [2. 👨‍💻compile to .pdf](<file:///C:\Users\mariosg\OneDrive - NTNU\FILES\workTips\✍Writing\compile_and_open.sh>)
--


---


files:: [📁tex file](<file:///C:\Users\mariosg\OneDrive - NTNU\FILES\workTips\✍Writing\texFile.tex>), [📁.pdf file](<file:///C:\Users\mariosg\OneDrive - NTNU\FILES\workTips\✍Writing\pdfFile.pdf>) 
--


%%

```bash
@echo off
setlocal enabledelayedexpansion

:: Set base path and file name
set "BASE_PATH=C:\Users\mariosg\OneDrive - NTNU\FILES\workTips\✍Writing"
set "FILE_NAME=✍⌛writing--PHEN--Mathematical Phenomena of Neural Networks"
set "TEXFILE=%BASE_PATH%\%FILE_NAME%.tex"
set "PDFFILE=%BASE_PATH%\%FILE_NAME%.pdf"

:: Print paths for debugging
echo TEXFILE: %TEXFILE%
echo PDFFILE: %PDFFILE%

:: Compile the LaTeX file
pdflatex -interaction=nonstopmode -shell-escape "%TEXFILE%"
if errorlevel 1 (
    echo pdflatex compilation failed.
    exit /b 1
)

:: Open the resulting PDF file
start "" "%PDFFILE%"
```

%%