import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNTIME_DIR = ROOT / "cli/image2ppt/runtime"
sys.path.insert(0, str(RUNTIME_DIR))

from formula_renderer import FormulaRenderError, build_latex_document, formula_image_fragment, select_latex_engine  # noqa: E402


class FormulaRendererTest(unittest.TestCase):
    def test_build_latex_document_wraps_formula(self):
        document = build_latex_document(r"\frac{a}{b}")

        self.assertIn(r"\documentclass[border=2pt]{standalone}", document)
        self.assertIn(r"\usepackage{amsmath,amssymb,mathtools,bm}", document)
        self.assertIn("\\[\n\\frac{a}{b}\n\\]", document)

    def test_fragment_records_latex_rendered_formula_image(self):
        fragment = formula_image_fragment(
            formula_id="objective_formula",
            image_path="/tmp/page/assets/f1.svg",
            tex_source="/tmp/page/assets/f1.tex",
            page_dir="/tmp/page",
            box_px="100,120,300,80",
        )

        self.assertEqual("latex-formula-image-fragment", fragment["type"])
        self.assertEqual("assets/f1.svg", fragment["images"][0]["path"])
        self.assertEqual([100.0, 120.0, 300.0, 80.0], fragment["images"][0]["box_px"])
        self.assertEqual("latex-rendered-formula", fragment["asset_provenance"][0]["source_type"])
        self.assertFalse(fragment["formula_inventory"][0]["editable"])

    def test_missing_explicit_engine_is_clear(self):
        with self.assertRaises(FormulaRenderError) as ctx:
            select_latex_engine("definitely-missing-latex-engine")

        self.assertIn("LaTeX engine not found", str(ctx.exception))

    def test_cli_help_exposes_render_latex_only(self):
        result = subprocess.run(
            [sys.executable, str(RUNTIME_DIR / "main.py"), "formula", "--help"],
            text=True,
            capture_output=True,
        )

        self.assertEqual(0, result.returncode)
        self.assertIn("render-latex", result.stdout)
        self.assertNotIn("compile", result.stdout)

    def test_cli_render_latex_missing_engine_fails_before_writing(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "f1.svg"
            result = subprocess.run(
                [
                    sys.executable,
                    str(RUNTIME_DIR / "main.py"),
                    "formula",
                    "render-latex",
                    "--tex",
                    r"\frac{a}{b}",
                    "--out",
                    str(out),
                    "--engine",
                    "definitely-missing-latex-engine",
                ],
                text=True,
                capture_output=True,
            )

            self.assertEqual(1, result.returncode)
            self.assertIn("LaTeX engine not found", result.stderr)
            self.assertFalse(out.exists())


if __name__ == "__main__":
    unittest.main()
