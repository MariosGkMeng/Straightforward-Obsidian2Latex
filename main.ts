import { App, FileSystemAdapter, Notice, Plugin, PluginSettingTab, Setting } from "obsidian";
import { spawn } from "child_process";
import { shell } from "electron";
import * as fs from "fs";
import * as https from "https";
import * as path from "path";

interface LatexConverterSettings {
	pythonPath: string;
	converterPath: string;
	commandNotePath: string;
}

const DEFAULT_SETTINGS: LatexConverterSettings = {
	pythonPath: "python",
	converterPath: "",
	commandNotePath: "",
};

const BUNDLED_PYTHON_VERSION = "3.12.10";
const BUNDLED_PYTHON_ZIP_URL = `https://www.python.org/ftp/python/${BUNDLED_PYTHON_VERSION}/python-${BUNDLED_PYTHON_VERSION}-embed-amd64.zip`;
const GET_PIP_URL = "https://bootstrap.pypa.io/get-pip.py";

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

	/** Absolute path to this plugin's own installed folder (desktop only). */
	getPluginDir(): string {
		const adapter = this.app.vault.adapter;
		if (!(adapter instanceof FileSystemAdapter)) {
			throw new Error("This plugin only supports the Obsidian desktop app.");
		}
		return path.join(adapter.getBasePath(), this.manifest.dir ?? "");
	}

	/** converter.py bundled with this plugin, unless the user overrode it in settings. */
	resolveConverterPath(): string {
		return this.settings.converterPath || path.join(this.getPluginDir(), "converter.py");
	}

	/** Downloads a URL to a local file, following redirects. */
	private downloadFile(url: string, destPath: string, redirectsLeft = 5): Promise<void> {
		return new Promise((resolve, reject) => {
			const file = fs.createWriteStream(destPath);
			https
				.get(url, (res) => {
					if (res.statusCode && res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
						file.close();
						fs.unlink(destPath, () => {
							if (redirectsLeft <= 0) {
								reject(new Error("Too many redirects"));
								return;
							}
							this.downloadFile(res.headers.location as string, destPath, redirectsLeft - 1).then(
								resolve,
								reject
							);
						});
						return;
					}
					if (res.statusCode !== 200) {
						file.close();
						fs.unlink(destPath, () => {});
						reject(new Error(`Download failed: HTTP ${res.statusCode}`));
						return;
					}
					res.pipe(file);
					file.on("finish", () => file.close(() => resolve()));
				})
				.on("error", (err) => {
					fs.unlink(destPath, () => {});
					reject(err);
				});
		});
	}

	/** Runs a command to completion and collects its output. */
	private runCommand(
		cmd: string,
		args: string[],
		cwd?: string
	): Promise<{ code: number; stdout: string; stderr: string }> {
		return new Promise((resolve, reject) => {
			const proc = spawn(cmd, args, { cwd, windowsHide: false });
			let stdout = "";
			let stderr = "";
			proc.stdout.on("data", (d) => (stdout += d.toString()));
			proc.stderr.on("data", (d) => (stderr += d.toString()));
			proc.on("close", (code) => resolve({ code: code ?? -1, stdout, stderr }));
			proc.on("error", reject);
		});
	}

	/**
	 * Downloads a private, self-contained Python (the official Windows embeddable
	 * distribution) into this plugin's own folder, bootstraps pip, installs numpy
	 * (the only third-party dependency converter.py needs), and points the
	 * "Python executable" setting at it. Doesn't touch any system-wide Python.
	 */
	async setupBundledPython(): Promise<void> {
		if (process.platform !== "win32" || process.arch !== "x64") {
			new Notice("Bundled Python setup is only available on 64-bit Windows right now.");
			return;
		}

		const pyDir = path.join(this.getPluginDir(), "python-embed");
		const pythonExe = path.join(pyDir, "python.exe");

		if (fs.existsSync(pythonExe)) {
			this.settings.pythonPath = pythonExe;
			await this.saveSettings();
			new Notice("Bundled Python is already set up — pointed the plugin at it.");
			return;
		}

		try {
			fs.mkdirSync(pyDir, { recursive: true });

			new Notice("Downloading Python...");
			const zipPath = path.join(pyDir, "python-embed.zip");
			await this.downloadFile(BUNDLED_PYTHON_ZIP_URL, zipPath);

			new Notice("Extracting Python...");
			const extract = await this.runCommand("powershell", [
				"-NoProfile",
				"-Command",
				`Expand-Archive -LiteralPath '${zipPath}' -DestinationPath '${pyDir}' -Force`,
			]);
			if (extract.code !== 0) throw new Error(`Extraction failed: ${extract.stderr}`);
			fs.unlinkSync(zipPath);

			// Embeddable Python ships with site-packages disabled; enable it so
			// pip-installed packages (numpy) are importable.
			const pthFile = fs.readdirSync(pyDir).find((f) => /^python\d+\._pth$/.test(f));
			if (pthFile) {
				const pthPath = path.join(pyDir, pthFile);
				const content = fs.readFileSync(pthPath, "utf8").replace(/#\s*import site/, "import site");
				fs.writeFileSync(pthPath, content, "utf8");
			}

			new Notice("Installing pip...");
			const getPipPath = path.join(pyDir, "get-pip.py");
			await this.downloadFile(GET_PIP_URL, getPipPath);
			const pipInstall = await this.runCommand(pythonExe, [getPipPath, "--no-warn-script-location"], pyDir);
			if (pipInstall.code !== 0) throw new Error(`pip bootstrap failed: ${pipInstall.stderr}`);
			fs.unlinkSync(getPipPath);

			new Notice("Installing numpy...");
			const numpyInstall = await this.runCommand(pythonExe, ["-m", "pip", "install", "numpy"], pyDir);
			if (numpyInstall.code !== 0) throw new Error(`numpy install failed: ${numpyInstall.stderr}`);

			this.settings.pythonPath = pythonExe;
			await this.saveSettings();
			new Notice("✓ Bundled Python set up! 'Python executable' setting updated automatically.");
		} catch (e) {
			new Notice(`Python setup failed: ${e.message}`);
			console.error("[LaTeX Converter] Bundled Python setup failed:", e);
		}
	}

	async runConverter(overrideNote: string | null, compile = false) {
		if (!this.settings.commandNotePath) {
			new Notice("Set 'Command note path' in the LaTeX Converter settings first.");
			return;
		}

		const converterPath = this.resolveConverterPath();
		const converterDir = path.dirname(converterPath);
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

		const proc = spawn(this.settings.pythonPath, [converterPath], {
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
			.setName("Bundled Python (Windows only)")
			.setDesc(
				"No Python installed? Download a private, self-contained Python + numpy just for this " +
					"plugin (~30 MB) and point 'Python executable' below at it automatically. Doesn't touch " +
					"any system-wide Python install."
			)
			.addButton((btn) =>
				btn.setButtonText("Set up bundled Python").onClick(async () => {
					btn.setDisabled(true).setButtonText("Setting up...");
					await this.plugin.setupBundledPython();
					btn.setDisabled(false).setButtonText("Set up bundled Python");
					this.display();
				})
			);

		new Setting(containerEl)
			.setName("converter.py path")
			.setDesc(
				"Leave empty to use the converter.py bundled with this plugin. Only set this if you keep converter.py somewhere else."
			)
			.addText((text) =>
				text
					.setPlaceholder(this.plugin.getPluginDir() + path.sep + "converter.py")
					.setValue(this.plugin.settings.converterPath)
					.onChange(async (value) => {
						this.plugin.settings.converterPath = value;
						await this.plugin.saveSettings();
					})
			);

		new Setting(containerEl)
			.setName("Command note path")
			.setDesc(
				"Required. Full absolute path to a note in your vault containing a line like " +
					"'convert_note:: [[Note Name]]' — the plugin temporarily points this line at " +
					"the note being converted before running the converter."
			)
			.addText((text) =>
				text
					.setPlaceholder("C:\\path\\to\\your-vault\\convert_to_latex.md")
					.setValue(this.plugin.settings.commandNotePath)
					.onChange(async (value) => {
						this.plugin.settings.commandNotePath = value;
						await this.plugin.saveSettings();
					})
			);
	}
}
