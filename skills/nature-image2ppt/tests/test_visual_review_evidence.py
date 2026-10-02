from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

from support import SCRIPTS, build_page, complete_visual_review_evidence, filled_arrow_manifest

sys.path.insert(0, str(SCRIPTS))
from visual_review_evidence import expected_page, validate_evidence, write_template  # noqa: E402


class VisualReviewEvidenceTests(unittest.TestCase):
    def test_template_requires_conditional_arrow_check(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            page = Path(name)
            manifest_path = filled_arrow_manifest(page)
            build_page(page)
            rendered = page / "preview.png"
            expected = [
                expected_page(
                    page_id="page_001",
                    source=page / "source.png",
                    rendered=rendered,
                    manifest=json.loads(manifest_path.read_text(encoding="utf-8")),
                )
            ]
            template = page / "template.json"
            write_template(template, expected)
            checks = json.loads(template.read_text(encoding="utf-8"))["pages"][0]["checks"]
            self.assertIn("arrow_geometry", checks)

    def test_evidence_paths_bind_review_to_current_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            page = Path(name)
            manifest_path = filled_arrow_manifest(page)
            build_page(page)
            expected = [
                expected_page(
                    page_id="page_001",
                    source=page / "source.png",
                    rendered=page / "preview.png",
                    manifest=json.loads(manifest_path.read_text(encoding="utf-8")),
                )
            ]
            evidence = page / "visual-review-evidence.json"
            write_template(evidence, expected)
            complete_visual_review_evidence(evidence, evidence)
            payload = json.loads(evidence.read_text(encoding="utf-8"))
            payload["pages"][0]["rendered"] = str(page / "unrelated.png")
            evidence.write_text(json.dumps(payload), encoding="utf-8")
            _payload, errors = validate_evidence(evidence, expected)
            self.assertTrue(any("rendered path" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
