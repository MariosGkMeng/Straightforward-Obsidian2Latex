import { App, Notice, Plugin, PluginSettingTab, Setting } from "obsidian";
import { spawn } from "child_process";
import { shell } from "electron";
import * as fs from "fs";
import * as path from "path";

interface LatexConverterSettings {
	pythonPath: string;
	converterPath: string;
	commandNotePath: string;
}

const DEFAULT_SETTINGS: LatexConverterSettings = {
	pythonPath: "python",
	converterPath: "C:\\Users\\mariosg\\OneDrive - NTNU\\FILES\\workTips\\Literature\\Straightforward-Obsidian2Latex\\converter.py",
	commandNotePath: "C:\\Users\\mariosg\\OneDrive - NTNU\\FILES\\workTips\\✍Writing\\👨‍💻convert_to_latex.md",
};

export default class LatexConverterPlugin extends Plugin {
	settings: LatexConverterSettings;

	async onload() {
		await this.loadSettings();

		this.addCommand({
			id: "convert-current-note",
			name: "Convert current note to LaTeX",
			callback: () => this.convertCurrentNote(),
		});

		this.addCommand({
			id: "run-converter",
			name: "Run LaTeX converter (use convert_to_latex.md target)",
			callback: () => this.runConverter(null, false),
		});

		this.addCommand({
			id: "convert-and-compile-current-note",
			name: "Convert current note to LaTeX AND compile to PDF",
			callback: () => this.convertCurrentNote(true),
		});

		this.addCommand({
			id: "convert-and-compile",
			name: "Convert AND compile to PDF (use convert_to_latex.md target)",
			callback: () => this.runConverter(null, true),
		});

		this.addSettingTab(new ConverterSettingTab(this.app, this));
	}

	async convertCurrentNote(compile = false) {
		const activeFile = this.app.workspace.getActiveFile();
		if (!activeFile) {
			new Notice("No active file open.");
			return;
		}
		await this.runConverter(activeFile.basename, compile);
	}

	async runConverter(overrideNote: string | null, compile = false) {
		const converterDir = path.dirname(this.settings.converterPath);
		let originalContent: string | null = null;
		let noteName = overrideNote;

		if (overrideNote !== null) {
			try {
				originalContent = fs.readFileSync(this.settings.commandNotePath, "utf8");
				const updated = originalContent.replace(/convert_note::.*/, `convert_note:: [[${overrideNote}]]`);
				fs.writeFileSync(this.settings.commandNotePath, updated, "utf8");
			} catch (e) {
				new Notice(`Failed to prepare command note: ${e.message}`);
				return;
			}
		} else {
			try {
				const content = fs.readFileSync(this.settings.commandNotePath, "utf8");
				const match = content.match(/convert_note::\s*\[\[([^\]]+)\]\]/);
				if (match) noteName = match[1];
			} catch (_) {
				// no command note yet — proceed without an override
			}
		}

		new Notice(`Converting ${noteName ?? "note"}...`);

		const proc = spawn(this.settings.pythonPath, [this.settings.converterPath], {
			cwd: converterDir,
			windowsHide: false,
			env: { ...process.env, PYTHONIOENCODING: "utf-8" },
		});

		let stdout = "";
		let stderr = "";
		proc.stdout.on("data", (data) => {
			stdout += data.toString();
		});
		proc.stderr.on("data", (data) => {
			stderr += data.toString();
		});

		proc.on("close", (code) => {
			if (originalContent !== null) {
				try {
					fs.writeFileSync(this.settings.commandNotePath, originalContent, "utf8");
				} catch (_) {
					// best-effort restore
				}
			}

			if (code === 0) {
				new Notice("✓ Conversion complete!");
				const texLine = stdout.split("\n").find((l) => l.startsWith("TEX_OUTPUT:"));
				if (texLine) {
					const texPath = texLine.slice("TEX_OUTPUT:".length).trim();
					if (compile) {
						this.compilePdf(texPath);
					} else {
						shell.openPath(texPath);
					}
				}
			} else {
				new Notice(`Converter failed (exit ${code}). See console for details.`);
				console.error("[LaTeX Converter] stderr:", stderr);
			}
		});

		proc.on("error", (err) => {
			new Notice(`Failed to start converter: ${err.message}`);
		});
	}

	compilePdf(texPath: string) {
		const texDir = path.dirname(texPath);
		new Notice("Compiling PDF...");

		const proc = spawn(
			"latexmk",
			["-pdf", "-interaction=nonstopmode", "-synctex=1", "-shell-escape", "-bibtex", texPath],
			{
				cwd: texDir,
				windowsHide: false,
				env: { ...process.env, PYTHONIOENCODING: "utf-8" },
			}
		);

		let stderr = "";
		proc.stderr.on("data", (data) => {
			stderr += data.toString();
		});

		proc.on("close", (code) => {
			if (code === 0) {
				new Notice("✓ PDF ready!");
				const pdfPath = texPath.replace(/\.tex$/, ".pdf");
				shell.openPath(texPath);
				shell.openPath(pdfPath);
			} else {
				new Notice(`PDF compilation failed (exit ${code}). See console for details.`);
				console.error("[LaTeX Converter] latexmk stderr:", stderr);
				shell.openPath(texPath);
			}
		});

		proc.on("error", (err) => {
			new Notice(`Failed to start latexmk: ${err.message}`);
			shell.openPath(texPath);
		});
	}

	async loadSettings() {
		this.settings = Object.assign({}, DEFAULT_SETTINGS, await this.loadData());
	}

	async saveSettings() {
		await this.saveData(this.settings);
	}
}

class ConverterSettingTab extends PluginSettingTab {
	plugin: LatexConverterPlugin;

	constructor(app: App, plugin: LatexConverterPlugin) {
		super(app, plugin);
		this.plugin = plugin;
	}

	display(): void {
		const { containerEl } = this;
		containerEl.empty();
		containerEl.createEl("h2", { text: "LaTeX Converter Settings" });

		new Setting(containerEl)
			.setName("Python executable")
			.setDesc('Path to python (e.g. "python", "python3", or full path like C:\\Python310\\python.exe)')
			.addText((text) =>
				text
					.setPlaceholder("python")
					.setValue(this.plugin.settings.pythonPath)
					.onChange(async (value) => {
						this.plugin.settings.pythonPath = value;
						await this.plugin.saveSettings();
					})
			);

		new Setting(containerEl)
			.setName("converter.py path")
			.setDesc("Full absolute path to converter.py")
			.addText((text) =>
				text
					.setPlaceholder("C:\\path\\to\\converter.py")
					.setValue(this.plugin.settings.converterPath)
					.onChange(async (value) => {
						this.plugin.settings.converterPath = value;
						await this.plugin.saveSettings();
					})
			);

		new Setting(containerEl)
			.setName("Command note path")
			.setDesc("Full absolute path to the convert_to_latex.md command note")
			.addText((text) =>
				text
					.setPlaceholder("C:\\path\\to\\convert_to_latex.md")
					.setValue(this.plugin.settings.commandNotePath)
					.onChange(async (value) => {
						this.plugin.settings.commandNotePath = value;
						await this.plugin.saveSettings();
					})
			);
	}
}
