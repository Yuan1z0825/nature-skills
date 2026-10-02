from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from support import SCRIPTS


class ConsolePortabilityTests(unittest.TestCase):
    def test_page_qa_json_is_ascii_safe_on_legacy_windows_codepage(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            page = Path(name) / "中文页面"
            page.mkdir()
            env = os.environ.copy()
            env["PYTHONIOENCODING"] = "cp1252"
            result = subprocess.run(
                [sys.executable, str(SCRIPTS / "run_image2ppt_qa.py"), str(page)],
                env=env,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 2, result.stderr.decode("utf-8", errors="replace"))
            report = json.loads(result.stdout.decode("ascii"))
            self.assertEqual(report["page_dir"], str(page.resolve()))


if __name__ == "__main__":
    unittest.main()
