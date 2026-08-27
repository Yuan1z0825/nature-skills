from __future__ import annotations

import importlib.util
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "skills/nature-figure/scripts/audit_panel_alignment.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


AUDIT = load_module("nature_figure_panel_alignment_test", SCRIPT)
MATPLOTLIB_AVAILABLE = importlib.util.find_spec("matplotlib") is not None


def panel(
    panel_id: str,
    bbox: list[float],
    row: tuple[int, int],
    column: tuple[int, int],
) -> dict[str, object]:
    return {
        "id": panel_id,
        "bbox_pt": bbox,
        "grid_id": "grid",
        "row_start": row[0],
        "row_stop": row[1],
        "col_start": column[0],
        "col_stop": column[1],
    }


def aligned_manifest() -> dict[str, object]:
    return {
        "schema_version": 1,
        "backend": "test",
        "figure": {"width_pt": 300, "height_pt": 200},
        "panels": [
            panel("a", [20, 110, 130, 180], (0, 1), (0, 1)),
            panel("b", [170, 110, 280, 180], (0, 1), (1, 2)),
            panel("c", [20, 20, 130, 90], (1, 2), (0, 1)),
            panel("d", [170, 20, 280, 90], (1, 2), (1, 2)),
        ],
    }


def asymmetric_vertical_manifest(spanning_side: str) -> dict[str, object]:
    if spanning_side == "right":
        panels = [
            panel("a", [20, 110, 130, 180], (0, 1), (0, 1)),
            panel("b", [20, 20, 130, 90], (1, 2), (0, 1)),
            panel("c", [170, 20, 280, 180], (0, 2), (1, 2)),
        ]
    elif spanning_side == "left":
        panels = [
            panel("a", [20, 20, 130, 180], (0, 2), (0, 1)),
            panel("b", [170, 110, 280, 180], (0, 1), (1, 2)),
            panel("c", [170, 20, 280, 90], (1, 2), (1, 2)),
        ]
    else:
        raise ValueError("spanning_side must be left or right")
    return {
        "schema_version": 1,
        "backend": "test",
        "figure": {"width_pt": 300, "height_pt": 200},
        "panels": panels,
    }


def horizontal_manifest(
    widths: list[float],
    *,
    column_spans: list[int] | None = None,
    exemptions: list[dict[str, object]] | None = None,
) -> dict[str, object]:
    spans = [1] * len(widths) if column_spans is None else column_spans
    panels = []
    left = 10.0
    column_start = 0
    for index, (width, span) in enumerate(zip(widths, spans)):
        panels.append(
            panel(
                chr(ord("a") + index),
                [left, 20, left + width, 80],
                (0, 1),
                (column_start, column_start + span),
            )
        )
        left += width + 20
        column_start += span
    return {
        "schema_version": 1,
        "backend": "test",
        "figure": {"width_pt": left + 10, "height_pt": 100},
        "panels": panels,
        "exemptions": [] if exemptions is None else exemptions,
    }


class PanelAlignmentCoreTests(unittest.TestCase):
    def test_single_panel_is_not_applicable_and_nonblocking(self) -> None:
        manifest = {
            "schema_version": 1,
            "backend": "test",
            "figure": {"width_pt": 200, "height_pt": 120},
            "panels": [{"id": "a", "bbox_pt": [20, 20, 180, 100]}],
        }
        report = AUDIT.audit_layout_manifest(manifest)
        self.assertEqual(report["verdict"], "NOT APPLICABLE")
        self.assertEqual(AUDIT.exit_code(report), 0)

    def test_aligned_two_by_two_grid_passes(self) -> None:
        report = AUDIT.audit_layout_manifest(aligned_manifest())

        self.assertTrue(report["auditable"])
        self.assertEqual(report["verdict"], "PASS")
        self.assertEqual(report["summary"]["comparisons"], 4)
        self.assertEqual(AUDIT.exit_code(report), 0)

    def test_shifted_panel_blocks_row_and_column_alignment(self) -> None:
        manifest = aligned_manifest()
        manifest["panels"][1]["bbox_pt"] = [175, 104, 285, 174]

        report = AUDIT.audit_layout_manifest(manifest)
        kinds = {finding["kind"] for finding in report["findings"]}

        self.assertEqual(report["verdict"], "FIX BEFORE DELIVERY")
        self.assertIn("row-axes-misalignment", kinds)
        self.assertIn("column-axes-misalignment", kinds)
        self.assertEqual(AUDIT.exit_code(report), 1)

    def test_left_two_right_one_and_left_one_right_two_pass(self) -> None:
        for spanning_side in ("right", "left"):
            with self.subTest(spanning_side=spanning_side):
                report = AUDIT.audit_layout_manifest(
                    asymmetric_vertical_manifest(spanning_side)
                )
                self.assertEqual(report["verdict"], "PASS")
                self.assertEqual(report["summary"]["comparisons"], 3)
                self.assertEqual(
                    {group["edge"] for group in report["layout"]["boundary_groups"]},
                    {"top", "bottom"},
                )

    def test_shifted_spanning_panel_blocks_shared_outer_edges(self) -> None:
        for spanning_side, panel_index in (("right", 2), ("left", 0)):
            with self.subTest(spanning_side=spanning_side):
                manifest = asymmetric_vertical_manifest(spanning_side)
                box = manifest["panels"][panel_index]["bbox_pt"]
                manifest["panels"][panel_index]["bbox_pt"] = [
                    box[0],
                    box[1] + 5,
                    box[2],
                    box[3] - 5,
                ]
                report = AUDIT.audit_layout_manifest(manifest)
                kinds = {finding["kind"] for finding in report["findings"]}
                self.assertEqual(report["verdict"], "FIX BEFORE DELIVERY")
                self.assertIn("shared-top-edge-misalignment", kinds)
                self.assertIn("shared-bottom-edge-misalignment", kinds)
                self.assertEqual(AUDIT.exit_code(report), 1)

    def test_spanning_layout_panel_labels_follow_the_shared_top_edge(self) -> None:
        manifest = asymmetric_vertical_manifest("right")
        anchors = ([15, 185], [15, 95], [165, 180])
        for panel_row, anchor in zip(manifest["panels"], anchors):
            panel_row["panel_label_anchor_pt"] = anchor

        report = AUDIT.audit_layout_manifest(manifest, require_panel_labels=True)
        kinds = {finding["kind"] for finding in report["findings"]}

        self.assertEqual(report["verdict"], "FIX BEFORE DELIVERY")
        self.assertIn("shared-top-panel-label-misalignment", kinds)

    def test_three_and_four_horizontal_equal_width_panels_pass(self) -> None:
        for widths in ([60, 60, 60], [45, 45, 45, 45]):
            with self.subTest(panel_count=len(widths)):
                report = AUDIT.audit_layout_manifest(horizontal_manifest(list(widths)))
                self.assertEqual(report["verdict"], "PASS")
                self.assertEqual(AUDIT.exit_code(report), 0)

    def test_three_and_four_horizontal_unequal_width_panels_block(self) -> None:
        for widths in ([60, 80, 100], [45, 60, 75, 90]):
            with self.subTest(panel_count=len(widths)):
                report = AUDIT.audit_layout_manifest(horizontal_manifest(list(widths)))
                kinds = {finding["kind"] for finding in report["findings"]}
                self.assertEqual(report["verdict"], "FIX BEFORE DELIVERY")
                self.assertIn("horizontal-panel-width-misalignment", kinds)
                self.assertEqual(AUDIT.exit_code(report), 1)

    def test_horizontal_width_check_compares_only_equal_grid_spans(self) -> None:
        report = AUDIT.audit_layout_manifest(
            horizontal_manifest([120, 60, 60], column_spans=[2, 1, 1])
        )
        self.assertEqual(report["verdict"], "PASS")

    def test_intentional_horizontal_width_exception_requires_panel_width_reason(self) -> None:
        manifest = horizontal_manifest(
            [60, 80, 60],
            exemptions=[
                {
                    "panels": ["b"],
                    "checks": ["panel-width"],
                    "reason": "middle hero panel intentionally receives extra width",
                }
            ],
        )
        report = AUDIT.audit_layout_manifest(manifest)
        self.assertEqual(report["verdict"], "PASS")
        self.assertEqual(report["summary"]["exemptions"], 1)

    def test_unequal_gutters_block_delivery(self) -> None:
        manifest = {
            "schema_version": 1,
            "backend": "test",
            "figure": {"width_pt": 220, "height_pt": 100},
            "panels": [
                panel("a", [10, 20, 50, 80], (0, 1), (0, 1)),
                panel("b", [70, 20, 110, 80], (0, 1), (1, 2)),
                panel("c", [150, 20, 190, 80], (0, 1), (2, 3)),
            ],
        }

        report = AUDIT.audit_layout_manifest(manifest)

        self.assertEqual(report["verdict"], "FIX BEFORE DELIVERY")
        self.assertIn(
            "horizontal-gutter-misalignment",
            {finding["kind"] for finding in report["findings"]},
        )

    def test_asymmetric_hero_panel_uses_only_valid_shared_edges(self) -> None:
        manifest = {
            "schema_version": 1,
            "backend": "test",
            "figure": {"width_pt": 300, "height_pt": 200},
            "panels": [
                panel("a", [20, 105, 280, 185], (0, 1), (0, 2)),
                panel("b", [20, 20, 130, 85], (1, 2), (0, 1)),
                panel("c", [170, 20, 280, 85], (1, 2), (1, 2)),
            ],
        }

        report = AUDIT.audit_layout_manifest(manifest)

        self.assertEqual(report["verdict"], "PASS")
        self.assertEqual(report["summary"]["comparisons"], 3)

    def test_exemption_requires_reason_and_can_remove_an_inset(self) -> None:
        manifest = {
            "schema_version": 1,
            "backend": "test",
            "figure": {"width_pt": 240, "height_pt": 120},
            "panels": [
                panel("a", [10, 20, 60, 90], (0, 1), (0, 1)),
                panel("b", [85, 28, 135, 98], (0, 1), (1, 2)),
                panel("c", [160, 20, 210, 90], (0, 1), (2, 3)),
            ],
            "exemptions": [
                {
                    "panels": ["b"],
                    "checks": ["row", "horizontal-gutter"],
                    "reason": "intentional inset panel",
                }
            ],
        }

        report = AUDIT.audit_layout_manifest(manifest)
        self.assertEqual(report["verdict"], "PASS")
        self.assertEqual(report["summary"]["exemptions"], 1)

        manifest["exemptions"][0]["reason"] = ""
        invalid = AUDIT.audit_layout_manifest(manifest)
        self.assertEqual(invalid["verdict"], "NOT AUDITABLE")
        self.assertEqual(AUDIT.exit_code(invalid), 2)

    def test_diagnostic_svg_and_json_are_written(self) -> None:
        report = AUDIT.audit_layout_manifest(aligned_manifest())
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            json_path = root / "alignment.json"
            svg_path = root / "alignment.svg"
            AUDIT.write_json_report(report, json_path)
            AUDIT.write_overlay_svg(report, svg_path)

            self.assertEqual(json.loads(json_path.read_text())["verdict"], "PASS")
            self.assertIn("<svg", svg_path.read_text())


@unittest.skipUnless(MATPLOTLIB_AVAILABLE, "matplotlib is not installed")
class MatplotlibPanelAlignmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        os.environ.setdefault("MPLCONFIGDIR", tempfile.gettempdir())
        import matplotlib

        matplotlib.use("Agg")

    def test_final_matplotlib_axes_and_panel_labels_are_measured(self) -> None:
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(2, 2, figsize=(4, 3))
        for label, axis in zip("abcd", axes.flat):
            axis.text(-0.12, 1.02, label, transform=axis.transAxes, fontweight="bold")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            report = AUDIT.require_matplotlib_panel_alignment(
                fig,
                json_out=root / "alignment.json",
                overlay_svg=root / "alignment.svg",
                require_panel_labels=True,
                strict=True,
            )

            self.assertEqual(report["verdict"], "PASS")
            self.assertEqual(len(report["layout"]["panels"]), 4)
            self.assertTrue(all("panel_label_anchor_pt" in row for row in report["layout"]["panels"]))
        plt.close(fig)

    def test_single_subplot_with_twin_axis_is_not_a_multipanel_figure(self) -> None:
        import matplotlib.pyplot as plt

        fig, axis = plt.subplots(figsize=(3, 2))
        axis.twinx()
        report = AUDIT.require_matplotlib_panel_alignment(fig, strict=True)

        self.assertEqual(report["verdict"], "NOT APPLICABLE")
        self.assertEqual(len(report["layout"]["panels"]), 1)
        plt.close(fig)

    def test_manual_axes_pass_with_explicit_comparison_groups(self) -> None:
        import matplotlib.pyplot as plt

        fig = plt.figure(figsize=(4, 2))
        ax_a = fig.add_axes([0.1, 0.15, 0.35, 0.7])
        ax_b = fig.add_axes([0.55, 0.15, 0.35, 0.7])
        report = AUDIT.require_matplotlib_panel_alignment(
            fig,
            axes=[ax_a, ax_b],
            panel_ids=["a", "b"],
            row_groups=[["a", "b"]],
            strict=True,
        )

        self.assertEqual(report["verdict"], "PASS")
        plt.close(fig)

    def test_both_vertical_two_plus_one_gridspec_layouts_are_inferred(self) -> None:
        import matplotlib.pyplot as plt
        from matplotlib.transforms import ScaledTranslation

        for spanning_side in ("right", "left"):
            with self.subTest(spanning_side=spanning_side):
                fig = plt.figure(figsize=(4, 3))
                grid = fig.add_gridspec(2, 2)
                if spanning_side == "right":
                    axes = [
                        fig.add_subplot(grid[0, 0]),
                        fig.add_subplot(grid[1, 0]),
                        fig.add_subplot(grid[:, 1]),
                    ]
                else:
                    axes = [
                        fig.add_subplot(grid[:, 0]),
                        fig.add_subplot(grid[0, 1]),
                        fig.add_subplot(grid[1, 1]),
                    ]
                offset = ScaledTranslation(-4 / 72, 3 / 72, fig.dpi_scale_trans)
                for label, axis in zip("abc", axes):
                    axis.text(
                        0,
                        1,
                        label,
                        transform=axis.transAxes + offset,
                        fontweight="bold",
                        ha="left",
                        va="bottom",
                    )

                report = AUDIT.require_matplotlib_panel_alignment(
                    fig,
                    require_panel_labels=True,
                    strict=True,
                )
                self.assertEqual(report["verdict"], "PASS")
                self.assertEqual(report["summary"]["comparisons"], 3)
                plt.close(fig)

    def test_shifted_vertical_spanning_axes_raise_blocking_error(self) -> None:
        import matplotlib.pyplot as plt

        for spanning_side in ("right", "left"):
            with self.subTest(spanning_side=spanning_side):
                fig = plt.figure(figsize=(4, 3))
                grid = fig.add_gridspec(2, 2)
                if spanning_side == "right":
                    fig.add_subplot(grid[0, 0])
                    fig.add_subplot(grid[1, 0])
                    spanning = fig.add_subplot(grid[:, 1])
                else:
                    spanning = fig.add_subplot(grid[:, 0])
                    fig.add_subplot(grid[0, 1])
                    fig.add_subplot(grid[1, 1])
                position = spanning.get_position()
                spanning.set_position(
                    [position.x0, position.y0 + 0.02, position.width, position.height - 0.04]
                )

                with self.assertRaises(AUDIT.PanelAlignmentError):
                    AUDIT.require_matplotlib_panel_alignment(fig, strict=True)
                plt.close(fig)

    def test_three_and_four_horizontal_matplotlib_panels_are_equal_width(self) -> None:
        import matplotlib.pyplot as plt

        for panel_count in (3, 4):
            with self.subTest(panel_count=panel_count):
                fig, _axes = plt.subplots(1, panel_count, figsize=(panel_count * 2, 2))
                report = AUDIT.require_matplotlib_panel_alignment(fig, strict=True)
                self.assertEqual(report["verdict"], "PASS")
                plt.close(fig)

    def test_unequal_matplotlib_width_ratios_block_three_and_four_panel_rows(self) -> None:
        import matplotlib.pyplot as plt

        for ratios in ([1, 1.3, 1], [1, 1.2, 1.4, 1]):
            with self.subTest(panel_count=len(ratios)):
                fig, _axes = plt.subplots(
                    1,
                    len(ratios),
                    figsize=(len(ratios) * 2, 2),
                    gridspec_kw={"width_ratios": ratios},
                )
                manifest = AUDIT.matplotlib_layout_manifest(fig)
                report = AUDIT.audit_layout_manifest(manifest)
                kinds = {finding["kind"] for finding in report["findings"]}
                self.assertEqual(report["verdict"], "FIX BEFORE DELIVERY")
                self.assertIn("horizontal-panel-width-misalignment", kinds)
                plt.close(fig)

    def test_manual_axes_shift_raises_blocking_error(self) -> None:
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(2, 2, figsize=(4, 3))
        shifted = axes[0, 1].get_position()
        axes[0, 1].set_position([shifted.x0, shifted.y0 - 0.03, shifted.width, shifted.height])

        with self.assertRaises(AUDIT.PanelAlignmentError):
            AUDIT.require_matplotlib_panel_alignment(fig)
        plt.close(fig)


class PanelAlignmentWorkflowIntegrationTests(unittest.TestCase):
    def read(self, relative: str) -> str:
        return (ROOT / relative).read_text(encoding="utf-8")

    def test_python_and_r_helpers_share_one_blocking_contract(self) -> None:
        r_helper = self.read("skills/nature-figure/scripts/panel_alignment.R")
        python_helper = self.read("skills/nature-figure/scripts/audit_panel_alignment.py")

        for requirement in (
            "write_patchwork_panel_layout",
            "require_patchwork_panel_alignment",
            "audit_panel_alignment.py",
            "row_groups",
            "column_groups",
        ):
            self.assertIn(requirement, r_helper)
        self.assertIn("require_matplotlib_panel_alignment", python_helper)
        self.assertIn("DEFAULT_TOLERANCE_PT = 1.5", python_helper)

    def test_router_backends_docs_eval_and_version_require_alignment_gate(self) -> None:
        skill = self.read("skills/nature-figure/SKILL.md")
        manifest = self.read("skills/nature-figure/manifest.yaml")
        python_backend = self.read("skills/nature-figure/static/fragments/backend/python.md")
        r_backend = self.read("skills/nature-figure/static/fragments/backend/r.md")
        qa = self.read("skills/nature-figure/references/qa-contract.md")
        readme_zh = self.read("skills/nature-figure/README.md")
        readme_en = self.read("skills/nature-figure/README_EN.md")
        evals = json.loads(self.read("skills/nature-figure/evals/evals.json"))

        self.assertIn("version: 2.8.0", manifest)
        for relative, text in (
            ("SKILL.md", skill),
            ("python.md", python_backend),
            ("r.md", r_backend),
            ("qa-contract.md", qa),
            ("README.md", readme_zh),
            ("README_EN.md", readme_en),
        ):
            self.assertIn("audit_panel_alignment.py", text, relative)
        self.assertIn("panel_alignment.R", r_backend)
        self.assertIn("1.5 pt", qa)
        self.assertIn("left two + right one", qa)
        self.assertIn("three or four same-row panels", qa)
        eval_ids = {case["id"] for case in evals["evals"]}
        self.assertIn("multipanel-render-time-alignment-gate", eval_ids)
        self.assertIn("asymmetric-two-plus-one-panel-alignment", eval_ids)
        self.assertIn("horizontal-three-four-panel-equal-width", eval_ids)


if __name__ == "__main__":
    unittest.main()
