#!/usr/bin/env python3
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "hooks" / "notify-approval.py"

_spec = importlib.util.spec_from_file_location("notify_approval", SCRIPT)
na = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(na)


class SummarizeTests(unittest.TestCase):
    def test_mcp_server_and_tool(self):
        title, body = na.summarize(
            {
                "hook_event_name": "beforeMCPExecution",
                "mcp_server_name": "airflow-snowflake",
                "tool_name": "sf_describe",
            }
        )
        self.assertEqual(title, "Cursor MCP approval")
        self.assertEqual(body, "airflow-snowflake: sf_describe")

    def test_shell_truncation(self):
        title, body = na.summarize(
            {"command": "a" * 200, "hook_event_name": "beforeShellExecution"}
        )
        self.assertEqual(title, "Cursor command approval")
        self.assertTrue(body.endswith("..."))
        self.assertLessEqual(len(body), 140)

    def test_empty_payload(self):
        title, body = na.summarize({})
        self.assertEqual(title, "Cursor needs approval")
        self.assertIn("Warp", body)


class ProcessTests(unittest.TestCase):
    def test_stdout_is_allow_json_only(self):
        payload = json.dumps(
            {
                "hook_event_name": "beforeMCPExecution",
                "mcp_server_name": "airflow-snowflake",
                "tool_name": "sf_describe",
            }
        )
        proc = subprocess.run(
            [sys.executable, str(SCRIPT)],
            input=payload,
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertEqual(json.loads(proc.stdout.strip()), {"permission": "allow"})


if __name__ == "__main__":
    unittest.main()
