from __future__ import annotations

import importlib.util
import sys
import unittest
import zlib
from pathlib import Path


SKILL = Path(__file__).parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


VALIDATOR = load_module("nature_figure_validator_test", SKILL / "scripts" / "validate_figure.py")
PDF_AUDIT = load_module("nature_figure_pdf_audit_test", SKILL / "scripts" / "audit_pdf_text.py")
FIGURE_SAFETY = load_module("nature_figure_safety_test", SKILL / "scripts" / "figure_safety.py")


def fake_pdf(stream: bytes, compressed: bool = False) -> bytes:
    payload = zlib.compress(stream) if compressed else stream
    filter_entry = b" /Filter /FlateDecode" if compressed else b""
    return (
        b"%PDF-1.4\n1 0 obj\n<< /Length "
        + str(len(payload)).encode("ascii")
        + filter_entry
        + b" >>\nstream\n"
        + payload
        + b"\nendstream\nendobj\n%%EOF\n"
    )


class PdfTextAuditTests(unittest.TestCase):
    def test_plain_pdf_passes_when_all_tf_sizes_meet_floor(self):
        result = PDF_AUDIT.audit_pdf(fake_pdf(b"BT /F1 7 Tf (Label) Tj ET"))
        self.assertTrue(result["auditable"])
        self.assertEqual(result["minimum_found_pt"], 7.0)
        self.assertEqual(result["below_minimum_count"], 0)

    def test_flate_pdf_catches_mathtext_sized_run(self):
        result = PDF_AUDIT.audit_pdf(
            fake_pdf(b"BT /F1 7 Tf (R) Tj /F2 4.9 Tf (2) Tj ET", compressed=True)
        )
        self.assertTrue(result["auditable"])
        self.assertEqual(result["minimum_found_pt"], 4.9)
        self.assertEqual(result["below_minimum_count"], 1)
        self.assertEqual(result["below_minimum"][0]["font"], "F2")

    def test_pdf_without_supported_tf_is_not_auditable(self):
        result = PDF_AUDIT.audit_pdf(fake_pdf(b"0 0 m 10 10 l S"))
        self.assertFalse(result["auditable"])


class SourceSafetyTests(unittest.TestCase):
    def findings(self, source: str):
        return {row.check_id: row for row in VALIDATOR.validate_source(source, "python")}

    def test_risky_patterns_are_reported(self):
        source = '''
import numpy as np
seed_scores = np.median(scores, axis=0)
n_equiv = np.interp(target, decreasing_error, n_samples)
ax.plot(x, seed_scores, label="+ semantic guidance")
ax.text(0.5, 0.5, "$R^2$", fontsize=7, rotation=45,
        bbox=dict(facecolor="white", edgecolor="none"))
LABEL_Y = 96.4
'''
        rows = self.findings(source)
        for check_id in (
            "FONT-GLYPH-FLOOR",
            "LEGEND-LABEL-CASE",
            "INTERP-MONOTONIC",
            "UNCERTAINTY-ENCODING",
            "ROTATION-ANCHOR",
            "ANNOTATION-WORKAROUND",
        ):
            self.assertEqual(rows[check_id].level, "WARN", check_id)

    def test_guarded_patterns_pass_targeted_checks(self):
        source = '''
import numpy as np
def interp_monotone(target, xp, fp):
    order = np.argsort(xp)
    xp = xp[order]
    fp = fp[order]
    assert np.all(np.diff(xp) > 0)
    return np.interp(target, xp, fp)

seed_scores = np.median(scores, axis=0)
ax.plot(x, seed_scores, label="+ Semantic guidance")
ax.fill_between(x, seed_scores - seed_std, seed_scores + seed_std)
ax.text(0.5, 0.5, "R²", fontsize=7, rotation=45, rotation_mode="anchor")
'''
        rows = self.findings(source)
        for check_id in (
            "FONT-GLYPH-FLOOR",
            "LEGEND-LABEL-CASE",
            "INTERP-MONOTONIC",
            "UNCERTAINTY-ENCODING",
            "ROTATION-ANCHOR",
            "ANNOTATION-WORKAROUND",
        ):
            self.assertEqual(rows[check_id].level, "PASS", check_id)

    def test_string_split_is_not_mistaken_for_random_split(self):
        source = '''
columns = [value.strip() for value in args.columns.split(",")]
ax.set_ylabel("Mean fold change")
'''
        rows = self.findings(source)
        self.assertEqual(rows["UNCERTAINTY-ENCODING"].level, "PASS")

    def test_every_rotated_call_must_be_anchored(self):
        source = '''
ax.text(0.2, 0.3, "A", rotation=45, rotation_mode="anchor")
ax.text(0.5, 0.6, "B", rotation=90)
'''
        rows = self.findings(source)
        self.assertEqual(rows["ROTATION-ANCHOR"].level, "WARN")
        self.assertEqual(rows["ROTATION-ANCHOR"].evidence, ["line 3: rotation=..."])

    def test_python_multipanel_source_requires_alignment_gate(self):
        missing = self.findings("fig, axes = plt.subplots(2, 2)")
        self.assertEqual(missing["PANEL-ALIGNMENT-GATE"].level, "FAIL")

        import_only = self.findings(
            "from audit_panel_alignment import require_matplotlib_panel_alignment\n"
            "fig, axes = plt.subplots(2, 2)"
        )
        self.assertEqual(import_only["PANEL-ALIGNMENT-GATE"].level, "FAIL")

        manual_axes = self.findings(
            "fig = plt.figure()\n"
            "ax_a = fig.add_axes([0.1, 0.1, 0.3, 0.8])\n"
            "ax_b = fig.add_axes([0.6, 0.1, 0.3, 0.8])"
        )
        self.assertEqual(manual_axes["PANEL-ALIGNMENT-GATE"].level, "FAIL")

        mosaic = self.findings("fig, axes = plt.subplot_mosaic([['a', 'b']])")
        self.assertEqual(mosaic["PANEL-ALIGNMENT-GATE"].level, "FAIL")

        wired = self.findings(
            '''
fig, axes = plt.subplots(2, 2)
require_matplotlib_panel_alignment(fig, strict=True)
'''
        )
        self.assertEqual(wired["PANEL-ALIGNMENT-GATE"].level, "PASS")

    def test_r_patchwork_source_requires_alignment_gate(self):
        missing = {
            row.check_id: row
            for row in VALIDATOR.validate_source(
                "fig <- (p_a | p_b) + plot_layout(guides = 'collect')",
                "r",
            )
        }
        self.assertEqual(missing["PANEL-ALIGNMENT-GATE"].level, "FAIL")

        manifest_only = {
            row.check_id: row
            for row in VALIDATOR.validate_source(
                "fig <- p_a | p_b\nwrite_patchwork_panel_layout(fig, manifest_path='a.json')",
                "r",
            )
        }
        self.assertEqual(manifest_only["PANEL-ALIGNMENT-GATE"].level, "FAIL")

        wired = {
            row.check_id: row
            for row in VALIDATOR.validate_source(
                "fig <- p_a | p_b\nrequire_patchwork_panel_alignment(fig, manifest_path='a.json')",
                "r",
            )
        }
        self.assertEqual(wired["PANEL-ALIGNMENT-GATE"].level, "PASS")

    def test_r_delimiter_check_ignores_comments(self):
        finding = VALIDATOR.check_syntax(
            "# patchwork's final panel cells { are measured\nfig <- (p_a | p_b)",
            "r",
        )
        self.assertEqual(finding.level, "WARN")
        self.assertIn("delimiter check passed", finding.message)


class NumericalSafetyTests(unittest.TestCase):
    def test_interp_monotone_handles_decreasing_grid(self):
        result = FIGURE_SAFETY.interp_monotone(7, [10, 8, 6], [5, 10, 15])
        self.assertAlmostEqual(float(result), 12.5)

    def test_interp_monotone_rejects_direction_changes(self):
        with self.assertRaisesRegex(ValueError, "strictly monotone"):
            FIGURE_SAFETY.interp_monotone(7, [10, 6, 8], [5, 10, 15])

    def test_label_position_clears_uncertainty(self):
        label_y = FIGURE_SAFETY.label_y_above([80, 90], spread=[2, 6])
        self.assertGreater(label_y, 96)


if __name__ == "__main__":
    unittest.main()
