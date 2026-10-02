from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

from PIL import Image

from support import SCRIPTS, build_deck, build_page, write_json


NS = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
}


def run_ok(command: list[str]) -> None:
    result = subprocess.run(command, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        raise AssertionError(result.stdout + result.stderr)


def graph_manifest(page: Path) -> Path:
    page.mkdir(parents=True)
    Image.new("RGB", (800, 450), "white").save(page / "source.png")
    nodes = []
    node_shapes = []
    node_anchors = []
    for index in range(42):
        row, column = divmod(index, 7)
        x = 70 + column * 85
        y = 65 + row * 44
        item_id = f"kg_node_{index + 1:02d}"
        node_shapes.append(
            {
                "id": item_id,
                "type": "ellipse",
                "box_px": [x, y, 22, 22],
                "fill": "#E8F2FF",
                "stroke": "#2563EB",
                "stroke_width": 1.2,
                "z_index": 100 + index,
            }
        )
        nodes.append(
            {
                "id": f"node-{index + 1:02d}",
                "manifest_id": item_id,
                "geometry": "circle",
                "source_center_px": [x + 11, y + 11],
                "source_size_px": [22, 22],
                "position_tolerance_px": 1,
                "size_tolerance_px": 1,
            }
        )
        node_anchors.append(
            {
                "id": f"anchor-{item_id}",
                "kind": "circle-node",
                "manifest_id": item_id,
                "source_bbox_px": [x, y, 22, 22],
            }
        )

    edges = []
    edge_shapes = []
    edge_anchors = []
    for index in range(41):
        start = nodes[index]["source_center_px"]
        end = nodes[index + 1]["source_center_px"]
        item_id = f"kg_edge_{index + 1:02d}"
        dashed = index % 5 == 4
        shape = {
            "id": item_id,
            "type": "line",
            "points_px": [*start, *end],
            "stroke": "#64748B",
            "stroke_width": 1.0,
            "connector": "straight",
            "start_arrow": "none",
            "end_arrow": "triangle",
            "z_index": 20 + index,
        }
        if dashed:
            shape["dash"] = "dash"
        edge_shapes.append(shape)
        edges.append(
            {
                "id": f"edge-{index + 1:02d}",
                "manifest_id": item_id,
                "source_points_px": [*start, *end],
                "line_style": "dashed" if dashed else "solid",
                "direction": "end",
                "position_tolerance_px": 1,
            }
        )
        edge_anchors.append(
            {
                "id": f"anchor-{item_id}",
                "kind": "dashed-relationship" if dashed else "directed-connector",
                "manifest_id": item_id,
                "source_points_px": [*start, *end],
            }
        )

    thin_arrow = {
        "id": "standalone_thin_arrow",
        "type": "line",
        "points_px": [100, 390, 300, 390],
        "stroke": "#0F766E",
        "stroke_width": 2.5,
        "connector": "straight",
        "start_arrow": "none",
        "end_arrow": "triangle",
        "z_index": 250,
    }
    filled_arrow = {
        "id": "standalone_filled_arrow",
        "type": "shape",
        "preset": "rightArrow",
        "box_px": [380, 365, 230, 55],
        "fill": "#2563EB",
        "stroke": "none",
        "text": "下一阶段",
        "font_size": 14,
        "text_color": "#FFFFFF",
        "align": "center",
        "valign": "middle",
        "z_index": 260,
    }
    graph_shape_ids = [item["id"] for item in [*node_shapes, *edge_shapes]]
    manifest = {
        "schema_version": 1,
        "slide": {"width": 13.333, "height": 7.5, "background": "#FFFFFF"},
        "content_box": {"left": 0, "top": 0, "width": 13.333, "height": 7.5},
        "source": {"path": "source.png", "width_px": 800, "height_px": 450},
        "page_strategy": "native-structure",
        "required_text": ["Knowledge Graph", "下一阶段"],
        "text_inventory": ["Knowledge Graph", "下一阶段"],
        "visual_inventory": [
            {"id": "graph", "description": "native structural measured knowledge graph", "decision": "native structure"},
            {"id": "arrows", "description": "native structural ordinary arrows", "decision": "native structure"},
        ],
        "background_strategy": {
            "mode": "native-or-script",
            "source_consistency_contract": "solid white source background",
            "removed_foreground": [],
            "comparison_note": "solid white background matched",
        },
        "quality_checks": {
            "font_size_calibrated": True,
            "visual_inventory_matched": True,
            "background_strategy_checked": True,
            "shape_corner_geometry_checked": True,
        },
        "text_boxes": [
            {
                "id": "title",
                "text": "Knowledge Graph",
                "box_px": [30, 10, 400, 35],
                "font_size": 20,
                "font_size_source": "measured",
                "color": "#111827",
                "z_index": 300,
            }
        ],
        "shapes": [*edge_shapes, *node_shapes, thin_arrow, filled_arrow],
        "images": [],
        "asset_provenance": [],
        "image2ppt_region_decomposition": {
            "schema_version": "image2ppt-region-decomposition-v1",
            "page_complexity": "structured",
            "source_size_px": [800, 450],
            "regions": [
                {
                    "id": "title-region",
                    "label": "Title",
                    "source_bbox_px": [0, 0, 800, 50],
                    "risk_level": "low",
                    "strategy": "native-text-layout",
                    "reason": "Measured native title.",
                    "manifest_ids": {"shapes": [], "text_boxes": ["title"], "images": []},
                    "protected_visual_anchors": [],
                },
                {
                    "id": "knowledge-graph-region",
                    "label": "42-node knowledge graph",
                    "source_bbox_px": [40, 50, 650, 300],
                    "risk_level": "high",
                    "strategy": "native-object-decomposition",
                    "reason": "All 42 circles and 41 directed relationships are individually measured.",
                    "manifest_ids": {"shapes": graph_shape_ids, "text_boxes": [], "images": []},
                    "protected_visual_anchors": [*node_anchors, *edge_anchors],
                    "compound_diagram": {
                        "kind": "knowledge-graph",
                        "object_inventory_complete": True,
                        "measurement_reviewed": True,
                        "native_object_policy": "measured-simple-objects-native",
                        "nodes": nodes,
                        "edges": edges,
                    },
                },
                {
                    "id": "arrow-region",
                    "label": "Arrow examples",
                    "source_bbox_px": [40, 350, 700, 90],
                    "risk_level": "medium",
                    "strategy": "native-object-decomposition",
                    "reason": "Ordinary arrows are single native objects.",
                    "manifest_ids": {
                        "shapes": [thin_arrow["id"], filled_arrow["id"]],
                        "text_boxes": [],
                        "images": [],
                    },
                    "protected_visual_anchors": [
                        {
                            "id": "anchor-standalone-thin",
                            "kind": "directed-connector",
                            "manifest_id": thin_arrow["id"],
                            "source_points_px": thin_arrow["points_px"],
                        },
                        {
                            "id": "anchor-standalone-filled",
                            "kind": "route-line",
                            "manifest_id": filled_arrow["id"],
                            "source_bbox_px": filled_arrow["box_px"],
                        },
                    ],
                },
            ],
        },
    }
    path = page / "manifest.json"
    write_json(path, manifest)
    write_json(page / "imagegen-jobs.json", {"schema_version": 1, "jobs": []})
    return path


def slide_xml(pptx: Path) -> ET.Element:
    with zipfile.ZipFile(pptx) as archive:
        return ET.fromstring(archive.read("ppt/slides/slide1.xml"))


def structure_counts(pptx: Path) -> dict[str, int]:
    root = slide_xml(pptx)
    ellipses = 0
    filled = 0
    for shape in root.findall(".//p:sp", NS):
        geom = shape.find(".//a:prstGeom", NS)
        if geom is not None and geom.get("prst") == "ellipse":
            ellipses += 1
        if geom is not None and geom.get("prst") == "rightArrow":
            filled += 1
    return {
        "circle_nodes": ellipses,
        "connectors": len(root.findall(".//p:cxnSp", NS)),
        "filled_arrows": filled,
        "pictures": len(root.findall(".//p:pic", NS)),
    }


class StructureReconstructionTests(unittest.TestCase):
    def test_42_native_nodes_relations_and_atomic_arrows_survive_final_build(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run = Path(tmp)
            page = run / "pages" / "page_001"
            manifest = graph_manifest(page)
            page_pptx = build_page(page)
            region_report = page / "region-report.json"
            run_ok(
                [sys.executable, str(SCRIPTS / "inspect_region_decomposition.py"), "--manifest", str(manifest), "--out", str(region_report)]
            )
            page_arrow_report = page / "arrow-postprocess.json"
            run_ok(
                [sys.executable, str(SCRIPTS / "postprocess_manifest_arrows.py"), str(page_pptx), "--manifest", str(manifest), "--report", str(page_arrow_report)]
            )
            page_inspection = page / "arrow-inspection.json"
            run_ok(
                [sys.executable, str(SCRIPTS / "inspect_arrow_atomicity.py"), str(page_pptx), "--manifest", str(manifest), "--out", str(page_inspection)]
            )
            counts = structure_counts(page_pptx)
            self.assertEqual(counts["circle_nodes"], 42)
            self.assertEqual(counts["connectors"], 42)  # 41 relations + one standalone thin arrow
            self.assertEqual(counts["filled_arrows"], 1)
            self.assertEqual(counts["pictures"], 0)
            region = json.loads(region_report.read_text(encoding="utf-8"))
            self.assertTrue(region["passed"], region)
            self.assertEqual(region["pages"][0]["region_count"], 3)
            arrows = json.loads(page_inspection.read_text(encoding="utf-8"))
            self.assertTrue(arrows["passed"], arrows)
            self.assertEqual(arrows["summary"]["connectors"], 42)
            self.assertEqual(arrows["summary"]["filled_arrows"], 1)

            final = run / "final" / "deck_edited.pptx"
            write_json(
                run / "deck_manifest.json",
                {
                    "schema_version": 1,
                    "job_dir": str(run),
                    "page_count": 1,
                    "slide": {"width": 13.333, "height": 7.5},
                    "pages": [{"page_id": "page_001", "manifest": "pages/page_001/manifest.json", "source_image": "pages/page_001/source.png"}],
                    "output": "final/deck_edited.pptx",
                },
            )
            final.parent.mkdir(parents=True, exist_ok=True)
            build_deck(run / "deck_manifest.json", final)
            final_arrow_report = final.parent / "arrow-postprocess.json"
            run_ok(
                [sys.executable, str(SCRIPTS / "postprocess_manifest_arrows.py"), str(final), "--run", str(run), "--report", str(final_arrow_report)]
            )
            final_inspection = final.parent / "arrow-inspection.json"
            run_ok(
                [sys.executable, str(SCRIPTS / "inspect_arrow_atomicity.py"), str(final), "--run", str(run), "--out", str(final_inspection)]
            )
            self.assertEqual(structure_counts(final), counts)
            self.assertTrue(json.loads(final_inspection.read_text(encoding="utf-8"))["passed"])


if __name__ == "__main__":
    unittest.main()
