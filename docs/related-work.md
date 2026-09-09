# Related work

This is **not** a greenfield category. Several tools already page you when an AI coding agent finishes or waits. What was missing (and what this repo is for) is a **small, MIT, notify-only Cursor hook** aimed at the Warp CLI prompt **Run this MCP tool?** plus a write-up of *why* Warp's own agent notifications do not cover that prompt.

## Closest open source

| Project | Link | Overlap | Gap vs this repo |
| --- | --- | --- | --- |
| **cursor-attention-beep** | https://github.com/aRealGem/cursor-attention-beep | Observe-only Cursor hooks; optional `beforeMCPExecution`; macOS sound; optional `osascript` / `terminal-notifier` | MCP is **opt-in** because it beeps on every MCP call, not only stalled approvals. No Warp OSC 777 path. |
| **cursor-notify** | https://github.com/nathan-folsom/cursor-notify | `~/.cursor/hooks.json` + native OS notifications | Hooks `stop`, `sessionStart`/`End`, `postToolUseFailure`, `preCompact` — **not** MCP/shell approval. |
| **agent-notify** (collindjohnson) | https://github.com/collindjohnson/agent-notify | Multi-agent desktop notify; Cursor via `stop` + a `cursor-notify` CLI wrapper | Cursor path is **task complete**. Claude gets `permission_prompt`; Cursor MCP TUI is not first-class. |
| **agent-notify** (cfngc4594) | https://github.com/cfngc4594/agent-notify | Sound / macOS / voice / ntfy for Claude, Cursor, Codex | Explicitly installs Cursor **`stop` only** for cross-tool consistency. |
| **code-notify** | https://github.com/mylee04/code-notify | Ancestor of collindjohnson/agent-notify | Same family: completion-oriented. |
| **johnlindquist/cursor-hooks** | https://github.com/johnlindquist/cursor-hooks | Typed payloads for `beforeMCPExecution` | Library / examples, not a pager. |
| **hookshot** | https://github.com/CorridorSecurity/hookshot | Go SDK including Cursor MCP hooks | Policy/control plane, not Warp notifications. |

## Closest commercial / closed

| Product | Link | Notes |
| --- | --- | --- |
| **AI Done Now** | https://www.aidonenow.com/cursor-agent-notifications | Paid macOS menu bar. Claims Cursor finish **and** shell/MCP permission banners. Zero-config, not OSS. |
| **AgentNotch** | https://www.agentnotch.app/ | Paid notch/menu-bar monitor for Claude / Cursor / Codex, including approvals. Not OSS. |
| **Voxlert** | https://github.com/settinghead/voxlert | Voice (TTS) when sessions need input. Different UX. |

## First-party (not Cursor CLI in Warp)

| Surface | Link | Covers this prompt? |
| --- | --- | --- |
| Warp desktop notifications | https://docs.warp.dev/terminal/more-features/notifications/ | Long commands and password prompts. Custom TUIs often missed. Warp must be in the **background**. |
| Warp agent notifications | https://docs.warp.dev/agents/capabilities/agent-notifications/ | Warp Agent, Claude Code (plugin), Codex, OpenCode. **Not Cursor CLI.** |
| Warp OSC 9 / 777 | same desktop-notifications doc | Generic escape sequences any process can emit if they hit the PTY. |
| Cursor IDE notifications | Settings → search “notifications” | Desktop Agent Chat, not the Warp `agent` TUI. |
| Cursor hooks | https://cursor.com/docs/hooks | The extension point this repo uses. |
| Cursor MCP approvals | https://cursor.com/docs/mcp | Allowlist / Auto-review. Orthogonal: fewer prompts vs paging you for remaining prompts. |
| Forum: CLI needs-input notify | https://forum.cursor.com/t/notification-when-a-cli-agent-needs-input/152166 | Feature request; people currently bolt on third-party tools. |

## When to use what

- **You run Claude Code in Warp** → install Warp's Claude plugin; do not start here.
- **You want “agent finished” for many CLIs** → [collindjohnson/agent-notify](https://github.com/collindjohnson/agent-notify).
- **You want a beep on turn-end / sudo-ish shells, MCP optional** → [cursor-attention-beep](https://github.com/aRealGem/cursor-attention-beep).
- **You want a paid click-to-focus Mac app** → AI Done Now or AgentNotch.
- **You run Cursor CLI in Warp and stall on MCP/shell `y`/`Tab`/`n`** → this repo.
