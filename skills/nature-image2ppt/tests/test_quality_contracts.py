import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNTIME_DIR = ROOT / "cli/image2ppt/runtime"
sys.path.insert(0, str(RUNTIME_DIR))

from validate_pptx import ALLOWED_SOURCE_TYPES, quality_contract_violations, required_texts_from_manifest  # noqa: E402
from build_pptx_from_manifest import shape_xml  # noqa: E402


def base_manifest():
    return {
        "visual_inventory": [],
        "background_strategy": {
            "mode": "native-or-script",
            "comparison_note": "background checked against source",
        },
        "quality_checks": {
            "font_size_calibrated": True,
            "visual_inventory_matched": True,
            "background_strategy_checked": True,
            "shape_corner_geometry_checked": True,
        },
        "shapes": [],
    }


def v2_manifest():
    manifest = base_manifest()
    manifest["schema_version"] = 2
    manifest["quality_evidence"] = {
        key: {"observation": f"Verified {key} against the source image and current render."}
        for key in manifest["quality_checks"]
    }
    return manifest


class QualityContractTest(unittest.TestCase):
    def test_quality_checks_are_required(self):
        violations = quality_contract_violations({})
        fields = {item["field"] for item in violations}
        self.assertIn("visual_inventory", fields)
        self.assertIn("background_strategy", fields)
        self.assertIn("quality_checks", fields)

    def test_round_rect_requires_source_evidence(self):
        manifest = base_manifest()
        manifest["shapes"] = [{"type": "roundRect", "box_px": [0, 0, 100, 40]}]
        violations = quality_contract_violations(manifest)
        self.assertEqual(["shapes[0]"], [item["field"] for item in violations])

    def test_rect_does_not_need_corner_evidence(self):
        manifest = base_manifest()
        manifest["shapes"] = [{"type": "rect", "box_px": [0, 0, 100, 40]}]
        self.assertEqual([], quality_contract_violations(manifest))

    def test_source_derived_assets_are_not_allowed(self):
        self.assertNotIn("source-derived-rasterization", ALLOWED_SOURCE_TYPES)

    def test_latex_rendered_formula_assets_are_allowed(self):
        self.assertIn("latex-rendered-formula", ALLOWED_SOURCE_TYPES)

    def test_asset_sheet_separated_assets_are_allowed(self):
        self.assertIn("asset-sheet-separated", ALLOWED_SOURCE_TYPES)

    def test_foreground_native_approximation_is_contract_violation(self):
        manifest = base_manifest()
        manifest["visual_inventory"] = [
            {
                "id": "bottom_icon",
                "description": "semantic icon in the bottom flow",
                "decision": "native approximation with text symbol",
            }
        ]
        violations = quality_contract_violations(manifest)
        reasons = " ".join(item["reason"] for item in violations)
        self.assertIn("foreground visual decisions", reasons)

    def test_foreground_direct_crop_provenance_is_contract_violation(self):
        manifest = base_manifest()
        manifest["visual_inventory"] = [
            {
                "id": "photo_panel",
                "description": "foreground photo panel",
                "decision": "source-faithful asset-sheet separation",
                "path": "assets/source_crops/photo.png",
            }
        ]
        manifest["asset_provenance"] = [
            {
                "path": "assets/source_crops/photo.png",
                "source_type": "user-provided",
                "source": "source.png",
                "provenance_note": "cropped from source foreground photo",
            }
        ]
        violations = quality_contract_violations(manifest)
        fields = [item["field"] for item in violations]
        self.assertIn("visual_inventory[0]", fields)
        self.assertIn("asset_provenance[0]", fields)

    def test_foreground_asset_sheet_decision_passes_contract(self):
        manifest = base_manifest()
        manifest["visual_inventory"] = [
            {
                "id": "photo_panel",
                "description": "foreground photo panel",
                "decision": "source-faithful asset-sheet separation through image2ppt image edit",
                "path": "assets/photo_panel.png",
            }
        ]
        manifest["asset_provenance"] = [
            {
                "path": "assets/photo_panel.png",
                "source_type": "asset-sheet-separated",
                "source": "assets/photo_sheet.png",
                "provenance_note": "split from source-faithful asset sheet generated with image2ppt image edit",
            }
        ]
        self.assertEqual([], quality_contract_violations(manifest))

    def test_structured_native_item_avoids_benchmark_substring_false_positive(self):
        manifest = v2_manifest()
        manifest["visual_inventory"] = [
            {
                "id": "benchmark_panel",
                "kind": "native-structure",
                "representation": "native",
                "description": "benchmark result panel",
            }
        ]
        self.assertEqual([], quality_contract_violations(manifest))

    def test_structured_foreground_item_cannot_hide_behind_background_word(self):
        manifest = v2_manifest()
        manifest["visual_inventory"] = [
            {
                "id": "icon",
                "kind": "foreground-asset",
                "representation": "native",
                "description": "foreground icon over background",
            }
        ]
        reasons = " ".join(item["reason"] for item in quality_contract_violations(manifest))
        self.assertIn("foreground-asset requires", reasons)

    def test_unrendered_formula_is_a_hard_failure_without_user_approval(self):
        manifest = v2_manifest()
        manifest["formula_inventory"] = [
            {"id": "f1", "status": "failed", "tex_source": "assets/f1.tex"}
        ]
        reasons = " ".join(item["reason"] for item in quality_contract_violations(manifest))
        self.assertIn("hard failure", reasons)

    def test_formula_visual_requires_formula_inventory(self):
        manifest = v2_manifest()
        manifest["visual_inventory"] = [
            {
                "id": "f1",
                "kind": "formula",
                "representation": "latex-rendered-formula",
                "path": "assets/f1.svg",
            }
        ]
        reasons = " ".join(item["reason"] for item in quality_contract_violations(manifest))
        self.assertIn("matching formula_inventory", reasons)

    def test_user_approved_formula_exception_requires_and_accepts_concrete_note(self):
        manifest = v2_manifest()
        manifest["formula_inventory"] = [
            {
                "id": "f1",
                "status": "failed",
                "tex_source": "assets/f1.tex",
                "user_approved_exception": True,
                "approval_note": "User explicitly approved delivery without this secondary formula.",
            }
        ]
        self.assertEqual([], quality_contract_violations(manifest))

    def test_v2_quality_booleans_require_specific_evidence(self):
        manifest = v2_manifest()
        manifest["quality_evidence"]["visual_inventory_matched"] = {"observation": "checked"}
        fields = [item["field"] for item in quality_contract_violations(manifest)]
        self.assertIn("quality_evidence.visual_inventory_matched.observation", fields)

    def test_round_rect_writes_ooxml_adjustment(self):
        xml = shape_xml(
            2,
            {
                "type": "roundRect",
                "box_px": [0, 0, 400, 200],
                "left": 0,
                "top": 0,
                "width": 4,
                "height": 2,
                "source_corner_radius_px": 10,
                "fill": "none",
                "stroke": "#000000",
            },
        )
        self.assertIn('prst="roundRect"', xml)
        self.assertIn('name="adj"', xml)
        self.assertIn('fmla="val 5000"', xml)

    def test_structured_text_inventory_flattens_to_required_strings(self):
        required = required_texts_from_manifest(
            {
                "required_text": ["市场概览"],
                "text_inventory": [
                    {"id": "metric", "text": "4280 万", "decision": "native-text"},
                    {"id": "insights", "required_text": ["扩张", "续约"]},
                    {"id": "note", "description": "not an exact text requirement"},
                ],
            }
        )
        self.assertEqual(["市场概览", "4280 万", "扩张", "续约"], required)

    def test_invalid_text_alignment_is_a_contract_violation(self):
        manifest = base_manifest()
        manifest["text_boxes"] = [
            {
                "text": "1",
                "box_px": [0, 0, 40, 40],
                "align": "sideways",
                "valign": "floating",
            }
        ]

        violations = quality_contract_violations(manifest)
        fields = {item["field"] for item in violations}

        self.assertIn("text_boxes[0].align", fields)
        self.assertIn("text_boxes[0].valign", fields)


if __name__ == "__main__":
    unittest.main()
