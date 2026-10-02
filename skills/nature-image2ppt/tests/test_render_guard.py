from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image

from support import SCRIPTS
from render_image2ppt_qa import render_powerpoint


class RenderGuardTests(unittest.TestCase):
    def test_powerpoint_command_releases_deck_before_application(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            completed = subprocess.CompletedProcess([], 1, "", "fixture")
            with (
                patch("render_image2ppt_qa.shutil.which", return_value="powershell.exe"),
                patch("render_image2ppt_qa.subprocess.run", return_value=completed),
            ):
                _rendered, raw = render_powerpoint(root / "page.pptx", root / "render", 1)

            script = raw["command"][-1]
            self.assertLess(script.index("$app=$null;$deck=$null;"), script.index("try{"))
            self.assertIn("finally{if($null -ne $deck)", script)
            self.assertLess(script.index("$deck.Close()"), script.index("ReleaseComObject($deck)"))
            self.assertLess(script.index("ReleaseComObject($deck)"), script.index("$app.Quit()"))
            self.assertLess(script.index("$app.Quit()"), script.index("ReleaseComObject($app)"))

    def test_source_image_cannot_be_reused_as_render_proof(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            source = root / "source.png"
            Image.new("RGB", (320, 180), "white").save(source)
            pptx = root / "page.pptx"
            pptx.write_bytes(b"not-needed-before-source-reuse-guard")
            report = root / "render_report.json"
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "render_image2ppt_qa.py"),
                    str(pptx),
                    "--out-dir",
                    str(root / "render"),
                    "--report",
                    str(report),
                    "--source",
                    str(source),
                    "--existing-rendered",
                    str(source),
                ],
                text=True,
                capture_output=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("source reuse", report.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
