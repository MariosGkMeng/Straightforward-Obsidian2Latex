// The subset of a QuickAdd (https://github.com/chhoumann/quickadd) setup that
// converter.py's "note-block logic" (equation/figure/table blocks) actually
// depends on. Extracted from a real working config, with everything specific
// to one person's broader research workflow left out.

export const QUICKADD_TEMPLATES: Record<string, string> = {
	"equation_block_single.md": `# %%expr%%
`,
	"figure_block.md": `%%
latex_conv_in_file::

size_in_latex:: 0.8
caption_short::
caption_long::
subfigure_widths::
subfigure_abs_or_rel:: abs
subfigure_captions::
subfigure_number_of_rows::
cover_all_columns::
Signal:: #📡/
%%
# %% fig %%
📣*\`=this.caption_long\`*
\`\`\`dataviewjs
let this_file = dv.current();
let subfig_captions = this_file.subfigure_captions || [];
let z=0;
for (let s of subfig_captions){
    if (s && s.length > 0){  // check that s is not null/undefined
	    z+=1
        dv.el("el", "(" + String(z) + ") " + s + "<br>");
        dv.el("el", "");
    }
}

\`\`\`
`,
	"table_block.md": `%%
latex_conv_in_file::

caption::
widths::
package:: #Latex/Table/package/
header_rotation::
use_hlines::
use_vlines::
exclude_columns::

If the table is a dataview table:
datav__file_column_name::
datav__exclude_columns::
datav__make_sections_out_of_notes::
%%
# %%table%%
📣*\`=this.caption\`*
`,
};

export const QUICKADD_OUTPUT_FOLDERS = ["✍Writing/equation blocks", "✍Writing/figure blocks", "✍Writing/table_blocks"];

/** QuickAdd "Template" choice configs, minus the id (assigned fresh on insert). */
export const QUICKADD_CHOICES: Record<string, unknown>[] = [
	{
		name: "equation_block_single",
		type: "Template",
		command: true,
		templatePath: "👨‍💻Automations/equation_block_single",
		fileNameFormat: { enabled: true, format: "eq__block__" },
		folder: {
			enabled: true,
			folders: ["✍Writing/equation blocks"],
			chooseWhenCreatingNote: false,
			createInSameFolderAsActiveFile: false,
			chooseFromSubfolders: false,
		},
		appendLink: true,
		openFileInNewTab: { enabled: false, direction: "vertical", focus: true },
		openFile: true,
		openFileInMode: "default",
		fileOpening: { location: "tab", direction: "vertical", focus: true, mode: "default" },
		fileExistsBehavior: { kind: "apply", mode: "increment" },
	},
	{
		name: "figure_block",
		type: "Template",
		command: true,
		templatePath: "👨‍💻Automations/figure_block.md",
		fileNameFormat: { enabled: true, format: "figure__block_" },
		folder: {
			enabled: true,
			folders: ["✍Writing/figure blocks"],
			chooseWhenCreatingNote: false,
			createInSameFolderAsActiveFile: false,
			chooseFromSubfolders: false,
		},
		appendLink: true,
		openFileInNewTab: { enabled: true, direction: "vertical", focus: true },
		openFile: true,
		openFileInMode: "default",
		fileOpening: { location: "window", direction: "vertical", focus: true, mode: "default" },
		fileExistsBehavior: { kind: "apply", mode: "increment" },
	},
	{
		name: "table_block",
		type: "Template",
		command: true,
		templatePath: "👨‍💻Automations/table_block",
		fileNameFormat: { enabled: true, format: "table__block_" },
		folder: {
			enabled: true,
			folders: ["✍Writing/table_blocks"],
			chooseWhenCreatingNote: false,
			createInSameFolderAsActiveFile: false,
			chooseFromSubfolders: false,
		},
		appendLink: true,
		openFileInNewTab: { enabled: true, direction: "vertical", focus: true },
		openFile: true,
		openFileInMode: "default",
		fileOpening: { location: "split", direction: "vertical", focus: true, mode: "default" },
		fileExistsBehavior: { kind: "apply", mode: "increment" },
	},
];
