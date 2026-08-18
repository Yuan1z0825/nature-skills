from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

from support import (
    build_deck,
    build_page,
    complete_visual_review_evidence,
    connector_manifest,
    filled_arrow_manifest,
    SCRIPTS,
    sha256_text,
    write_json,
)

from inspect_arrow_atomicity import inspect
from postprocess_manifest_arrows import postprocess_pptx, read_json


class ManifestArrowTests(unittest.TestCase):
    def test_connector_variants_are_one_native_object(self) -> None:
        for connector in ("straight", "elbow", "curve"):
            with self.subTest(connector=connector), tempfile.TemporaryDirectory() as name:
                page = Path(name)
                manifest_path = connector_manifest(page, connector)
                pptx = build_page(page)
                post = postprocess_pptx(pptx, [manifest_path], page / "postprocess.json")
                self.assertTrue(post["passed"], post)
                report = inspect([read_json(manifest_path)], pptx)
                self.assertTrue(report["passed"], report)
                self.assertEqual(report["summary"]["expected_arrows"], 1)
                self.assertEqual(report["arrows"][0]["pptx_object"]["kind"], "cxnSp")
                self.assertEqual(report["arrows"][0]["pptx_object"]["end_arrow"], "triangle")

    def test_filled_arrow_keeps_label_in_same_autoshape(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            page = Path(name)
            manifest_path = filled_arrow_manifest(page)
            pptx = build_page(page)
            first = postprocess_pptx(pptx, [manifest_path], page / "first.json")
            second = postprocess_pptx(pptx, [manifest_path], page / "second.json")
            self.assertTrue(first["passed"], first)
            self.assertTrue(second["passed"], second)
            report = inspect([read_json(manifest_path)], pptx)
            self.assertTrue(report["passed"], report)
            obj = report["arrows"][0]["pptx_object"]
            self.assertEqual(obj["kind"], "sp")
            self.assertEqual(obj["preset"], "rightArrow")
            self.assertEqual(obj["text"], "下一阶段")

    def test_final_postprocess_preserves_speaker_notes_parts(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            run = Path(name)
            page = run / "pages" / "page_001"
            manifest = filled_arrow_manifest(page)
            note = "保留的演讲者备注"
            notes = run / "notes_manifest.json"
            write_json(
                notes,
                {"notes": [{"page_index": 1, "text": note, "text_sha256": sha256_text(note)}]},
            )
            deck = run / "deck_manifest.json"
            out = run / "final" / "deck_edited.pptx"
            write_json(
                deck,
                {
                    "schema_version": 1,
                    "job_dir": str(run),
                    "page_count": 1,
                    "slide": {"width": 13.333, "height": 7.5},
                    "pages": [{"page_id": "page_001", "manifest": str(manifest)}],
                    "notes_manifest": str(notes),
                    "output": str(out),
                },
            )
            build_deck(deck, out)
            with zipfile.ZipFile(out) as archive:
                before = {name: archive.read(name) for name in archive.namelist() if name.startswith("ppt/notes")}
            report = postprocess_pptx(out, [manifest], run / "final" / "postprocess.json")
            self.assertTrue(report["passed"], report)
            self.assertTrue(report["preservation"]["notes_parts_preserved"])
            with zipfile.ZipFile(out) as archive:
                after = {name: archive.read(name) for name in archive.namelist() if name.startswith("ppt/notes")}
            self.assertEqual(before, after)
            self.assertTrue(inspect([read_json(manifest)], out)["passed"])

    def test_page_profile_qa_merges_into_standard_validation(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            page = Path(name)
            filled_arrow_manifest(page)
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
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "run_image2ppt_qa.py"),
                    str(page),
                    "--visual-review-status",
                    "reviewed",
                    "--visual-review-evidence",
                    str(evidence),
                    "--visual-review-notes",
                    "fixture: rendered arrow direction, embedded text, silhouette, and page bounds checked",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            validation = json.loads((page / "validation.json").read_text(encoding="utf-8"))
            report = json.loads((page / "image2ppt_qa.json").read_text(encoding="utf-8"))
            self.assertTrue(validation["passed"])
            self.assertTrue(validation["image2ppt_profile"]["passed"])
            self.assertEqual(report["state_owner"], "page_jobs.json")
            self.assertTrue((page / "render" / "rendered.png").is_file())
            self.assertFalse((page / "render" / "slide_01.png").exists())

    def test_final_profile_qa_revalidates_benchmark_deck(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            run = Path(name)
            page = run / "pages" / "page_001"
            manifest = filled_arrow_manifest(page)
            write_json(page / "validation.json", {"passed": True})
            out = run / "final" / "deck_edited.pptx"
            deck = run / "deck_manifest.json"
            write_json(
                deck,
                {
                    "schema_version": 1,
                    "job_dir": str(run),
                    "page_count": 1,
                    "slide": {"width": 13.333, "height": 7.5},
                    "pages": [
                        {
                            "page_id": "page_001",
                            "manifest": str(manifest),
                            "validation": str(page / "validation.json"),
                            "source_image": str(page / "source.png"),
                        }
                    ],
                    "output": str(out),
                },
            )
            build_deck(deck, out)
            pending = subprocess.run(
                [sys.executable, str(SCRIPTS / "run_final_image2ppt_qa.py"), str(run)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(pending.returncode, 2, pending.stdout + pending.stderr)
            evidence = run / "final" / "visual-review-evidence.json"
            complete_visual_review_evidence(
                run / "final" / "visual-review-evidence.template.json", evidence
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "run_final_image2ppt_qa.py"),
                    str(run),
                    "--visual-review-status",
                    "reviewed",
                    "--visual-review-evidence",
                    str(evidence),
                    "--visual-review-notes",
                    "fixture: all rendered slides checked for arrow object, text, direction, and page bounds",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads((run / "final" / "image2ppt_qa.json").read_text(encoding="utf-8"))
            self.assertTrue(report["passed"], report)
            self.assertEqual(report["state_owner"], "page_jobs.json")
            self.assertTrue(report["checks"]["image2ppt_validation"]["passed"])
            self.assertEqual(len(report["checks"]["page_diff_metrics"]), 1)
            self.assertFalse((run / "final" / "image2ppt_render" / "rendered.png").exists())


if __name__ == "__main__":
    unittest.main()
