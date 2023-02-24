# Straightforward-Obsidian2Latex
An Obsidian to Latex translator that is straightforward to use and has no 🐂💩 unnecessary complexity as an end result.

# 💪 What it can convert (new capabilities to be appended soon)

- [X] Tables
  - Long tables (tables that can expand to more than 1 pages)
  - Non-long tables
- [X] Internal links
- [X] External links
- [X] Sections and subsections
- [X] Image display (however not yet with desirable placement)
- [X] Bullet lists (up to level 4 of indentation)
- [X] Numbered lists
- [X] Embedded notes (only for entire note content)
- [X] Equations (although the equations in Obsidian are exactly the same as in Latex)
- [X] Discard of text that is inside comments



# 👨‍💻🚧 What it cannot convert (so far)
## Frequently used functionalities

- [ ] (under dev.) Desirable placement for images
- [ ] Bibliography
- [ ] Equation numbering
- [ ] Bold font
- [ ] Italic font
- [ ] Bullet lists with indentation of level 5 and above
- [ ] Specific parts of embedded notes (e.g. if the embedded note is "![[note_name# Some note section]]", the script would still paste the entire content of that note)

## Niche/rarely encountered functionalities
- [ ] Discard text inside comments **after** start of a (sub)section


# How to use
## Prerequisites
1. Have Python 3 installed
2. Have Jupyter notebook editor installed (e.g. in Visual Studio Code)

## Usage
Go to the jupyter notebook. 

For each user-defined parameter, go to the "PARAMETERS" section, wherein the 'PARS' dictionary is located.

To set the paths for the .md file to be converted, change the `PARS['📂']['markdown-file']` and `PARS['📂']['tex-file']`.
Then, just run all code blocks and VOILA!
