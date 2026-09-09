# Setup guide: page yourself when Cursor CLI asks to run a tool

Audience: Mac + [Warp](https://www.warp.dev/) + Cursor CLI (`agent`), with MCP servers that still prompt **Run this MCP tool?**

This does not grant the tool permission. It only pings Notification Center (and Warp, when the PTY sees OSC 777) so you can walk back and press `y`, Tab, or `n`.

## 0. Decide if you need this repo

Read [related work](related-work.md) first.

Skip this repo if:

- You already use Warp Agent / Claude Code / Codex / OpenCode and Warp's [agent notifications](https://docs.warp.dev/agents/capabilities/agent-notifications/) cover you.
- You only care that the **desktop Cursor app** finished a turn (enable Cursor Settings → notifications).
- You want a paid menu-bar app: [AI Done Now](https://www.aidonenow.com/cursor-agent-notifications) or [AgentNotch](https://www.agentnotch.app/).

Stay here if Warp is sitting on **Run this MCP tool?** / **Run (once) (y)** and you were in Slack.

## 1. macOS notification permission

1. System Settings → Notifications → **Warp**: Banners or Alerts, sounds on.
2. After the first `osascript` test, also allow **Script Editor** (or whatever macOS attributes the `display notification` to).
3. Turn off Focus / Do Not Disturb while you validate.

## 2. Warp settings (still useful)

1. Warp → Settings → Features → **Session** → desktop notifications on.
2. Settings → Features → **Notifications** → long-running commands and password/input prompts on.
3. Remember: Warp's own banners usually fire only when Warp is **not** focused.

These catch `sleep 30` and some password prompts. They often **miss** Cursor's custom approval TUI. That is expected.

## 3. Install the hook

```bash
git clone https://github.com/CloudsDocker/cursor-cli-pager.git
cd cursor-cli-pager
chmod +x install.sh
./install.sh
```

`install.sh` copies `hooks/notify-approval.py` to `~/.cursor/hooks/` and merges two events into `~/.cursor/hooks.json`:

- `beforeMCPExecution`
- `beforeShellExecution`

User-level hooks run with cwd `~/.cursor/`, so the command is `./hooks/notify-approval.py`.

Restart the CLI session (`exit` then `agent`). Cursor reloads `hooks.json` on save, but a full restart is the reliable path.

## 4. Prove the notifier without waiting for Snowflake

```bash
python3 ~/.cursor/hooks/notify-approval.py <<'EOF'
{"hook_event_name":"beforeMCPExecution","mcp_server_name":"airflow-snowflake","tool_name":"sf_describe"}
EOF
```

Expect:

- stdout: `{"permission": "allow"}` only
- Glass sound
- a banner titled **Cursor MCP approval**

If stdout is mixed with OSC garbage, you are on a version that wrote the escape sequence to the wrong stream — upgrade the script; OSC must go to `/dev/tty` or stderr.

## 5. Prove it on a real stalled prompt

1. Start `agent` in Warp.
2. Ask for something that needs an MCP tool that is **not** allowlisted.
3. Switch to another app.
4. When the TUI shows **Run this MCP tool?**, you should already have a banner with `server: tool`.
5. Return to Warp: `y` once, Tab to allowlist for the session, or `n` / `p`.

## 6. Turn down noise

`beforeMCPExecution` runs before **every** MCP invocation the agent attempts, including tools you already allowlisted. If those run without a TUI, you will get extra banners.

Mitigations:

- Allowlist only the noisy read tools, and treat remaining prompts as the ones you want paged for.
- Or fork the hook and skip servers/tools you do not care about (still return `allow`).
- For sudo-class shells only, look at [cursor-attention-beep](https://github.com/aRealGem/cursor-attention-beep), which defaults MCP **off**.

Do **not** “fix” noise by returning hook `permission: allow` and expecting the TUI to disappear. Cursor's MCP allowlist and the hook channel are separate; hooks today are reliable for **deny**, not for skipping the prompt. See the [deep dive](02-deep-dive.md).

## 7. Uninstall

Run the automated uninstaller:

```bash
chmod +x uninstall.sh
./uninstall.sh
```

Or manually remove `./hooks/notify-approval.py` entries from `~/.cursor/hooks.json` and delete `~/.cursor/hooks/notify-approval.py`.

## 8. Publish this repo on GitHub

This workspace may start as a private cloud project. To open-source it:

1. In Cursor, use **Create repo** so the project has a public GitHub remote.
2. Confirm `LICENSE` is MIT and `docs/` is in `main`.
3. Optional: GitHub → Settings → Pages → deploy from `main` / `docs`.
