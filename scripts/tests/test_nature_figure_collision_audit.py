from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "skills/nature-figure/scripts/audit_figure_collisions.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


AUDIT = load_module("nature_figure_collision_audit_test", SCRIPT)
PYMUPDF_AVAILABLE = any(
    importlib.util.find_spec(module_name) is not None
    for module_name in ("pymupdf", "fitz")
)


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


class CollisionGeometryTests(unittest.TestCase):
    def test_clean_text_and_distant_line_pass(self) -> None:
        page = AUDIT.PageGeometry(
            page=1,
            bbox=(0, 0, 200, 120),
            texts=[AUDIT.TextBox(0, "Clear", (50, 20, 90, 32))],
            traces=[AUDIT.TraceBox(0, "Clear", (50, 20, 90, 32))],
            strokes=[
                AUDIT.StrokePath(
                    0,
                    (20, 70, 180, 70),
                    1.0,
                    (((20, 70), (180, 70)),),
                )
            ],
        )

        result = AUDIT.audit_geometries([page])

        self.assertEqual(result["verdict"], "PASS")
        self.assertEqual(result["summary"]["fail"], 0)

    def test_text_stroke_and_text_text_collisions_block_delivery(self) -> None:
        page = AUDIT.PageGeometry(
            page=1,
            bbox=(0, 0, 200, 120),
            texts=[
                AUDIT.TextBox(0, "First", (50, 40, 100, 54)),
                AUDIT.TextBox(1, "Second", (80, 43, 125, 57)),
            ],
            traces=[
                AUDIT.TraceBox(0, "First", (50, 40, 100, 54)),
                AUDIT.TraceBox(1, "Second", (80, 43, 125, 57)),
            ],
            strokes=[
                AUDIT.StrokePath(
                    0,
                    (20, 47, 180, 47),
                    1.0,
                    (((20, 47), (180, 47)),),
                )
            ],
        )

        result = AUDIT.audit_geometries([page])
        kinds = {finding["kind"] for finding in result["findings"]}

        self.assertEqual(result["verdict"], "FIX BEFORE DELIVERY")
        self.assertIn("text-text", kinds)
        self.assertIn("text-stroke", kinds)
        self.assertEqual(AUDIT.exit_code(result), 1)

    def test_contained_fill_is_informational_but_partial_fill_warns(self) -> None:
        page = AUDIT.PageGeometry(
            page=1,
            bbox=(0, 0, 200, 120),
            texts=[
                AUDIT.TextBox(0, "Inside", (60, 40, 90, 52)),
                AUDIT.TextBox(1, "Edge", (120, 40, 155, 52)),
            ],
            traces=[
                AUDIT.TraceBox(0, "Inside", (60, 40, 90, 52)),
                AUDIT.TraceBox(1, "Edge", (120, 40, 155, 52)),
            ],
            fills=[
                AUDIT.FilledRegion(0, (50, 30, 100, 60), "fill"),
                AUDIT.FilledRegion(1, (105, 30, 135, 60), "fill"),
            ],
        )

        result = AUDIT.audit_geometries([page])

        self.assertEqual(result["verdict"], "REVIEW REQUIRED")
        self.assertEqual(result["summary"]["contained_fill_overlays"], 1)
        self.assertEqual(result["summary"]["warn"], 1)
        self.assertEqual(result["findings"][0]["kind"], "text-fill-edge")
        self.assertEqual(AUDIT.exit_code(result), 0)
        self.assertEqual(AUDIT.exit_code(result, strict=True), 1)

    def test_page_clipping_blocks_delivery(self) -> None:
        page = AUDIT.PageGeometry(
            page=1,
            bbox=(0, 0, 200, 120),
            traces=[AUDIT.TraceBox(0, "Clipped", (50, -8, 90, 4))],
        )

        result = AUDIT.audit_geometries([page])

        self.assertEqual(result["summary"]["fail"], 1)
        self.assertEqual(result["findings"][0]["kind"], "text-page-clipping")

    def test_pdf_without_editable_text_is_not_claimed_as_checked(self) -> None:
        result = AUDIT.audit_geometries(
            [AUDIT.PageGeometry(page=1, bbox=(0, 0, 200, 120))]
        )

        self.assertFalse(result["auditable"])
        self.assertEqual(result["verdict"], "NOT AUDITABLE")
        self.assertEqual(AUDIT.exit_code(result), 2)


@unittest.skipUnless(PYMUPDF_AVAILABLE, "PyMuPDF is not installed in this test runtime")
class CollisionPdfEndToEndTests(unittest.TestCase):
    def test_real_pdf_detects_crossed_text_and_writes_overlay(self) -> None:
        try:
            import pymupdf as fitz
        except ImportError:
            import fitz

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "collision.pdf"
            overlay = root / "collision-overlay.pdf"
            report = root / "collision.json"

            document = fitz.open()
            page = document.new_page(width=200, height=120)
            page.insert_text((50, 60), "Crossed", fontsize=12)
            page.insert_text((50, 95), "Clear", fontsize=12)
            page.draw_line((20, 55), (180, 55), width=1)
            document.save(source)
            document.close()

            result = AUDIT.audit_pdf(source)
            report.write_text(json.dumps(result), encoding="utf-8")
            AUDIT.write_overlay_pdf(source, overlay, result["findings"])
            first_overlay_size = overlay.stat().st_size
            AUDIT.write_overlay_pdf(source, overlay, result["findings"])

            crossed = [
                finding
                for finding in result["findings"]
                if finding["kind"] == "text-stroke"
            ]
            self.assertEqual([finding["text"] for finding in crossed], ["Crossed"])
            self.assertTrue(overlay.is_file())
            self.assertGreater(overlay.stat().st_size, source.stat().st_size)
            self.assertEqual(overlay.stat().st_size, first_overlay_size)
            self.assertTrue(json.loads(report.read_text(encoding="utf-8"))["findings"])


class CollisionWorkflowIntegrationTests(unittest.TestCase):
    def test_every_python_or_r_figure_routes_through_collision_audit(self) -> None:
        skill = read("skills/nature-figure/SKILL.md")
        python_backend = read("skills/nature-figure/static/fragments/backend/python.md")
        r_backend = read("skills/nature-figure/static/fragments/backend/r.md")
        qa = read("skills/nature-figure/references/qa-contract.md")

        for relative, text in (
            ("SKILL.md", skill),
            ("python.md", python_backend),
            ("r.md", r_backend),
            ("qa-contract.md", qa),
        ):
            self.assertIn("audit_figure_collisions.py", text, relative)

        self.assertIn("After every generated or revised Python/R scientific figure", skill)
        self.assertIn("FIX BEFORE DELIVERY", qa)
        self.assertIn("REVIEW REQUIRED", qa)

    def test_dependency_docs_eval_and_release_version_are_connected(self) -> None:
        manifest = read("skills/nature-figure/manifest.yaml")
        requirements = read("skills/nature-figure/requirements.txt")
        readme_zh = read("skills/nature-figure/README.md")
        readme_en = read("skills/nature-figure/README_EN.md")
        evals = json.loads(read("skills/nature-figure/evals/evals.json"))
        installer = read("scripts/update-codex-skills.sh")

        self.assertIn("version: 2.8.0", manifest)
        self.assertIn("PyMuPDF", requirements)
        for text in (readme_zh, readme_en):
            self.assertIn("audit_figure_collisions.py", text)
        self.assertIn("nature-figure/requirements.txt", installer)
        ids = {case["id"] for case in evals["evals"]}
        self.assertIn("rendered-collision-audit-is-mandatory", ids)


if __name__ == "__main__":
    unittest.main()
