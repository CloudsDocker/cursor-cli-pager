# Contributing

This project is a tiny, observe-only Cursor hook. Keep it that way.

## Rules

- Never auto-approve MCP or shell tools. Stdout must remain `{"permission":"allow"}` only so Cursor's own prompt still appears.
- Never print OSC sequences or log noise on stdout. Cursor parses stdout as hook JSON.
- Prefer stdlib Python. No npm runtime for the hook itself.

## Checks

```bash
python3 -m unittest discover -s tests -v
python3 -m py_compile hooks/notify-approval.py
```

## Docs

Setup and technology write-ups live in `docs/`. Update them when hook events, Warp OSC behavior, or Cursor permission semantics change.
