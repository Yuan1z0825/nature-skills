from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from support import SCRIPTS, filled_arrow_manifest, image2ppt_command, image2ppt_runtime_script


class PathConfinementTests(unittest.TestCase):
    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [*image2ppt_command(), *args],
            text=True,
            capture_output=True,
            check=False,
        )

    def test_page_build_rejects_parent_output_escape(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            page = root / "page"
            filled_arrow_manifest(page)
            result = self.run_cli(
                "page",
                "build",
                str(page),
                "--out",
                "../escaped.pptx",
                "--preview",
                "../escaped.png",
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("must stay inside page_dir", result.stderr)
            self.assertFalse((root / "escaped.pptx").exists())
            self.assertFalse((root / "escaped.png").exists())

    def test_page_helpers_reject_parent_output_escape(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            page = root / "page"
            filled_arrow_manifest(page)
            hints = self.run_cli("page", "hints", str(page), "--out", "../hints.json")
            self.assertNotEqual(hints.returncode, 0)
            self.assertIn("must stay inside page_dir", hints.stderr)
            self.assertFalse((root / "hints.json").exists())

            Image.new("RGB", (1280, 720), "white").save(page / "preview.png")
            contact = self.run_cli("page", "contact-sheet", str(page), "--out", "../contact.png")
            self.assertNotEqual(contact.returncode, 0)
            self.assertIn("must stay inside page_dir", contact.stderr)
            self.assertFalse((root / "contact.png").exists())

    def test_formula_output_rejects_parent_escape_before_engine_lookup(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            page = root / "page"
            page.mkdir()
            result = self.run_cli(
                "formula",
                "render-latex",
                str(page),
                "--tex",
                "x",
                "--out",
                "../formula.svg",
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("must stay inside page_dir", result.stderr)
            self.assertFalse((root / "formula.svg").exists())

    def test_manifest_image_cannot_read_outside_page_directory(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            page = root / "page"
            manifest_path = filled_arrow_manifest(page)
            outside = root / "outside.png"
            Image.new("RGB", (32, 32), "red").save(outside)
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["images"] = [
                {"id": "outside", "path": "../outside.png", "box_px": [0, 0, 32, 32]}
            ]
            manifest["asset_provenance"] = [
                {
                    "path": "../outside.png",
                    "source": "../outside.png",
                    "source_type": "user-provided",
                    "provenance_note": "path confinement fixture",
                }
            ]
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            result = self.run_cli("page", "build", str(page))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("outside allowed directory", result.stderr)
            self.assertFalse((page / "page.pptx").exists())

    def test_finalize_rejects_output_outside_run(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            run = root / "run"
            run.mkdir()
            (run / "deck_manifest.json").write_text(
                json.dumps({"output": "../escaped.pptx", "pages": []}),
                encoding="utf-8",
            )
            (run / "page_jobs.json").write_text(
                json.dumps({"pages": [], "run_status": "pages_recorded"}),
                encoding="utf-8",
            )
            result = self.run_cli("run", "finalize", str(run))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("must stay inside run directory", result.stderr)
            self.assertFalse((root / "escaped.pptx").exists())

    def test_direct_builder_and_validator_reject_parent_escape(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            page = root / "page"
            manifest = filled_arrow_manifest(page)
            build = subprocess.run(
                [
                    sys.executable,
                    str(image2ppt_runtime_script("build_pptx_from_manifest.py")),
                    str(manifest),
                    "--out",
                    "../escaped.pptx",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(build.returncode, 0)
            self.assertFalse((root / "escaped.pptx").exists())

            (page / "page.pptx").write_bytes(b"invalid but path-local fixture")
            validate = subprocess.run(
                [
                    sys.executable,
                    str(image2ppt_runtime_script("validate_pptx.py")),
                    str(page / "page.pptx"),
                    "--manifest",
                    str(manifest),
                    "--report",
                    "../escaped-validation.json",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(validate.returncode, 0)
            self.assertFalse((root / "escaped-validation.json").exists())

    def test_supplemental_reports_reject_parent_escape(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            page = root / "page"
            manifest = filled_arrow_manifest(page)
            region = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "inspect_region_decomposition.py"),
                    "--manifest",
                    str(manifest),
                    "--out",
                    "../escaped-region.json",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(region.returncode, 0)
            self.assertFalse((root / "escaped-region.json").exists())

            postprocess = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "postprocess_manifest_arrows.py"),
                    str(page / "page.pptx"),
                    "--manifest",
                    str(manifest),
                    "--report",
                    "../escaped-arrow.json",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(postprocess.returncode, 0)
            self.assertFalse((root / "escaped-arrow.json").exists())


if __name__ == "__main__":
    unittest.main()
