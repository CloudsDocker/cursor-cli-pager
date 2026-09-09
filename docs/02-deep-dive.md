# Deep dive: why a stalled MCP prompt is invisible, and how this pager works

This is the technology note behind [the setup guide](01-setup-guide.md). It is written for people who will be asked in an interview (or an incident review) *why the agent sat on `sf_describe` for twenty minutes*.

## 1. Three permission planes that do not share a brain

When Cursor CLI prints **Run this MCP tool?**, at least three systems may have an opinion:

| Plane | Config | What it actually does |
| --- | --- | --- |
| **MCP / agent allowlist** | Cursor Settings → Tools & MCP, Auto-review / Allowlist, `permissions.json` `mcpAllowlist`, CLI `permissions.allow` | Decides whether the **TUI approval** appears. |
| **Hooks** | `~/.cursor/hooks.json` `beforeMCPExecution` / `beforeShellExecution` | Spawn a process, JSON on stdin/stdout. Can **deny**. Returning `allow` does **not** currently override the MCP prompt. |
| **Terminal emulator** | Warp notifications, OSC 9/777, macOS Notification Center | Knows about PTYs, passwords, and (for some agents) structured “Request” events. Does not parse Cursor's Ink/TUI prompt unless something emits a signal. |

Cursor staff have stated the split explicitly in forum threads: hook `allow`/`ask` and the MCP allowlist are independent; hooks are the **deny** tool. Citations:

- https://forum.cursor.com/t/hooks-return-allow-but-mcp-tool-still-requires-manual-approval-gets-skipped/155434
- https://forum.cursor.com/t/the-cursor-hooks-did-not-execute-as-expected/155711

**Design implication:** a pager must be *observe-only*. If the hook denies, you “fixed” the stall by breaking the agent. If the hook tries to allow, you did not remove the TUI. If the hook notifies and returns `allow`, the human still owns `ODS.HRIS.EMPLOYEE`.

## 2. There is no `approvalPromptShown` event

Cursor documents agent hooks at https://cursor.com/docs/hooks. The events that *look* like “needs you” are:

- `beforeMCPExecution` / `beforeShellExecution` — **about to run**, which is when the TUI usually appears if the tool is not allowlisted.
- `stop` — turn ended; the agent may be idle because it **finished**, not because it is blocked.
- `postToolUseFailure` — error, not a `y/n` gate.

Claude Code is different: it has `Notification` (`idle_prompt`) and `PermissionRequest`. That is why Warp ships a [Claude plugin](https://github.com/warpdotdev/claude-code-warp) and why [agent-notify](https://github.com/collindjohnson/agent-notify) can key off `permission_prompt` for Claude but only `stop` for Cursor.

**Approximation error:** `beforeMCPExecution` also fires for allowlisted tools that never show a prompt. [cursor-attention-beep](https://github.com/aRealGem/cursor-attention-beep) therefore makes MCP **opt-in**. This repo keeps MCP **on** because the motivating bug is a stalled MCP TUI in Warp. If your allowlist is wide, expect chatter and filter in the script.

## 3. Hook I/O is a security-sensitive protocol

Cursor spawns the command, writes one JSON object to stdin, and reads stdout as a JSON decision:

```json
{
  "hook_event_name": "beforeMCPExecution",
  "mcp_server_name": "airflow-snowflake",
  "tool_name": "sf_describe",
  "tool_input": "{\"table\":\"ODS.HRIS.EMPLOYEE\"}"
}
```

Stdout must be exactly:

```json
{"permission": "allow"}
```

Anything else is a protocol bug:

- Extra `print()` debugging → Cursor may ignore the hook or fail open.
- OSC 777 on stdout → you injected `ESC ] 777 ; ... BEL` into the parser.
- `failClosed: true` (not used here) would **block the tool** if the script crashed. This pager is fail-open on purpose.

User hooks run from `~/.cursor/`. Project hooks run from the repo root. Mixing those paths is the usual “command not found” outage.

Exit code `2` is treated as deny (Claude-compatible). This script always exits `0`.

## 4. Warp's notification stack

Warp has **two** products that look like one:

### 4.1 Session / command notifications

Documented at https://docs.warp.dev/terminal/more-features/notifications/

Triggers: command ran longer than N seconds; process looks like a **password** prompt. Delivery: native banner **only if another app is focused**.

Cursor's approval UI is a full-screen TUI (`Run this MCP tool?`, arrow keys, Tab allowlist). It is not `Password:` on stdin. Warp has no reason to classify it as a password prompt.

### 4.2 Agent notifications

Documented at https://docs.warp.dev/agents/capabilities/agent-notifications/

Supported: Warp Agent, Claude Code (plugin), Codex (`notification_condition`), OpenCode (plugin).

Cursor CLI is absent. The [Claude plugin](https://github.com/warpdotdev/claude-code-warp) talks to Warp with **OSC 777** and a JSON payload Warp parses as Complete / Request / Error. Cursor does not emit that schema.

Foreground caveat (open issue): https://github.com/warpdotdev/warp/issues/8439 — even first-party agent banners often do not appear while Warp itself is focused (other tab included).

### 4.3 Escape sequences this repo uses

From Warp's docs:

- OSC 9: `ESC ] 9 ; <body> BEL`
- OSC 777: `ESC ] 777 ; notify ; <title> ; <body> BEL`

The hook process is **not** the PTY's foreground shell. Writing OSC to stdout is wrong (see §3). Writing to `/dev/tty` is the attempt to reach the same terminal Warp is rendering. If Cursor's hook sandbox has no TTY, OSC is dropped and **osascript still runs**. That is why Mac Notification Center is the primary channel and OSC is opportunistic.

`afplay /System/Library/Sounds/Glass.aiff` covers the case Warp is focused: you hear Glass even with no banner.

## 5. macOS Notification Center

`osascript` `display notification` is the stdlib path. Limitations:

- Attribution may be Script Editor, not Warp or Cursor, so users hunt the wrong app in System Settings.
- No reliable click-to-focus of the Warp tab (paid apps sell this).
- Focus modes swallow banners.

`terminal-notifier` is a better citizen (bundle id, click actions). This repo stays on osascript to avoid a brew dependency for a 100-line hook.

## 6. MCP tool approval UX in the CLI

The screenshot that started this project is Cursor CLI's MCP gate:

- **Run (once) (y)** — this call only
- **Allowlist MCP Tool (tab)** — session/server allowlist
- **Reject & propose changes (p)**
- **Skip (esc / n)**

Human-in-the-loop here is load-bearing for data tools (`ODS.HRIS.EMPLOYEE`). Paging is the SLO; auto-allow is a separate, explicit policy change.

MCP itself is just JSON-RPC tools + Cursor's client policy. Spec: https://modelcontextprotocol.io/

## 7. Failure modes (ops)

| Symptom | Likely cause |
| --- | --- |
| Silent stall, no banner | Hook not in `~/.cursor/hooks.json`; CLI not restarted; Focus mode; notifications denied for osascript |
| Banner on every MCP call | Tools already allowlisted; `beforeMCPExecution` is not “prompt shown” |
| Agent blocked / tools denied | Script printed non-JSON; `failClosed`; exit 2 |
| Warp banner never, Mac banner yes | OSC did not hit PTY; Warp in foreground |
| Duplicate pings | Also running cursor-notify `stop`, agent-notify, and this hook |

## 8. What a senior FDE should not build

Do not scrape the Warp pane for the string `Run this MCP tool?` as the primary design (brittle, privacy-hostile, races). That pattern shows up in multi-agent orchestration notes; it is a fallback, not a product.

Do not return hook `ask` and expect Cursor to honor it today.

Do not put secrets from `tool_input` into the notification body. This script shows **server + tool name** (or a truncated shell command), not table payloads.

## 9. Further reading

- Cursor hooks: https://cursor.com/docs/hooks
- Cursor CLI: https://cursor.com/docs/cli/overview
- Cursor MCP: https://cursor.com/docs/mcp
- Warp notifications: https://docs.warp.dev/terminal/more-features/notifications/
- Warp agent notifications: https://docs.warp.dev/agents/capabilities/agent-notifications/
- OSC 9 historical note: many terminals use it for “growl” style notify; Warp documents OSC 9 and OSC 777 explicitly.
