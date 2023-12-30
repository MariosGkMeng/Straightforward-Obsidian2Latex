# Straightforward-Obsidian2Latex
An Obsidian to Latex translator that is straightforward to use and has no 🐂💩 unnecessary complexity as an end result.

It is the most complete that I have seen among existing ones, since it offers more niche functionalities, such as:
- Correct table conversion
- Unfolding content of embedded notes (other packages I have seen just keep the "![[embedded_note]]" in the final text, when in reality the content of that note should appear in the LateX file)

# 💪 What it can convert (new capabilities regularly added)

- [X] Tables
  - Long tables (tables that can expand to more than 1 pages)
  - Non-long tables
- [X] Internal links (sections and blocks)
- [X] External links
- [X] Sections and subsections
  - [X] Maintain proper hierarchy of sections of the main note when a note with sections is embedded
- [X] Image display (however not yet with desirable placement)
- [X] Bullet lists
- [X] Numbered lists
- [X] Embedded notes
- [X] Equations (although the equations in Obsidian are exactly the same as in Latex)
  - [X] Numbered equations
- [X] Discard of text that is inside comments
- [X] Bold font
- [X] Highlighted font
- [X] Removal of Obsidian Comments
- [X] Specific parts of embedded notes (e.g. if the embedded note is "![[note_name# Some note section]]", the script would still paste the entire content of that note)
- [X] Convertion of codeblocks


# 👨‍💻🚧 What it cannot convert (so far)
## Frequently used functionalities

- [ ] (under dev.) Desirable placement for images
- [ ] Bibliography
- [ ] Italic font
- [ ] Regarding Internal links: add page number next to the cross-reference, in case the document is printed
- [ ] Remove link formatting from external links
  - [ ] Add setting for the user to choose if (s)he wishes to print the external .md file reference in a .pdf and create a hyperlink to that .pdf
- [ ] EMOJIS: Latex does not include emojis. Therefore, so far they are replaced by text, however in the future I am considering to convert them to small pictures

## Niche/rarely encountered functionalities
- [X] Discard text inside comments **after** start of a (sub)section
- [ ] Properly convert results from querying commands in Obsidian. This will probably never be achieved with this converter, since it requires to have access to the obsidian dataview and dataviewjs outputs.
- [ ] Convert anything that has to do with dataview, dataviewjs and inline queries


# How to use
## Prerequisites
1. Have Python 3 installed
2. Have Jupyter notebook editor installed (e.g. in Visual Studio Code)
3. Have Obsidian installed
4. Install the following Obsidian plugins
	1. Optional: QuickAdd (for quick insert of equation blocks)

## Usage
Go to the jupyter notebook. 

For each user-defined parameter, go to the "PARAMETERS" section, wherein the 'PARS' dictionary is located.

To set the paths for the .md file to be converted, change the `PARS['📂']['markdown-file']` and `PARS['📂']['tex-file']`.
Then, just run the code block under the section "Rest of code" and VOILA!


### Adding equations
Due to the inherent difficulty of equation numbering in Obsidian (read this [thread](https://forum.obsidian.md/t/automatic-equation-numbering-latex-math/1325) for details), there is no direct way to number and refer to the equations in Obsidian.

The workaround that I have used consists of the following simple steps:

1. Create a separate note wherein only the equation is to be added. The note has to obey a few formatting rules (see ?)



#### Formatting rules of the equation note

1. Name: The equations are to be labeled based on the **name** of the note. Therefore, for the code to be able to recognize them easily, I have created a name-based rule. If you wish to name the equation "conversion_law", then the name of the note should be "eq__block_conversion_law". Then, when in your document you refer to this equation, you can simply write "in equation \[\[eq\_\_block\_conversion\_law\]\]", and the final latex text would be "in equation \ref{conversion_law}".
2. Structure: The note has to **only have that equation inside, and nothing else!**. It is recommended that you start with a section "# \%\% expr \%\%" and then add the equation, such that you can embed it like \!\[\[eq\_\_block\_conversion\_law#expr\]\]. That way, the title of the note is not visible, making the obsidian file more readable.
3. Path: use a path of your choosing to put those equations. The reason for this is that in case you have a large vault, the code would have to search for the path of that note within the entire vault. Specifying a path for the equation blocks saves time.


##### Automating the creation of that note based on the formatting rules
Those steps above would normally require manual work, which would be annoying.

A way to automatically create an equation-note with the right format, in the right folder is to use the **QUICKADD** community plugin.

📽 The videos below illustrate how it creates those automatic equation notes, reference them, and how it looks in LateX.

https://github.com/MariosGkMeng/Straightforward-Obsidian2Latex/assets/61937432/178bbe0f-b04c-43a0-a3d3-a6efebd6b9df



https://github.com/MariosGkMeng/Straightforward-Obsidian2Latex/assets/61937432/2afa177d-9252-4ab5-9ab4-92d7e668af9a


