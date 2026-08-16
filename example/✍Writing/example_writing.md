# Warnings to users
![[⚠warning to users]]

# Development Tasks
![[dev-tasks]]
# Formatting

![[formatting]]

# Itemization
## Bullet list
- Item 1
	- item 1.1
	- item 1.2
		- item 1.2.1
- Item 2
	1. Enumeration 1
		1. Enumeration 1.2
		2. Enumeration 2.2
	2. Enumeration 2
		1. Enumeration 2.1
			- Bullet 2.1.1
	3. Enumeration 3

## Enumerated list
1. Item 1
2. Item 2
	1. Item 2.1
	2. Item 2.2

## Task list
- [ ] Task 1
- [ ] Task 2
- [ ] Task 3
	- [ ] Task 3.1
- [ ] Task 4
# Adding citations
Command: just mention that link that pertains to the literature file. I use the "p"+"number" naming convention. For example, "p1" would be the first literature file in my vault. 

Example: In [[p1]], we see that... ^ad3b86

# Equations
Both equations and subfigures are written in the form of embedded notes, since they are encoded as notes.
```ad-warning
If you write an equation outside of the designated template in an embedded note, then the conversion will be faulty!
```
## Writing the equation

Steps:

1. Press ctrl+P, then Quickadd: equation\_block\_single

![[eq__block_Einstein#expr]]

It supports the aligned equations, as seen in [[eq__block_1]].

![[eq__block_1#expr]]
## Referencing the equation
In [[eq__block_Einstein]], we see that...
# Figures
## Adding figures
### No subfigures
![[figure__block_gradient_steps#fig]]

### With subfigures
See [[figure__block_1]].


- ➕ Allow user to create more complex configurations
![[figure__block_1#fig]]


## Referencing figures
In [[figure__block_1]], we can notice that...


# Admonition blocks
If you write admonition blocks, they are translated into something similar in latex.
**Example**
```ad-warning
This is a warning
```

```ad-note
This is a note
```


# Code blocks
```python
print("this is a code block")
print("this is another code block")
```

# Cross-reference of section
Check [[example_writing#Adding citations|this section]] about adding citations.


# 🔴Cross-reference of block
[[example_writing#^ad3b86|example]]

# Assume sections from embedded notes
The sections from embedded notes can assume the hierarchy of the file wherein they are embedded.
```ad-note
Notice in the latex file that the section hierarchy has been modified to adhere to the hierarchy of the file that embeds the note.
```

![[embedded with sections]]

# Hyperlinks
Click [here](https://www.youtube.com/).


# Tables

See [[table__block_1]], [[table__block_2]], and [[table__block_long]].

![[table__block_1#table]]

![[table__block_2#table]]

![[table__block_long#table]]

# Latex commands
When there is something niche, or some translation functionality that hasn't been developed yet, you can write a latex command within the code-block functionality of Obsidian, and the translator will not touch it. Use the syntax according to the following example:

```latex
\lipsum[1-4]
```

# Inline code parameterization
Open [[fields_for_report|this note]] to modify the fields and add more.
We used method_1. `=choice([[fields_for_report]].argument_1[0], [[fields_for_report]].argument_1[1], "")` `=choice([[fields_for_report]].idea_1[0], [[fields_for_report]].idea_1[1], "")`


# Appendix
![[example_writing--Appendix]]
