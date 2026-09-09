# cursor-approval-ping

Notify-only Cursor CLI hook: when Warp is sitting on **Run this MCP tool?** or a shell `y/n` gate, ping macOS Notification Center (and Warp via OSC 777). It does **not** auto-approve tools.

## Sample

![image](assets/pager.png)


This is a niche pager, not a new category. **Similar tools already exist** — read [docs/related-work.md](docs/related-work.md) before you adopt or publish a copy.

## Similar / prior art (start here)

Open source:

- https://github.com/aRealGem/cursor-attention-beep — closest: observe-only Cursor hooks, MCP optional because it fires on every MCP call
- https://github.com/nathan-folsom/cursor-notify — Cursor hooks for **task complete** / session / errors, not MCP approval
- https://github.com/collindjohnson/agent-notify — Claude/Codex/Gemini/Cursor; Cursor uses the **`stop`** hook
- https://github.com/cfngc4594/agent-notify — same idea; Cursor **`stop` only**
- https://github.com/mylee04/code-notify — parent of collindjohnson/agent-notify
- https://github.com/johnlindquist/cursor-hooks — hook payload types, not a pager

Commercial:

- https://www.aidonenow.com/cursor-agent-notifications — Mac menu bar, including Cursor MCP/shell permission
- https://www.agentnotch.app/ — notch/menu-bar status + approvals
- https://github.com/settinghead/voxlert — spoken alerts

First-party (does **not** cover Cursor CLI in Warp):

- https://docs.warp.dev/agents/capabilities/agent-notifications/ — Warp Agent, Claude Code, Codex, OpenCode
- https://forum.cursor.com/t/notification-when-a-cli-agent-needs-input/152166 — CLI needs-input is still a feature request

This repo exists because Warp does not treat Cursor CLI as a supported agent, and `stop`-hook notifiers miss the stalled MCP TUI.

## Docs (the “blog”)

| Piece | File |
| --- | --- |
| Setup | [docs/01-setup-guide.md](docs/01-setup-guide.md) |
| Deep dive (hooks, MCP vs allowlist, Warp OSC, Notification Center) | [docs/02-deep-dive.md](docs/02-deep-dive.md) |
| Landscape | [docs/related-work.md](docs/related-work.md) |

GitHub Pages: Settings → Pages → `main` / `/docs`.

## Install

```bash
chmod +x install.sh
./install.sh
```

Then restart `agent` in Warp. Test:

```bash
python3 ~/.cursor/hooks/notify-approval.py <<'EOF'
{"hook_event_name":"beforeMCPExecution","mcp_server_name":"airflow-snowflake","tool_name":"sf_describe"}
EOF
```

## Open-sourcing

Use Cursor’s **Create repo** control to put this on a public GitHub remote. The tree is already MIT-licensed (`LICENSE`). Do not treat this cloud workspace name as the public project name.

## Tests

```bash
python3 -m unittest discover -s tests -v
```

## License

MIT
