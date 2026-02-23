import sys
import urllib.parse
import webbrowser
import time
from pathlib import Path
import json

def print_msg(msg, dt = 2):
    if IN_DEBUG_MODE:
        print(msg)
        time.sleep(dt)

# --- configure ---
IN_DEBUG_MODE = False
VAULT = "workTips"  # must match Obsidian vault name exactly
note_map_path = Path(__file__).resolve().parent / "note_map.json"

with open(note_map_path, "r", encoding="utf-8") as f:
    NOTE_MAP = json.load(f)

def open_obsidian_note(vault: str, note_path: str, block_id: str = None) -> None:
    uri = (
        "obsidian://open?"
        f"vault={urllib.parse.quote(vault)}&"
        f"file={urllib.parse.quote(note_path)}"
        f"#{urllib.parse.quote('^' + block_id)}"
    )
    print_msg(f"Opening Obsidian note with URI: {uri}")
    webbrowser.open(uri)


def obsidian_open_block(vault: str, note_path: str, block_id: str) -> str:
    # 1) Obsidian wants URL-style forward slashes
    note_path = note_path.replace("\\", "/")

    # 2) block_id can be "block1" or "^block1" — normalize it
    if not block_id.startswith("^"):
        block_id = "^" + block_id

    uri = (
        "obsidian://open?"
        f"vault={urllib.parse.quote(vault)}&"
        f"file={urllib.parse.quote(note_path)}"
        f"#{urllib.parse.quote(block_id, safe='^')}"  # keep caret unescaped
    )
    print_msg(f"Opening Obsidian note with URI: {uri}")
    return uri


def main(argv):
    # print_msg("Got inside main...")
    if len(argv) < 2:
        print("No command given.")
        return 1

    cmd = argv[1]
    # print_msg(f"Received command: {cmd}")

    if cmd.startswith("runNote:"):
        print_msg("Running note command...")
        key = cmd.split(":", 1)[1]
        note = NOTE_MAP.get(key).replace("C:\\Users\\mariosg\\OneDrive - NTNU\\FILES\\workTips\\", "")
        print_msg("Opening note: " + str(note))
        if not note:
            print(f"Unknown note key: {key}")
            return 2
        open_obsidian_note(VAULT, note, block_id='block1')
        # obsidian_open_block(VAULT, note, 'block1')

        return 0

    print(f"Unknown command: {cmd}")
    return 3

if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
