# Comparisons to other converters
 (➕under construction)


|                                                                                                                                                                                                                                  | This repo | Pandoc Plugin                                  | Copy as Latex | Enhancing Export   |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- | ---------------------------------------------- | ------------- | ------------------ |
| Embedded notes                                                                                                                                                                                                                   | ✔         | ❌                                              | ❌             | not running for me |
| Equations                                                                                                                                                                                                                        | ✔         | ❌❓ --> maybe not, was not able to do it so far | ✔             | not running for me |
| [Equation referencing](#adding-equations)                                                                                                                                                                                                             | ✔         | ❌ (seems to not be working)                    | ❌             | not running for me |
| Is fast                                                                                                                                                                                                                          | ✔ \*      | ✔✔                                             | ✔✔            | not running for me |
| Ignores comments                                                                                                                                                                                                                 | ✔         | ✔                                              | ✔             | not running for me |
| [Converting inline dataview code](#new-converting-inline-dataview-code)                                                                                                                                                          | ✔         | ❌                                              | ❌             | not running for me |
| Dataview Table conversion                                                                                                                                                                                                        | ✔         | ❌                                              | ❌             | not running for me |
| Can add custom latex code for specific things                                                                                                                                                                                    | ✔         | ❓                                              | ❓             | not running for me |
| Can control the sizes and latex class types for figures and tables from Obsidian                                                                                                                                                 | ✔         | ❓                                              | ❓             | not running for me |
| [Can treat cases wherein the note to be converted is too complicated, resulting in severe RAM consumption](#for-when-the-note-to-be-converted-is-too-large-and-contains-many-embedded-notes-resulting-in-severe-ram-consumption) | ✔         | ❌                                              | ❌             | not running for me |
| Can convert [admonition blocks](https://notes.nicolevanderhoeven.com/Obsidian+Admonition)                                                                                                                                        | ✔         | ❓                                              | ❓             | not running for me |
| [Parameterization code that hides parts of the note programmatically](#new-parameterizing-whether-parts-in-the-document-will-appear-in-the-pdf-file)                                                                                                                                                                               | ✔         | ❓                                              | ❓             | not running for me |

\*Provided that the embedded notes are already mapped in `PARS['📁']['list_paths_notes']`, therefore the algorithm does not need to search in the vault for them. Also, conditional formatting takes some time, since the algorithm has to search inside every linked note for certain tags.

# 📽 General Video (under development)
General video showcasing all the functionalities (will be uploaded on YouTube. For now, you can view the video I've rendered so far [here](https://drive.google.com/file/d/1KK-r5KZQHdIEtGJf9gZzpQrIEesj6_GA/view?usp=sharing))


# To be added soon
- Guide on how the dataview tables are converted (also, include the example in the `example_vault`)
- More videos on the conversion
- General video showcasing all the functionalities (will be uploaded on YouTube. For now, you can view the video [here](https://drive.google.com/file/d/1KK-r5KZQHdIEtGJf9gZzpQrIEesj6_GA/view?usp=sharing))
- Relative path to the `converter.py` from `👨‍💻convert_to_latex.md`
- Make proper installer so that the user doesn't have to do manual work
	- QuickAdd commmads: make function that appends to the `QuickAdd/data.json`. Install automatically if needed
 - Occasional cleanup of `PARS['📂']['list_paths_notes']`

# Citing this work
Please cite the following if you use it for publishable work (i.e., if you write your paper in Obsidian, and use this code to print to Latex)
```
@misc{MariosGkionisObsidian2Latex,
  author = {Marios Gkionis},
  title = {Straightforward Obsidian to Latex},
  year = {2023},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/MariosGkMeng/Straightforward-Obsidian2Latex}},
}
```

# Quicker readthrough
- Skip the first section if you want to skip the "sales pitch"
- Start by doing: clone the repo, open Obsidian. In Obsidian, select "open folder as vault", and select the `example_vault` in the repo
	- Unzip the `obsidian.zip` file and rename the folder `.obsidian` (github doesn't allow folders that start with `.`). This action is needed, because the `.obsidian` folder I provided includes the community plugins that you need to use (mainly the QuickAdd plugin)
 - Make sure community plugins are activated in your vault
 - Open the `example_writing` note in Obsidian and check out the functionalities
 - Convert the note using the `👨‍💻convert_to_latex` note



# Straightforward-Obsidian2Latex

- Do you want to
	- write your documents entirely in Obsidian, and then print them to LateX (e.g., for scientific papers and lab reports)?
	- print pretty .pdf files from Obsidian, while maintaining all the links?

 
Are you annoyed by:
- How incomplete the "print to .pdf" command in Obsidian is?
- The fact that you have to write code, just to make a nice report/paper (though LateX is not very hard to use in Overleaf)?

  
Do you just want to be able to seamlessly write formal content in the same software as your notes, and print it from there, without the need to move to external software?
Or do you just want to write pretty scientific documents without needing to learn Latex at all (with the exception of the equation environment)?

This Obsidian to Latex translator is **complete**, straightforward to use, and has no 🐂💩 unnecessary complexity as an end result.

It is the most complete that I have seen among existing ones, since it offers more niche functionalities, such as:
- Correct table conversion
- Unfolding content of embedded notes (other packages I have seen just keep the "![[embedded_note]]" in the final text, when in reality the content of that note should appear in the LateX file)
- NEW: Conditional Formatting Rules
- Write proper installer, so that user does not have to create folders and copy files


## Why not use the already existing plugins for conversion?


**Yes**, plugins for Obsidian to Latex already exist, but they have [limitations](#comparisons-to-other-converters) that do not allow the user to write in Obsidian freely. **Yes**, I'd have loved to contribute to those projects, but I don't know Javascript and Typescript.

I consider LateX a very archaeic tool (Overleaf has come a long way and is quite comfortable to use), not suited for the intense knowledge-work of 2024. It is clunky, and forces the researcher to write code, when they just want to write about their work 😩
I want to see it not being used at all, but due to its legacy, I doubt it will happen any time soon. So, what we are left with is the need to translate content from proper tools (like Obsidian) to not-so-good old LateX. 

# 💪 What it can convert (new capabilities regularly added)

- [X] Tables
  - Long tables (tables that can expand to more than 1 pages)
  - Non-long tables
  - Special formatting for each table (different package, coloring of rows)
  - (NEW) Dataview table conversion!
- [X] Internal links (sections and blocks)
- [X] External links
- [X] Sections and subsections
  - [X] Maintain proper hierarchy of sections of the main note when a note with sections is embedded
- [X] Image/figure display with appropriate figure referencing, captions, and size in LateX
- [X] Bullet lists
- [X] Numbered lists
- [X] References/bibliography
	-  But so far only with my own referencing method
- [X] Embedded notes
	- Inluding section hierarchization (i.e., keeping track on what level of section the embedded note was, thus converting any sections inside it to subsections that adhere to the initial hierarchy
- [X] Equations (although the equations in Obsidian are exactly the same as in Latex)
  - [X] Numbered equations
- [X] Discard of text that is inside comments
- [X] Bold font
- [X] Highlighted font
- [X] Removal of Obsidian Comments
- [X] Specific parts of embedded notes (e.g. if the embedded note is "![[note_name# Some note section]]", the script would still paste the entire content of that note)
- [X] Convertion of codeblocks (including inline code)
- [X] Italic font
- [X] [Admonition](https://f5-rtd-howto.readthedocs.io/en/dev/resources/resources_rtd-admonitions.html) blocks (I use that quite frequently, because it is very pleasant for the eye)
- [X] Captions for figures (will use the note-block logic, as in the [Equation Referencing](#Adding-equations))
- [X] Figure size
- [X] Subplots
- [X] Conditional Formatting: colored text for notes that contain specific tag(s)
- [X] (**NEW**) Performing dataview inline code in the form: `= choice([[note]].field[0], [[note]].field[1], "")`. This enhances parameterization of the document.


# 👨‍💻🚧 What it cannot convert (so far)
## Frequently used functionalities

- [ ] Graphs with the latex plotting environment (won't be developing that soon, since most people use .pdf files for figures anyways)
- [ ] Desirable placement for images
	- [X] Subplots (so far figures only have one plot)
- [ ] Switching from 2 columns to 1 column per page (or any column number switch for that matter) --> needs a short "command language" for when the user is writing in Obsidian
- [X] Formatting certain words based on rules
	- Examples
	- Format text of mentioned notes based on
		- their path (e.g., path with methods)
		- [X]tags therein

## Niche/rarely encountered functionalities
- [X] Discard text inside comments **after** start of a (sub)section
- [ ] Properly convert results from querying commands in Obsidian. This will probably never be achieved with this converter, since it requires to have access to the obsidian dataview and dataviewjs outputs.
- [ ] **VERY DIFFICULT**: Convert anything that has to do with dataviewjs and inline queries. Dataview tables have been converted
	- This would be very useful, since dataview(js) is quite a powerful tool for organization of numerous things. An idea would be to convert it to .pdf, and merge it to the LateX file. Otherwise, a lot of programming is required!
- [ ] Automatic table size manipulation (not even LateX does that itself)
- [ ] Regarding Internal links: add page number next to the cross-reference, in case the document is printed
- [ ] EMOJIS: Latex does not include emojis. Therefore, so far they are replaced by text, however in the future I am considering to convert them to small pictures

## ➕️ Working on at the moment 
- Code maintenance
- Creating warning messages for errors that the user makes when writing the note
- More niche table conversions
- Inline code rendering for agile document parameterization

## 💀 What can cause errors
In this section, I will be writing what actions will cause errors in this version of the code.

1. Writing equations outside of the equation-block notes (read [here](#Adding-equations)). A correct conversion happens only when the equations are inside these special note files.
2. Writing tables and figures outside of their designated table-block and figure-block notes (same as with the equations)
3. Writing text using underscores without the escape character ("_" instead of "\_"), unless written in specific environments, such as equations
4. Having the following characters appear an odd number of times in the document:
	a. "\*\*"
	b. "\*"
	c. "\=\="



# 😁🔋 Strengths
- **Equations**:
	- The equation-referencing system helps reference the equations using the **note-linking** feature, thus allowing perfect **traceability of the equations**. The user can reference the equations in Obsidian and click/hover on their link to view them! See [short video](#video-3) for a quick demonstration.
 		- In addition, if you change the name of the equation, because it is a note, any references to it will be updated! 
- **Fast conversion:** Conversion to LateX is fast when the user allows the program to first find the note paths, log them in a textfile, and then not search for them again (unless moved to another folder, or have their names changed, in which case the tool searches anew within the vault)
- Works seamlessly with **embedded notes**. The benefits of using **embedded notes** are enlisted [here](#embedded-notes)
- Erases Obsidian Comments
- Every equation, table, and section receives a label automatically (no need to create one like in LateX)

# 😥 Weaknesses
- Large Obsidian files consume significant RAM (read [here](https://www.reddit.com/r/ObsidianMD/comments/scwg7a/obsidian_is_a_ram_hog/) as to why)
- Equation referencing: so far need to create separate embedded notes that represent equation blocks, since Obsidian itself cannot interact with MathJax well enough to create an equation referencing system
- ⚠ Direct text replacements are not possible, since we are using embedded notes, therefore those texts that we want to replace are not found in a single document (a solution can implemented, via tracking the links)
	- **Solution:** Use the text replacement tool in `converter.py`.

# Comparison to Overleaf

## Where Obsidian thrives

- First of all, it's FREE. Overleaf's advanced features require payment (most of which can be replicated by Obsidian)
- Much cleaner editor than Overleaf. Even though Overleaf is quite clean to use, it cannot compare to Obsidian. Obsidian is just more minimalistic (ok, as long as one does not obsess over style)
- Can keep your report/publication/book/etc connected to your note-taking ecosystem, instead of having to move around to an external source. That way, all the notes stay linked with the report you are writing
- Math: Much faster and cleaner equation writing (read the section about Equations and check the videos).
- More aesthetically pleasing
- Can write comments between the text, instead of requiring a new line (there are ways to go around it in Overleaf, but the comment text doesn't disappear when we hover the cursor away from it)


## Where Overleaf thrives
- Can write comments in a Google-docs-like manner
- (Latex property) Consumes much less RAM. Obsidian consumes a lot of RAM when the note is very large and contains objects that require rendering (e.g., embedded notes). There is a workaround in this tool for such cases.
- More distraction-free, since one can't obsess over plugins and workflows, which is the BIG TRAP of using Obsidian (https://www.youtube.com/watch?v=baKCC2uTbRc). Helps with avoiding procrastination
- Can track changes (though Obsidian with github can work better)
- Can define custom functions

# 📽 List of videos
If you want to jump to some videos, here's the list:

|     |     | 
| --- | --- | 
| [General video](https://drive.google.com/file/d/1KK-r5KZQHdIEtGJf9gZzpQrIEesj6_GA/view?usp=sharing) | General video showcasing the tool |
| [create equation block for referencing](#video-1)    |  create equation block for referencing   |
| [convert and see the result in LateX](#video-2)     |  convert and see the result in LateX   |
| [why this conversion system is very convenient](#video-3)    | why this conversion system is very convenient    |
| [how to write equations quickly](#video-4)    | Much faster than vanilla LateX, or vanilla Obsidian!    |

# ℹ How to use
## Prerequisites
1. Have Python 3 installed
2. Have Obsidian installed
3. Install the following Obsidian plugins
	1. Helps speed up equation referencing: **QuickAdd** (for quick insert of equation blocks)
 	2. Optional, helps write equations very fast: **Quick Latex for Obsidian**

## Usage

1. Clone the git
2. In `👨‍💻convert_to_latex.md`, you will need to change the path that links to the `converter.py`, since it is dependent on where you place it (will make the path relative in the future). 

In the note `👨‍💻convert_to_latex.md` you can specify which note you wish to convert, and then trigger the `converter.py` script to perform the conversion.

### (⚠ IMPORTANT) 📁 Set your paths 


To set the paths for the .md file to be converted, inside `converter.py`, under "User Parameters" section, change the:
- PATHS['command_note']. It corresponds to the path of `👨‍💻convert_to_latex.md`.

You won't need to change anything else inside `converter.py`, since the other paths are given in `👨‍💻convert_to_latex.md`.

`👨‍💻convert_to_latex.md` contains the instructions inside commands. 


### Using the example vault
You can use the example vault in order to see how the converter works, and a showcase of what it can convert.
The only modification you will need to do in order to use the vault as I intended to is to rename the "obsidian" folder to ".obsidian", since the latter name implies a hidden folder, github does not allow me to upload it, therefore I had to rename it.


### ▶ ▶ HOW TO RUN 
In `👨‍💻convert_to_latex.md`, click on the links next to the `code_run:: ` field. The 1st command performs the conversion from Obsidian to Latex, the 2nd compiles the latex file to .pdf. 
Make sure you first set the correct path to the `converter.py` file that runs the code. This basically opens the python file, which executes it. Make sure that the default app for opening the python file is python, not some editor (otherwise, you need to trigger a .bat file that triggers the .py file).

### Adding equations
[back to comparisons to other converters](#comparisons-to-other-converters)

This uses what we can call "**==note-block logic==**". I.e., writing the equation in a single note, but without writing anything else in that note (hence the "block" part of the name). We will use the same logic for Tables and Figures, so that their referencing becomes easier, and automatic upon name changes.


Due to the inherent difficulty of equation numbering and referencing in Obsidian (read this [thread](https://forum.obsidian.md/t/automatic-equation-numbering-latex-math/1325) for details), there is no direct way to number and refer to the equations in Obsidian.

The workaround that I have used requires creation of a separate note wherein only the equation is to be added. The note has to obey a few formatting rules, which can be automated with **QuickAdd**. To learn how to use it, please refer to the plugin guide. It is quite easy. 

The folder that you specify in QuickAdd wherein your equation note/block is to be created must be the same as `PARS['📂']['equation_blocks']` (in the `get_parameters.py`).

#### Formatting rules of the equation note

1. Name: The equations are to be labeled based on the **name** of the note. Therefore, for the code to be able to recognize them easily, I have created a name-based rule. If you wish to name the equation "conversion_law", then the name of the note should be "eq__block_conversion_law". Then, when in your document you refer to this equation, you can simply write "in equation \[\[eq\_\_block\_conversion\_law\]\]", and the final latex text would be "in equation \ref{conversion_law}".
2. Structure: The note has to **only have that equation inside, and nothing else!**. It is recommended that you start with a section "# \%\% expr \%\%" and then add the equation, such that you can embed it like \!\[\[eq\_\_block\_conversion\_law#expr\]\]. That way, the title of the note is not visible, making the obsidian file more readable.
3. Path: use a path of your choosing to put those equations. The reason for this is that in case you have a large vault, the code would have to search for the path of that note within the entire vault. Specifying a path for the equation blocks saves time.


##### Automating the creation of that note based on the formatting rules
Those steps above would normally require manual work, which would be annoying.

A way to automatically create an equation-note with the right format, in the right folder is to use the **QUICKADD** community plugin.

📽 The videos below illustrate how it creates those automatic equation notes, reference them, and how it looks in LateX.

#### Example of Equation conversion

##### video 1
[↩ back to list of videos](#-list-of-videos)

https://github.com/MariosGkMeng/Straightforward-Obsidian2Latex/assets/61937432/178bbe0f-b04c-43a0-a3d3-a6efebd6b9df

##### video 2
[↩ back to list of videos](#-list-of-videos)

https://github.com/MariosGkMeng/Straightforward-Obsidian2Latex/assets/61937432/1fe9b769-84be-495b-bad3-8a988472b952
##### video 3
[↩ back to list of videos](#-list-of-videos)

https://github.com/MariosGkMeng/Straightforward-Obsidian2Latex/assets/61937432/a6948f18-9cbe-4b13-a4ec-a1736828ad8e

### Adding citations

Citations are added as internal links with the syntax: "[[pItemNumber]]". For example, `[[p62]]` is the note that represents the 62nd literature file (be it an article, a book, etc)
Obsidian Text: "In [[p63]], the authors mention that ..."
Converted Latex Text:    "In \cite{p63}, the authors mention that ..."

BUT: as a user, you have to add the BibTex citation manually in your designated BibTex file, and use the "p63" as a name. That Bibtex file should be located in **the same path as `PARS['📁']['tex-file']`**!

I will add different rules upon user request.

### (NEW) Converting inline (dataview) code
[back to comparisons to other converters](#comparisons-to-other-converters)

For when you want to parameterize your document, here's a handy trick. You might have some fields in a note that contain text that you programmatically insert into your document. 

For example, assume that you have a note titled `fields_for_report`. In that note, you might have the field:

```markdown
argument_1:: true
argument_1:: We use this method, because it's awesome.
```
The first entry of `argument_1` is a boolean that we set to `true` if we want to print the message (the second entry of `argument_1`).

And then, in the `main` note (the one you want to convert to latex), you can write: 

```markdown
We used method_1. `=choice([[fields_for_report]].argument_1[0], [[fields_for_report]].argument_1[1], "")`
```

### (NEW) Parameterizing whether parts in the document will appear in the pdf file
[back to comparisons to other converters](#comparisons-to-other-converters)

In case you want to be able to parameterize the appearance of larger parts in the document, you can use the following syntax:

```
#Latex/Command/Use_section/Start (expression)

Your content here

#Latex/Command/Use_section/End
```
where `expression` can be either inline code that produces a boolean value (e.g., `=this.use_part_A`) or `true`/`false`. 

### Mapping packages that should not be combined
Regretably, LateX suffers from one more flaw; that of needing to be concious of packages that should not be loaded together. 
This is controlled in `get_parameters.py`, in the `PARS['par']['packages-to-load']` list. The first entry of this list contains the package, the second contains the document class for which this package should **not** be loaded (e.g., the package `cleveref` should not be loaded when using the `ifacconf` document class).

### For things that are not converted yet
[back to comparisons to other converters](#comparisons-to-other-converters)

Despite the fact that there are still a few features that have not yet been fully developed, it is possible to fully compose a document completely via Obsidian. 
This is possible through the recognition of **LateX command snippets**. A command snippet is something that looks like:

``` python
plt.figure()
plt.plot(x, y)
plt.show()
```
This is a snippet that contains code. The first line "``` python" declares the start of the snippet and its _language_.

The converter is able to recognize such snippets and print them in their corresponding format.

👆However, if the language of the snippet is specified as `latex`, then the converter will simply paste those lines of latex code to the .tex file without any formatting, thus allowing these lines to run properly in LateX. 

Examples: 

```latex
\lipsum[1-3]
```

```latex
\begin{frontmatter}
	
	\title{Style for IFAC Conferences & Symposia: Use Title Case for Paper Title\thanksref{footnoteinfo}} 
	% Title, preferably not more than 10 words.
	
	\thanks[footnoteinfo]{Sponsor and financial support acknowledgment goes here. Paper titles should be written in uppercase and lowercase letters, not all uppercase.}
	
	\author[First]{First A. Author} 
	\author[Second]{Second B. Author, Jr.} 
	\author[Third]{Third C. Author}
	
	\address[First]{National Institute of Standards and Technology, Boulder, CO 80305 USA (e-mail: author@ boulder.nist.gov).}
	\address[Second]{Colorado State University, Fort Collins, CO 80523 USA (e-mail: author@lamar. colostate.edu)}
	\address[Third]{Electrical Engineering Department,Seoul National University, Seoul, Korea, (e-mail: author@snu.ac.kr)}
	
	\begin{abstract}                % Abstract of not more than 250 words.
		\lipsum[1]
	\end{abstract}
	
	\begin{keyword}
		Five to ten keywords, preferably chosen from the IFAC keyword list.
	\end{keyword}
	
\end{frontmatter}
```
### For when the note to be converted is too large and contains many embedded notes, resulting in severe RAM consumption
It can happen that for large notes, Obsidian starts to consume significant RAM resulting in very slow performance.

A workaround developed for this tool is the usage of the following command that avoids embedding a note in Obsidian, but having the same effect when converted to LateX:

```
#Latex/Command/Invoke_note  [[note name]]
```

This way, the note `[[note name]]` will be unfolded in the converted version, while remaining "hidden" in the Obsidian editor, in order not to make the note to be converted very "heavy" for your computer.


# 🟢 Good Practices in Obsidian
## Embedded notes
Read in the [Obsidian website](https://help.obsidian.md/Linking+notes+and+files/Embed+files) for information on **what** they are.

Embedded notes allow us to:
- Make our work modular
	- Reuse notes, i.e., making them repeatable --> no need to manually copy/paste and rewrite things!
 	- Index the content of these notes (with more linked notes and/or tags) that apply only on that note --> doing that helps make the search for this note based on the indexing easier
- Focus on specific small parts of a document, instead of searching it in large stand-alone documents
- Use Obsidian for what it was made: creation of a **knowledge structure**: this means that smaller blocks of information are linked to each other based on their relationships and the meaning that they have to the creator. Therefore, writing a large document without embedded notes would result in you missing out in one of the most important features of Knowledge Management


## Automations and hacks

### QuickAdd for automatic creation of notes based on templates

Basically, the QuickAdd community plugin creates new notes based on user specified templates. You can make it place that note in specific folder, specify naming convention for that note, and a few other functionalities.

### Lightning fast Latex equation writing in Obsidian
Install the "Quick Latex for Obsidian" Community plugin. 
You can write **your own** snippets (see video below, wherein I show a few of my own as examples).

🔋🔋🔋 This makes equation writing much faster than vanilla LateX, or vanilla Obsidian!

📽 see video below on how fast you can write equations!

#### video 4
⚠ For the equation snippets, don't forget to press the Space key after inserting them (not mentioned in the video)

[↩ back to list of videos](#-list-of-videos)

https://github.com/MariosGkMeng/Straightforward-Obsidian2Latex/assets/61937432/95295ca1-3fce-457d-b18d-591ecd2796cb



# 💀 Potential errors
Some errors are linked to specific LateX editors. Since Obsidian is a local program, it makes sense that you might chose to use a local latex editor. Those can be sometimes finnicky and overly strict with compilation errors. A workaround is to use Overleaf, in which case you would need to copy the `.tex` file content to Overleaf, and make sure that your figures are all uploaded. So far, you should put the figures in the same path as the latex file, and set the parameter: `use_overleaf_all_in_the_same_folder` to `🟢` or `True`.

## Syntax that the user needs to follow

- For equations, the user should never leave any whitespace between the equation and the "$$" prefix
- If the first line of the note is a section, that section's title will be ignored


## Package problems
I am encountering package problems when I try to run the package in a different computer (therefore with different miktex package installations). For example, the `minted` package cannot be loaded, causing issues with the compilation (everything is fine when I remove the package loading command for `minted`).


- Missing `.sty` files and packages
	- `latex2pydata.sty` missing. Did not have this issue with my conversions. My `minted.sty` file does not require the latex2pydata package. Working on it.

# TODOs
- [ ] Add promo video of the tool, showing how it looks like to write a complete manuscript
- [X] Add a toy-vault with the appropriate paths and folders --> adjust the paths in the code accordingly
	- [ ] Add comments within the note for the user to learn interactively
- [ ] Move the parameter selection from `get_parameters.py` to an Obsidian note
	- [ ] Provide option for using different parameters for each note that is converted
## For the ReadMe file
- [ ] Add video to show how the figure system works
- [ ] Add video to show how the admonition system works

