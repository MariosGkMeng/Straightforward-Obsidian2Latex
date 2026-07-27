import fs from "fs/promises";
import path from "path";

const vaultPath = "/path/to/your/obsidian/vault";
const targetNote = "My Note"; // without .md

async function getMarkdownFiles(dir: string): Promise<string[]> {
	const entries = await fs.readdir(dir, { withFileTypes: true });

	const files = await Promise.all(
		entries.map(async (entry) => {
			const fullPath = path.join(dir, entry.name);

			if (entry.isDirectory()) {
				return getMarkdownFiles(fullPath);
			}

			if (entry.isFile() && entry.name.endsWith(".md")) {
				return [fullPath];
			}

			return [];
		})
	);

	return files.flat();
}

function extractWikiLinks(markdown: string): string[] {
	const regex = /\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]/g;
	const links: string[] = [];

	let match: RegExpExecArray | null;

	while ((match = regex.exec(markdown)) !== null) {
		links.push(match[1].trim());
	}

	return links;
}

async function main() {
	const files = await getMarkdownFiles(vaultPath);
	const backlinks: string[] = [];

	for (const file of files) {
		const content = await fs.readFile(file, "utf8");
		const links = extractWikiLinks(content);

		if (links.includes(targetNote)) {
			const relativePath = path.relative(vaultPath, file);
			const noteName = relativePath.replace(/\.md$/, "");

			backlinks.push(`[[${noteName}]]`);
		}
	}

	console.log(backlinks.map((link) => `- ${link}`).join("\n"));
}

main().catch(console.error);