from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from support import SCRIPTS, SKILL_ROOT

sys.path.insert(0, str(SCRIPTS))
from runtime_paths import (  # noqa: E402
    CLI_ENTRY,
    RUNTIME_ROOT,
    image2ppt_command,
    image2ppt_runtime_script,
    required_runtime_files,
    runtime_path_report,
)


class RuntimePathTests(unittest.TestCase):
    def test_every_declared_local_resource_exists(self) -> None:
        missing = {name: path for name, path in required_runtime_files().items() if not path.is_file()}
        self.assertEqual(missing, {})

    def test_runtime_probe_uses_only_local_owners(self) -> None:
        report = runtime_path_report()
        self.assertEqual(Path(report["cli_entry"]), CLI_ENTRY)
        self.assertEqual(Path(report["runtime_root"]), RUNTIME_ROOT)
        self.assertTrue(all(item["exists"] for item in report["files"].values()))

    def test_runtime_probe_parses_complete_doctor_json(self) -> None:
        result = subprocess.run(
            [*image2ppt_command(), "doctor", "--json"],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = json.loads(result.stdout)
        self.assertTrue(report["ok"])
        self.assertIn(report["ocr"]["selection"], {"paddleocr-vl", "builtin-ink"})

    def test_command_is_fixed_to_source_tree_cli(self) -> None:
        poisoned = {
            "IMAGE2PPT_COMMAND": "/tmp/not-used",
            "IMAGE2PPT_SKILL_ROOT": "/tmp/not-used",
            "PYTHONPATH": "/tmp/not-used",
        }
        with patch.dict(os.environ, poisoned, clear=False):
            command = image2ppt_command()
        self.assertEqual(command, [sys.executable, str(SKILL_ROOT / "cli" / "image2ppt" / "cli.py")])

    def test_runtime_path_cannot_escape_local_runtime(self) -> None:
        with self.assertRaises(ValueError):
            image2ppt_runtime_script("../../outside.py")
        self.assertEqual(image2ppt_runtime_script("main.py").parent, RUNTIME_ROOT)


if __name__ == "__main__":
    unittest.main()
