import re
from pathlib import Path

def _build_pdf_index(pdf_dir: Path) -> dict[int, Path]:
    """
    Index PDFs by leading number in filename: '1234. whatever.pdf' -> 1234
    If multiple PDFs share the same number, pick the shortest filename (usually the "main" one).
    """
    index: dict[int, list[Path]] = {}
    for p in pdf_dir.glob("*.pdf"):
        m = re.match(r"^\s*(\d+)\.", p.name)
        if not m:
            continue
        n = int(m.group(1))
        index.setdefault(n, []).append(p)

    # choose a deterministic "best" file per number
    best: dict[int, Path] = {}
    for n, paths in index.items():
        paths_sorted = sorted(paths, key=lambda x: (len(x.name), x.name.lower()))
        best[n] = paths_sorted[0]
    return best

def _iter_bib_entries(text: str):
    """
    Yield (start_idx, end_idx, entry_text, key) for each top-level BibTeX entry.
    Parses braces properly (handles nested braces in fields).
    """
    i, N = 0, len(text)
    while i < N:
        at = text.find("@", i)
        if at == -1:
            return
        # Find the first '{' after '@'
        brace_open = text.find("{", at)
        if brace_open == -1:
            return

        # BibTeX entry key is from after '{' up to the first comma at top-level
        j = brace_open + 1
        # skip whitespace/newlines
        while j < N and text[j].isspace():
            j += 1
        comma = text.find(",", j)
        if comma == -1:
            i = brace_open + 1
            continue
        key = text[j:comma].strip()

        # Now find matching closing brace for the entry, tracking nesting
        depth = 0
        k = brace_open
        while k < N:
            c = text[k]
            if c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    end = k + 1
                    yield at, end, text[at:end], key
                    i = end
                    break
            k += 1
        else:
            # Unbalanced braces; stop
            return

def _has_field(entry_text: str, field_name: str) -> bool:
    # naive-but-effective: detect "annote =" (case-insensitive) anywhere in entry
    return re.search(rf"(?im)^\s*{re.escape(field_name)}\s*=", entry_text) is not None

def _insert_annote(entry_text: str, annote_value: str) -> str:
    """
    Insert `annote = {{...}},` before the final closing brace of the entry.
    Keeps indentation reasonable.
    """
    # Find indentation from an existing field line, else default two spaces
    m = re.search(r"(?m)^(\s+)\w+\s*=", entry_text)
    indent = m.group(1) if m else "  "

    # Ensure there is a comma before the closing brace (BibTeX wants commas between fields;
    # final comma is usually tolerated, but we’ll be polite).
    # We'll insert right before the last '}'.
    last_brace = entry_text.rfind("}")
    if last_brace == -1:
        return entry_text

    before = entry_text[:last_brace].rstrip()
    after = entry_text[last_brace:]

    # If before ends with ',' already, great; otherwise add one.
    if not before.endswith(","):
        before += ","

    # Double braces preserve the path as a single token better (helps line breaking).
    field = f"\n{indent}annote = {{{{{annote_value}}}}},\n"
    return before + field + after

def add_annote_paths_to_bib(
    bib_path: str | Path,
    pdf_dir: str | Path,
    *,
    make_backup: bool = True,
    overwrite: bool = True,
) -> dict[str, int]:
    """
    Append annote field to BibTeX entries whose key is like p1234 and whose PDF exists
    in `pdf_dir` with filename starting '1234.'.

    - Writes back to the .bib by default (overwrite=True).
    - Makes a .bak copy by default.
    Returns stats.
    """
    bib_path = Path(bib_path)
    pdf_dir = Path(pdf_dir)

    text = bib_path.read_text(encoding="utf-8", errors="replace")
    pdf_index = _build_pdf_index(pdf_dir)

    out_parts = []
    cursor = 0

    stats = {
        "entries_seen": 0,
        "matched_keys": 0,
        "already_had_annote": 0,
        "pdf_not_found": 0,
        "annote_added": 0,
    }

    for start, end, entry, key in _iter_bib_entries(text):
        stats["entries_seen"] += 1
        out_parts.append(text[cursor:start])
        cursor = end

        m = re.fullmatch(r"p(\d+)", key.strip())
        if not m:
            out_parts.append(entry)
            continue

        stats["matched_keys"] += 1
        number = int(m.group(1))

        if _has_field(entry, "annote"):
            stats["already_had_annote"] += 1
            out_parts.append(entry)
            continue

        pdf_path = pdf_index.get(number)
        if not pdf_path:
            stats["pdf_not_found"] += 1
            out_parts.append(entry)
            continue

        # Use forward slashes for hyperref friendliness on Windows
        annote_value = pdf_path.resolve().as_posix()

        new_entry = _insert_annote(entry, annote_value)
        out_parts.append(new_entry)
        stats["annote_added"] += 1

    out_parts.append(text[cursor:])
    new_text = "".join(out_parts)

    if overwrite:
        if make_backup:
            backup = bib_path.with_suffix(bib_path.suffix + ".bak")
            backup.write_text(text, encoding="utf-8", errors="replace")
        bib_path.write_text(new_text, encoding="utf-8", errors="replace")

    return stats


stats = add_annote_paths_to_bib(
    bib_path=r"C:\Users\mariosg\OneDrive - NTNU\FILES\workTips\✍Writing\BIBTEX.bib",
    pdf_dir=r"C:\Users\mariosg\OneDrive - NTNU\FILES\workTips\Literature",
)
print(stats)