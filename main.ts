import { App, FileSystemAdapter, Notice, Plugin, PluginSettingTab, Setting, SettingDefinitionItem } from "obsidian";
import { spawn } from "child_process";
import { shell } from "electron";
import { randomUUID } from "crypto";
import * as fs from "fs";
import * as https from "https";
import * as path from "path";
import { PYTHON_ASSETS } from "./python-assets.generated";
import { QUICKADD_CHOICES, QUICKADD_OUTPUT_FOLDERS, QUICKADD_TEMPLATES } from "./quickadd-assets";

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
		this.ensurePythonAssets();

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

	/** Absolute path to the current vault's root folder (desktop only). */
	getVaultDir(): string {
		const adapter = this.app.vault.adapter;
		if (!(adapter instanceof FileSystemAdapter)) {
			throw new Error("This plugin only supports the Obsidian desktop app.");
		}
		return adapter.getBasePath();
	}

	/** Absolute path to this plugin's own installed folder (desktop only). */
	getPluginDir(): string {
		return path.join(this.getVaultDir(), this.manifest.dir ?? "");
	}

	/** converter.py bundled with this plugin, unless the user overrode it in settings. */
	resolveConverterPath(): string {
		return this.settings.converterPath || path.join(this.getPluginDir(), "converter.py");
	}

	/**
	 * Writes converter.py/src/ out to this plugin's own install folder, creating
	 * or refreshing them to match the currently-installed plugin version.
	 *
	 * Obsidian's plugin installer (community browser or BRAT) only ever fetches
	 * main.js/manifest.json from a GitHub release — never the rest of the repo —
	 * so without this, converter.py wouldn't exist wherever the plugin actually
	 * gets installed. Safe to call on every load: files are only (re)written
	 * when missing or when their content differs from what's embedded.
	 */
	private ensurePythonAssets(): void {
		let pluginDir: string;
		try {
			pluginDir = this.getPluginDir();
		} catch {
			return;
		}

		for (const [relPath, content] of Object.entries(PYTHON_ASSETS)) {
			const dest = path.join(pluginDir, ...relPath.split("/"));
			try {
				fs.mkdirSync(path.dirname(dest), { recursive: true });
				if (!fs.existsSync(dest) || fs.readFileSync(dest, "utf8") !== content) {
					fs.writeFileSync(dest, content, "utf8");
				}
			} catch (e) {
				console.error(`[LaTeX Converter] Failed to write bundled file ${relPath}:`, e);
			}
		}

		// note_map.json is runtime-generated cache data the tool populates during
		// use, not shipped source — seed it once if missing, but never overwrite
		// it afterward (unlike the source files above).
		const noteMapPath = path.join(pluginDir, "src", "note_map.json");
		if (!fs.existsSync(noteMapPath)) {
			try {
				fs.mkdirSync(path.dirname(noteMapPath), { recursive: true });
				fs.writeFileSync(noteMapPath, "{\n}\n", "utf8");
			} catch (e) {
				console.error("[LaTeX Converter] Failed to seed note_map.json:", e);
			}
		}
	}

	/** Whether a given community plugin id is currently installed and enabled in this vault. */
	isPluginEnabled(id: string): boolean {
		// app.plugins isn't part of the public Obsidian API — this is read-only
		// presence detection, not an attempt to control other plugins.
		const anyApp = this.app as unknown as { plugins?: { enabledPlugins?: Set<string> } };
		return !!anyApp.plugins?.enabledPlugins?.has(id);
	}

	/**
	 * Sets up the QuickAdd templates/folders/commands that converter.py's
	 * "note-block logic" (equation/figure/table blocks) depends on: writes the
	 * 3 template files into <vault>/👨‍💻Automations/, creates the matching
	 * output folders under ✍Writing/, and — if QuickAdd is installed — adds
	 * the 3 matching QuickAdd commands, without touching any of the user's
	 * other QuickAdd choices.
	 */
	async setupQuickAddTemplates(): Promise<void> {
		const vaultDir = this.getVaultDir();
		const automationsDir = path.join(vaultDir, "👨‍💻Automations");

		try {
			fs.mkdirSync(automationsDir, { recursive: true });
			for (const [filename, content] of Object.entries(QUICKADD_TEMPLATES)) {
				const dest = path.join(automationsDir, filename);
				if (!fs.existsSync(dest)) {
					fs.writeFileSync(dest, content, "utf8");
				}
			}
			for (const folder of QUICKADD_OUTPUT_FOLDERS) {
				fs.mkdirSync(path.join(vaultDir, ...folder.split("/")), { recursive: true });
			}
			new Notice("Created the equation/figure/table block templates and folders.");
		} catch (e) {
			const message = e instanceof Error ? e.message : String(e);
			new Notice(`Failed to set up templates/folders: ${message}`);
			return;
		}

		if (!this.isPluginEnabled("quickadd")) {
			new Notice(
				'QuickAdd isn\'t installed/enabled. Install it via Settings → Community plugins → Browse → "QuickAdd", enable it, then click this button again to add the commands.',
				20000
			);
			return;
		}

		const quickAddDataPath = path.join(vaultDir, ".obsidian", "plugins", "quickadd", "data.json");
		try {
			const data: { choices?: Record<string, unknown>[] } = fs.existsSync(quickAddDataPath)
				? JSON.parse(fs.readFileSync(quickAddDataPath, "utf8"))
				: {};
			if (!Array.isArray(data.choices)) data.choices = [];

			let added = 0;
			for (const choice of QUICKADD_CHOICES) {
				const exists = data.choices.some((c) => c && c["name"] === choice["name"]);
				if (!exists) {
					data.choices.push({ ...choice, id: randomUUID() });
					added++;
				}
			}

			if (added > 0) {
				fs.writeFileSync(quickAddDataPath, JSON.stringify(data, null, 2), "utf8");
				new Notice(
					`Added ${added} QuickAdd command(s): equation/figure/table block. Restart Obsidian (or reload QuickAdd) to see them.`,
					15000
				);
			} else {
				new Notice("QuickAdd already has these commands configured — nothing to add.");
			}
		} catch (e) {
			const message = e instanceof Error ? e.message : String(e);
			new Notice(`Failed to update QuickAdd's configuration: ${message}`);
		}
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
			proc.stdout.on("data", (d: Buffer) => (stdout += d.toString()));
			proc.stderr.on("data", (d: Buffer) => (stderr += d.toString()));
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
			const message = e instanceof Error ? e.message : String(e);
			new Notice(`Python setup failed: ${message}`);
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
				const message = e instanceof Error ? e.message : String(e);
				new Notice(`Failed to prepare command note: ${message}`);
				return;
			}
		} else {
			try {
				const content = fs.readFileSync(this.settings.commandNotePath, "utf8");
				const match = content.match(/convert_note::\s*\[\[([^\]]+)\]\]/);
				if (match) noteName = match[1];
			} catch {
				// no command note yet — proceed without an override
			}
		}

		new Notice(`Converting ${noteName ?? "note"}...`);

		const proc = spawn(this.settings.pythonPath, [converterPath], {
			cwd: converterDir,
			windowsHide: false,
			env: { ...process.env, PYTHONIOENCODING: "utf-8", OBSIDIAN_VAULT_PATH: this.getVaultDir() },
		});

		let stdout = "";
		let stderr = "";
		proc.stdout.on("data", (data: Buffer) => {
			stdout += data.toString();
		});
		proc.stderr.on("data", (data: Buffer) => {
			stderr += data.toString();
		});

		proc.on("close", (code) => {
			if (originalContent !== null) {
				try {
					fs.writeFileSync(this.settings.commandNotePath, originalContent, "utf8");
				} catch {
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
						void shell.openPath(texPath).then((openErr) => {
							if (openErr) new Notice(`Failed to open ${texPath}: ${openErr}`);
						});
					}
				}
			} else {
				void this.showErrorLog("last-conversion-error.txt", stderr).then((logPath) => {
					new Notice(`Converter failed (exit ${code}). Full error: ${logPath}`, 15000);
				});
				console.error("[LaTeX Converter] stderr:", stderr);
			}
		});

		proc.on("error", (err) => {
			new Notice(
				`Failed to start converter using python path "${this.settings.pythonPath}": ${err.message}`,
				15000
			);
		});
	}

	/**
	 * Writes error output to a plain-text log file in the plugin's own folder
	 * and opens it, so Python/latexmk tracebacks (with exact line numbers) are
	 * easy to read without hunting through Obsidian's developer console
	 * (Ctrl+Shift+I). Falls back to revealing the file in the file manager if
	 * nothing has ".txt" associated as a default opener. Always returns the
	 * absolute path so it can be shown even if opening it silently fails.
	 */
	private async showErrorLog(filename: string, content: string): Promise<string> {
		const logPath = path.join(this.getPluginDir(), filename);
		try {
			fs.writeFileSync(logPath, content || "(no error output captured)", "utf8");
		} catch (e) {
			console.error("[LaTeX Converter] Failed to write error log:", e);
			return logPath;
		}
		const openErr = await shell.openPath(logPath);
		if (openErr) {
			console.error("[LaTeX Converter] Failed to open error log, revealing it instead:", openErr);
			shell.showItemInFolder(logPath);
		}
		return logPath;
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
		proc.stderr.on("data", (data: Buffer) => {
			stderr += data.toString();
		});

		proc.on("close", (code) => {
			if (code === 0) {
				new Notice("✓ PDF ready!");
				const pdfPath = texPath.replace(/\.tex$/, ".pdf");
				void shell.openPath(texPath).then(() => shell.openPath(pdfPath));
			} else {
				void this.showErrorLog("last-compile-error.txt", stderr).then((logPath) => {
					new Notice(`PDF compilation failed (exit ${code}). Full error: ${logPath}`, 15000);
				});
				console.error("[LaTeX Converter] latexmk stderr:", stderr);
				void shell.openPath(texPath);
			}
		});

		proc.on("error", (err) => {
			new Notice(`Failed to start latexmk: ${err.message}. Is latexmk installed and on PATH?`, 15000);
			void shell.openPath(texPath);
		});
	}

	async loadSettings() {
		const data = (await this.loadData()) as Partial<LatexConverterSettings> | null;
		this.settings = Object.assign({}, DEFAULT_SETTINGS, data);
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

	/** Explicit read from this.plugin.settings, rather than relying on the inherited default. */
	getControlValue(key: string): unknown {
		return (this.plugin.settings as unknown as Record<string, unknown>)[key];
	}

	/** Explicit write to this.plugin.settings + persist, rather than relying on the inherited default. */
	async setControlValue(key: string, value: unknown): Promise<void> {
		(this.plugin.settings as unknown as Record<string, unknown>)[key] = value;
		await this.plugin.saveSettings();
	}

	/** Declarative settings for Obsidian 1.13.0+ (adds settings-search support). */
	getSettingDefinitions(): SettingDefinitionItem[] {
		return [
			{
				name: "Python executable",
				desc: 'Path to python (e.g. "python", "python3", or full path like C:\\Python310\\python.exe)',
				control: { type: "text", key: "pythonPath", placeholder: "python" },
			},
			{
				name: "Bundled Python (Windows only)",
				desc:
					"No Python installed? Download a private, self-contained Python + numpy just for this " +
					"plugin (~30 MB) and point 'Python executable' above at it automatically. Doesn't touch " +
					"any system-wide Python install.",
				render: (setting) => {
					setting.addButton((btn) =>
						btn.setButtonText("Set up bundled Python").onClick(async () => {
							btn.setDisabled(true).setButtonText("Setting up...");
							await this.plugin.setupBundledPython();
							btn.setDisabled(false).setButtonText("Set up bundled Python");
							this.update();
						})
					);
				},
			},
			{
				name: "converter.py path",
				desc: "Leave empty to use the converter.py bundled with this plugin. Only set this if you keep converter.py somewhere else.",
				control: {
					type: "text",
					key: "converterPath",
					placeholder: this.plugin.getPluginDir() + path.sep + "converter.py",
				},
			},
			{
				name: "Command note path",
				desc:
					"Required. Full absolute path to a note in your vault containing a line like " +
					"'convert_note:: [[Note Name]]' — the plugin temporarily points this line at " +
					"the note being converted before running the converter.",
				control: {
					type: "text",
					key: "commandNotePath",
					placeholder: "C:\\path\\to\\your-vault\\convert_to_latex.md",
				},
			},
			{
				name: "Required plugins",
				desc: "This converter's equation/figure/table block workflow depends on QuickAdd. Quick Latex is optional (just speeds up manual equation typing).",
				render: (setting) => {
					const quickAddOk = this.plugin.isPluginEnabled("quickadd");
					const quickLatexOk = this.plugin.isPluginEnabled("quick-latex");
					setting.descEl.createEl("div", {
						text: `QuickAdd (required): ${quickAddOk ? "✓ installed and enabled" : "✗ not installed/enabled"}`,
					});
					setting.descEl.createEl("div", {
						text: `Quick Latex (optional): ${quickLatexOk ? "✓ installed and enabled" : "not installed"}`,
					});
					if (!quickAddOk || !quickLatexOk) {
						setting.descEl.createEl("div", {
							text: 'Install missing plugins via Settings → Community plugins → Browse, then search by name.',
						});
					}
				},
			},
			{
				name: "QuickAdd templates (equation/figure/table blocks)",
				desc:
					"Creates the equation_block_single/figure_block/table_block template files and their " +
					"output folders, and — if the QuickAdd plugin is installed and enabled — adds the " +
					"matching QuickAdd commands. Existing choices with the same name are left untouched.",
				render: (setting) => {
					setting.addButton((btn) =>
						btn.setButtonText("Set up QuickAdd templates").onClick(async () => {
							btn.setDisabled(true).setButtonText("Setting up...");
							await this.plugin.setupQuickAddTemplates();
							btn.setDisabled(false).setButtonText("Set up QuickAdd templates");
						})
					);
				},
			},
		];
	}
}
