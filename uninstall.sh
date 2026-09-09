#!/usr/bin/env bash
# Uninstall Cursor approval notifications from ~/.cursor (user-level hooks).
set -euo pipefail

DEST="${HOME}/.cursor"
HOOKS_DIR="${DEST}/hooks"
TARGET_SCRIPT="${HOOKS_DIR}/notify-approval.py"
CONFIG="${DEST}/hooks.json"

python3 - <<'PY'
import json
from pathlib import Path

dest = Path.home() / ".cursor" / "hooks.json"
entry_cmd = "./hooks/notify-approval.py"
events = ("beforeMCPExecution", "beforeShellExecution")

if dest.exists():
    try:
        data = json.loads(dest.read_text())
        if isinstance(data, dict) and "hooks" in data and isinstance(data["hooks"], dict):
            hooks = data["hooks"]
            for event in events:
                if event in hooks and isinstance(hooks[event], list):
                    hooks[event] = [
                        item for item in hooks[event]
                        if not (isinstance(item, dict) and item.get("command") == entry_cmd)
                    ]
            dest.write_text(json.dumps(data, indent=2) + "\n")
            print(f"Cleaned hook references from {dest}")
    except Exception as e:
        print(f"Warning: Could not clean {dest}: {e}")
PY

if [ -f "${TARGET_SCRIPT}" ]; then
    rm -f "${TARGET_SCRIPT}"
    echo "Removed ${TARGET_SCRIPT}"
fi

echo
echo "Uninstalled successfully. Restart Cursor CLI (agent)."
