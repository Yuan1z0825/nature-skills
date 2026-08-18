from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from support import (
    SCRIPTS,
    build_page,
    complete_visual_review_evidence,
    image2ppt_command,
    filled_arrow_manifest,
    write_json,
)


class Image2PPTStateEndToEndTests(unittest.TestCase):
    def run_ok(self, command: list[str]) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(command, text=True, capture_output=True, check=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    def test_local_page_jobs_record_and_finalize(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            run = Path(name)
            page = run / "pages" / "page_001"
            manifest = filled_arrow_manifest(page)
            request = page / "page_request.json"
            write_json(
                request,
                {
                    "schema_version": 1,
                    "page_id": "page_001",
                    "page_index": 1,
                    "page_dir": str(page),
                    "source_image": str(page / "source.png"),
                    "slide": {"width": 13.333, "height": 7.5},
                    "content_box": {"left": 0, "top": 0, "width": 13.333, "height": 7.5},
                },
            )
            write_json(run / "notes_manifest.json", {"source": None, "notes": []})
            write_json(
                run / "deck_manifest.json",
                {
                    "schema_version": 1,
                    "run_id": "thin-profile-fixture",
                    "job_dir": str(run),
                    "page_count": 1,
                    "slide": {"width": 13.333, "height": 7.5},
                    "pages": [
                        {
                            "page_id": "page_001",
                            "page_index": 1,
                            "page_dir": "pages/page_001",
                            "source_image": "pages/page_001/source.png",
                            "manifest": "pages/page_001/manifest.json",
                            "validation": "pages/page_001/validation.json",
                        }
                    ],
                    "notes_manifest": "notes_manifest.json",
                    "output": "final/deck_edited.pptx",
                },
            )
            write_json(
                run / "page_jobs.json",
                {
                    "schema_version": 1,
                    "run_id": "thin-profile-fixture",
                    "run_status": "inputs_prepared",
                    "max_concurrent_pages": 1,
                    "pages": [
                        {
                            "page_id": "page_001",
                            "page_index": 1,
                            "status": "pending",
                            "page_dir": "pages/page_001",
                            "source": "pages/page_001/source.png",
                            "page_request": "pages/page_001/page_request.json",
                            "manifest": "pages/page_001/manifest.json",
                            "validation": "pages/page_001/validation.json",
                            "dispatch": None,
                            "result": None,
                            "accepted": False,
                        }
                    ],
                },
            )

            prompt = page / "worker-prompt.md"
            self.run_ok(
                [
                    sys.executable,
                    str(SCRIPTS / "build_page_worker_prompt.py"),
                    str(run),
                    "--page",
                    "page_001",
                    "--out",
                    str(prompt),
                ]
            )
            self.run_ok(
                [
                    *image2ppt_command(),
                    "run",
                    "dispatch",
                    str(run),
                    "--page",
                    "page_001",
                    "--agent-id",
                    "main",
                    "--prompt-file",
                    str(prompt),
                    "--local",
                ]
            )
            build_page(page)
            pending_page_qa = subprocess.run(
                [sys.executable, str(SCRIPTS / "run_image2ppt_qa.py"), str(page)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(pending_page_qa.returncode, 2, pending_page_qa.stdout + pending_page_qa.stderr)
            page_evidence = page / "visual-review-evidence.json"
            complete_visual_review_evidence(
                page / "visual-review-evidence.template.json", page_evidence
            )
            self.run_ok(
                [
                    sys.executable,
                    str(SCRIPTS / "run_image2ppt_qa.py"),
                    str(page),
                    "--visual-review-status",
                    "reviewed",
                    "--visual-review-evidence",
                    str(page_evidence),
                    "--visual-review-notes",
                    "fixture: source and render checked for arrow silhouette, direction, text, and bounds",
                ]
            )
            self.run_ok([*image2ppt_command(), "page", "contact-sheet", str(page)])
            write_json(
                page / "page_result.json",
                {
                    "page_manifest": "manifest.json",
                    "imagegen_jobs": "imagegen-jobs.json",
                    "page_pptx": "page.pptx",
                    "preview": "preview.png",
                    "contact_sheet": "split_assets_contact.png",
                    "validation": "validation.json",
                    "page_result": "page_result.json",
                },
            )
            self.run_ok(
                [
                    *image2ppt_command(),
                    "run",
                    "record",
                    str(run),
                    "--page",
                    "page_001",
                    "--agent-id",
                    "main",
                ]
            )
            self.run_ok([*image2ppt_command(), "run", "finalize", str(run)])
            pending_final_qa = subprocess.run(
                [sys.executable, str(SCRIPTS / "run_final_image2ppt_qa.py"), str(run)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(pending_final_qa.returncode, 2, pending_final_qa.stdout + pending_final_qa.stderr)
            final_evidence = run / "final" / "visual-review-evidence.json"
            complete_visual_review_evidence(
                run / "final" / "visual-review-evidence.template.json", final_evidence
            )
            self.run_ok(
                [
                    sys.executable,
                    str(SCRIPTS / "run_final_image2ppt_qa.py"),
                    str(run),
                    "--visual-review-status",
                    "reviewed",
                    "--visual-review-evidence",
                    str(final_evidence),
                    "--visual-review-notes",
                    "fixture: final rendered slide checked against source for arrow, text, and page geometry",
                ]
            )

            jobs = json.loads((run / "page_jobs.json").read_text(encoding="utf-8"))
            self.assertEqual(jobs["run_status"], "complete")
            self.assertEqual(jobs["pages"][0]["status"], "accepted")
            self.assertFalse((run / "image2ppt_jobs.json").exists())
            self.assertTrue((run / "final" / "image2ppt_qa.json").is_file())
            report_text = (run / "final" / "image2ppt_qa.json").read_text(encoding="utf-8")
            self.assertTrue(json.loads(report_text)["passed"])


if __name__ == "__main__":
    unittest.main()
