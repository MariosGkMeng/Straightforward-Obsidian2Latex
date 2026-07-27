#!/usr/bin/env python3
"""
collect_figures.py

Scan a .tex file for \\includegraphics commands, collect absolute paths,
copy the image files to a local "project folder" (outside OneDrive),
and optionally write a rewritten .tex that points to the copied images.

Usage:
  python collect_figures.py path/to/main.tex --out "D:/latex_projects/paper3"
  python collect_figures.py path/to/main.tex --out "D:/latex_projects/paper3" --rewrite

Notes:
- Designed for Windows-style absolute paths, but also works with POSIX.
- Handles \\includegraphics[...]{...} and \\includegraphics{...}
- Handles paths wrapped in double quotes: {"C:/path with spaces/img.png"}
- Copies with collision-safe names (adds short hash when needed).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
from pathlib import Path
from typing import Dict, List, Tuple
from path_searching import *

INCLUDEGRAPHICS_RE = re.compile(
    r"""
    \\includegraphics
    (?:\s*\[[^\]]*\])?          # optional [key=val,...]
    \s*\{                       # opening brace
    \s*                         # optional whitespace
    (?P<path>
        "(?:[^"\\]|\\.)*"       # "quoted string" (allow escaped quotes)
        |
        (?:[^{}]|\\\{|\\\})+    # or unquoted content (tolerant)
    )
    \s*                         # optional whitespace
    \}                          # closing brace
    """,
    re.VERBOSE,
)


def unquote(s: str) -> str:
    s = s.strip()
    if len(s) >= 2 and s[0] == '"' and s[-1] == '"':
        # unescape \" and \\ inside the quoted string
        inner = s[1:-1]
        inner = inner.replace(r"\\", "\\").replace(r"\"", '"')
        return inner
    return s


def is_absolute_path(p: str) -> bool:
    # Windows drive: C:/... or C:\...
    if re.match(r"^[A-Za-z]:[\\/]", p):
        return True
    # UNC: \\server\share\...
    if p.startswith("\\\\"):
        return True
    # POSIX absolute: /...
    if p.startswith("/"):
        return True
    return False


def find_includegraphics_paths(tex_text: str) -> List[str]:
    paths: List[str] = []
    for m in INCLUDEGRAPHICS_RE.finditer(tex_text):
        raw = m.group("path")
        p = unquote(raw).strip()

        # LaTeX sometimes uses forward slashes on Windows: keep as-is
        # but normalize later via Path.
        paths.append(p)

    # Deduplicate while preserving order
    seen = set()
    unique = []
    for p in paths:
        if p not in seen:
            seen.add(p)
            unique.append(p)
    return unique


def short_hash(s: str, n: int = 8) -> str:
    return hashlib.sha1(s.encode("utf-8", errors="ignore")).hexdigest()[:n]


def safe_target_name(src_path: str, used_names: set[str]) -> str:
    """
    Choose a filename for the copied file. If basename collides, append a short hash.
    """
    src = Path(src_path)
    base = src.name
    if base not in used_names:
        used_names.add(base)
        return base

    stem = src.stem
    suffix = src.suffix
    h = short_hash(src_path, 8)
    candidate = f"{stem}__{h}{suffix}"
    i = 2
    while candidate in used_names:
        candidate = f"{stem}__{h}_{i}{suffix}"
        i += 1
    used_names.add(candidate)
    return candidate


def copy_figures(
    abs_paths: List[str],
    figures_dir: Path,
) -> Tuple[Dict[str, str], List[str]]:
    """
    Copy each absolute path into figures_dir.
    Returns:
      mapping: original_path -> copied_relative_path (e.g. figures/foo.png)
      missing: list of paths not found
    """
    figures_dir.mkdir(parents=True, exist_ok=True)
    used_names: set[str] = set()

    mapping: Dict[str, str] = {}
    missing: List[str] = []

    for p in abs_paths:
        # Only copy absolute paths (your use case)
        if not is_absolute_path(p):
            continue

        src = Path(p)
        if not src.exists():
            missing.append(p)
            continue

        dst_name = safe_target_name(p, used_names)
        dst = figures_dir / dst_name

        # Copy (preserve metadata)
        shutil.copy2(src, dst)

        mapping[p] = (Path("figures") / dst_name).as_posix()

    return mapping, missing


def rewrite_tex(tex_text: str, mapping: Dict[str, str]) -> str:
    """
    Rewrite includegraphics{<abs>} to includegraphics{<mapped rel>}.
    Keeps the original quoting style (quoted/unquoted) when possible.
    """

    def repl(m: re.Match) -> str:
        raw = m.group("path")
        original = unquote(raw).strip()
        if original in mapping:
            new_path = mapping[original]
            # Keep quotes if the original was quoted OR if new path contains spaces.
            needs_quotes = (raw.strip().startswith('"') and raw.strip().endswith('"')) or (" " in new_path)
            if needs_quotes:
                new_raw = f"\"{new_path}\""
            else:
                new_raw = new_path

            # Replace only the {...} content for safety
            start, end = m.span("path")
            return m.group(0)[: (start - m.start())] + new_raw + m.group(0)[(end - m.start()) :]

        return m.group(0)

    return INCLUDEGRAPHICS_RE.sub(repl, tex_text)


def move_project(tex: str, out: str, PARS: dict, rewrite: bool = False) -> None:

    tex_path = Path(tex).expanduser().resolve()
    if not tex_path.exists():
        raise SystemExit(f"TeX file not found: {tex_path}")

    out_dir = Path(out).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    figures_dir = out_dir / "figures"

    tex_text = tex_path.read_text(encoding="utf-8", errors="replace")
    paths = find_includegraphics_paths(tex_text)
    
    used_absolute_paths = not PARS['⚙']['figures']['use_overleaf_all_in_the_same_folder']
    if not used_absolute_paths:
        paths = [get_embedded_reference_path(Path(p)._cparts[-1],PARS) for p in paths]
        
    paths = [p for p in paths if p]  # filter out None or empty paths
    # Save detected list (all, including relative)
    (out_dir / "figures_list.txt").write_text("\n".join(paths) + "\n", encoding="utf-8")

    abs_paths = [p for p in paths if is_absolute_path(p)]
    mapping, missing = copy_figures(abs_paths, figures_dir)

    (out_dir / "figmap.json").write_text(json.dumps(mapping, indent=2), encoding="utf-8")

    if missing:
        (out_dir / "missing_figures.txt").write_text("\n".join(missing) + "\n", encoding="utf-8")
        print(f"[!] Missing {len(missing)} figure(s). See: {out_dir / 'missing_figures.txt'}")
    else:
        print("[✓] All figures found and copied.")

    print(f"[✓] Copied {len(mapping)} figure(s) to: {figures_dir}")

    if rewrite:
        rewritten = rewrite_tex(tex_text, mapping)
        rewritten = rewritten.replace("figures\\", "figures/")

        # Add \graphicspath if user wants (optional): we won’t inject it automatically
        # because you may already set it elsewhere.

        out_tex = out_dir / tex_path.name
        out_tex.write_text(rewritten, encoding="utf-8")
        print(f"[✓] Wrote rewritten TeX to: {out_tex}")
        print("    Compile THIS file for fastest builds (local figures).")


if __name__ == "__main__":
    # ===== EDIT THESE =====
    tex_file = r"C:\Users\mariosg\OneDrive - NTNU\FILES\workTips\✍Writing\✍⌛writing--THESIS--Paper-3--Results.tex"
    output_folder = r"C:\Users\mariosg\latex_projects\paper3_results"
    rewrite_tex_file = True
    # =======================
    
    move_project(
        tex=tex_file,
        out=output_folder,
        rewrite=rewrite_tex_file,
    )