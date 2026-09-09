#!/usr/bin/env bash
# Install Cursor approval notifications into ~/.cursor (user-level hooks).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
DEST="${HOME}/.cursor"
HOOKS_DIR="${DEST}/hooks"
SRC_HOOK="${ROOT}/hooks/notify-approval.py"

mkdir -p "${HOOKS_DIR}"
cp "${SRC_HOOK}" "${HOOKS_DIR}/notify-approval.py"
chmod +x "${HOOKS_DIR}/notify-approval.py"

python3 - <<'PY'
import json
from pathlib import Path

dest = Path.home() / ".cursor" / "hooks.json"
entry = {"command": "./hooks/notify-approval.py"}
events = ("beforeMCPExecution", "beforeShellExecution")

if dest.exists():
    data = json.loads(dest.read_text())
else:
    data = {"version": 1, "hooks": {}}

if not isinstance(data, dict):
    data = {"version": 1, "hooks": {}}
hooks = data.setdefault("hooks", {})
if not isinstance(hooks, dict):
    hooks = {}
    data["hooks"] = hooks
data.setdefault("version", 1)

for event in events:
    items = hooks.get(event) or []
    if not isinstance(items, list):
        items = []
    already = any(
        isinstance(item, dict) and item.get("command") == entry["command"]
        for item in items
    )
    if not already:
        items.append(dict(entry))
    hooks[event] = items

dest.parent.mkdir(parents=True, exist_ok=True)
dest.write_text(json.dumps(data, indent=2) + "\n")
print(f"Updated {dest}")
PY

echo
echo "Installed. Next steps:"
echo "  1. Allow notifications for Warp (and Terminal/iTerm if you use those)."
echo "  2. In Warp: Settings → Features → Session → desktop notifications ON."
echo "  3. Restart Cursor CLI (agent) so it reloads ~/.cursor/hooks.json."
echo "  4. Test:  python3 ~/.cursor/hooks/notify-approval.py <<'EOF'"
echo '           {"hook_event_name":"beforeMCPExecution","mcp_server_name":"airflow-snowflake","tool_name":"sf_describe"}'
echo "           EOF"
