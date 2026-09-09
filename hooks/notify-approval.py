#!/usr/bin/env python3
"""Notify macOS (and Warp) when Cursor is about to prompt for tool approval.

Cursor CLI still shows "Run this MCP tool?" / "Run this command?" in the
terminal. This hook does not auto-approve anything. It only pings you so you
can return to Warp and press y / Tab / n.

Stdin: JSON payload from Cursor (beforeMCPExecution or beforeShellExecution).
Stdout: JSON permission response. Must stay allow so we never block the agent.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from typing import Any


def read_payload() -> dict[str, Any]:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return {"_raw": raw[:400]}
    return data if isinstance(data, dict) else {"_raw": raw[:400]}


def summarize(payload: dict[str, Any]) -> tuple[str, str]:
    event = str(payload.get("hook_event_name") or "")
    tool = str(payload.get("tool_name") or "").strip()
    server = str(
        payload.get("mcp_server_name")
        or payload.get("server")
        or ""
    ).strip()
    command = str(payload.get("command") or "").strip()

    if server and tool:
        title = "Cursor MCP approval"
        body = f"{server}: {tool}"
    elif tool:
        title = "Cursor MCP approval"
        body = tool
    elif command:
        title = "Cursor command approval"
        snippet = command.replace("\n", " ")
        if len(snippet) > 140:
            snippet = snippet[:137] + "..."
        body = snippet
    elif event:
        title = "Cursor needs approval"
        body = event
    else:
        title = "Cursor needs approval"
        body = "A tool is waiting in Warp. Press y, Tab, or n."
    return title, body


def emit_warp_osc(title: str, body: str) -> None:
    """Warp desktop notification via OSC 777.

    Never write this to stdout. Cursor parses stdout as hook JSON.
    Prefer /dev/tty so Warp sees the sequence on the same PTY as `agent`.
    """
    safe_title = title.replace(";", " ").replace("\n", " ")
    safe_body = body.replace(";", " ").replace("\n", " ")
    sequence = f"\033]777;notify;{safe_title};{safe_body}\007"
    encoded = sequence.encode("utf-8", errors="replace")
    try:
        fd = os.open("/dev/tty", os.O_WRONLY)
    except OSError:
        fd = None
    if fd is not None:
        try:
            if os.isatty(fd):
                os.write(fd, encoded)
                return
        finally:
            os.close(fd)
    try:
        if sys.stderr.isatty():
            sys.stderr.buffer.write(encoded)
            sys.stderr.flush()
    except OSError:
        pass


def macos_notify(title: str, body: str) -> None:
    if sys.platform != "darwin":
        return
    script = (
        'display notification {body} with title {title} sound name "Glass"'
    ).format(
        title=json.dumps(title),
        body=json.dumps(body),
    )
    try:
        subprocess.run(
            ["osascript", "-e", script],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=5,
        )
    except (OSError, subprocess.TimeoutExpired):
        pass

    afplay = shutil.which("afplay")
    sound = "/System/Library/Sounds/Glass.aiff"
    if afplay and os.path.exists(sound):
        try:
            subprocess.Popen(
                [afplay, sound],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except OSError:
            pass


def main() -> int:
    payload = read_payload()
    title, body = summarize(payload)
    emit_warp_osc(title, body)
    macos_notify(title, body)
    # Fail-open: never deny. Cursor's own approval UI still applies.
    sys.stdout.write(json.dumps({"permission": "allow"}) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
