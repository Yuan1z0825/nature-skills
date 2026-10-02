from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from support import SCRIPTS, build_page, complete_visual_review_evidence, filled_arrow_manifest

sys.path.insert(0, str(SCRIPTS))
from visual_review_evidence import expected_page, validate_evidence  # noqa: E402


class VisualReviewRuntimeTests(unittest.TestCase):
    """Integration tests that require a real PowerPoint or LibreOffice renderer."""

    def test_generic_review_notes_do_not_pass_without_structured_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            page = Path(name)
            filled_arrow_manifest(page)
            build_page(page)
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "run_image2ppt_qa.py"),
                    str(page),
                    "--visual-review-status",
                    "reviewed",
                    "--visual-review-notes",
                    "looks good",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            report = json.loads((page / "image2ppt_qa.json").read_text(encoding="utf-8"))
            self.assertFalse(report["passed"])
            self.assertTrue(any("visual review evidence" in error for error in report["errors"]))

    def test_evidence_hashes_bind_review_to_current_render(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            page = Path(name)
            manifest_path = filled_arrow_manifest(page)
            build_page(page)
            pending = subprocess.run(
                [sys.executable, str(SCRIPTS / "run_image2ppt_qa.py"), str(page)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(pending.returncode, 2, pending.stdout + pending.stderr)
            evidence = page / "visual-review-evidence.json"
            complete_visual_review_evidence(
                page / "visual-review-evidence.template.json", evidence
            )
            payload = json.loads(evidence.read_text(encoding="utf-8"))
            payload["pages"][0]["rendered_sha256"] = "0" * 64
            evidence.write_text(json.dumps(payload), encoding="utf-8")
            expected = [
                expected_page(
                    page_id=page.name,
                    source=page / "source.png",
                    rendered=page / "render" / "rendered.png",
                    manifest=json.loads(manifest_path.read_text(encoding="utf-8")),
                )
            ]
            _payload, errors = validate_evidence(evidence, expected)
            self.assertTrue(any("rendered_sha256" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
