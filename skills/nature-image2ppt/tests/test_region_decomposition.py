from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from support import write_json

from inspect_region_decomposition import read_json, validate_manifest


def knowledge_graph_manifest(page: Path, *, distorted: bool = False, flattened: bool = False) -> Path:
    nodes = [
        ("node_concept", [100, 80, 24, 34] if distorted else [100, 85, 24, 24], [112, 97], [24, 24]),
        ("node_threshold", [100, 145, 24, 24], [112, 157], [24, 24]),
        ("node_exception", [100, 205, 24, 24], [112, 217], [24, 24]),
    ]
    shapes = [
        {"id": item_id, "type": "ellipse", "box_px": box}
        for item_id, box, _center, _size in nodes
    ]
    shapes.extend(
        [
            {
                "id": "edge_concept_threshold",
                "type": "line",
                "points_px": [112, 109, 112, 145],
                "end_arrow": "triangle",
            },
            {
                "id": "edge_threshold_exception",
                "type": "line",
                "points_px": [112, 169, 112, 205],
                "dash": "dash",
                "end_arrow": "triangle",
            },
        ]
    )
    manifest_ids = [item["id"] for item in shapes]
    anchors = [
        {
            "id": f"anchor-{item_id}",
            "kind": "circle-node",
            "manifest_id": item_id,
            "source_bbox_px": [center[0] - 12, center[1] - 12, 24, 24],
        }
        for item_id, _box, center, _size in nodes
    ]
    anchors.extend(
        [
            {
                "id": "anchor-edge-concept-threshold",
                "kind": "directed-connector",
                "manifest_id": "edge_concept_threshold",
                "source_points_px": [112, 109, 112, 145],
            },
            {
                "id": "anchor-edge-threshold-exception",
                "kind": "dashed-relationship",
                "manifest_id": "edge_threshold_exception",
                "source_points_px": [112, 169, 112, 205],
            },
        ]
    )
    compound = {
        "kind": "knowledge-graph",
        "object_inventory_complete": True,
        "measurement_reviewed": True,
        "native_object_policy": "measured-simple-objects-native",
        "nodes": [
            {
                "id": item_id.removeprefix("node_"),
                "manifest_id": item_id,
                "geometry": "circle",
                "source_center_px": center,
                "source_size_px": size,
                "position_tolerance_px": 2,
                "size_tolerance_px": 2,
            }
            for item_id, _box, center, size in nodes
        ],
        "edges": [
            {
                "id": "concept-threshold",
                "manifest_id": "edge_concept_threshold",
                "source_points_px": [112, 109, 112, 145],
                "line_style": "solid",
                "direction": "end",
            },
            {
                "id": "threshold-exception",
                "manifest_id": "edge_threshold_exception",
                "source_points_px": [112, 169, 112, 205],
                "line_style": "dashed",
                "direction": "end",
            },
        ],
    }
    region = {
        "id": "knowledge-graph",
        "label": "Supplementary Knowledge Graph Context",
        "source_bbox_px": [50, 40, 230, 240],
        "risk_level": "high",
        "strategy": "bounded-local-asset" if flattened else "native-object-decomposition",
        "reason": "Measured graph nodes and relationships.",
        "manifest_ids": {"shapes": manifest_ids, "text_boxes": [], "images": []},
        "protected_visual_anchors": anchors,
        "compound_diagram": compound,
    }
    empty_regions = [
        {
            "id": "title",
            "label": "Title",
            "source_bbox_px": [0, 0, 640, 40],
            "risk_level": "low",
            "strategy": "native-text-layout",
            "reason": "Simple title region.",
            "manifest_ids": {"shapes": [], "text_boxes": ["title_text"], "images": []},
            "protected_visual_anchors": [],
        },
        {
            "id": "legend",
            "label": "Legend",
            "source_bbox_px": [300, 40, 300, 100],
            "risk_level": "low",
            "strategy": "native-text-layout",
            "reason": "Simple legend region.",
            "manifest_ids": {"shapes": [], "text_boxes": ["legend_text"], "images": []},
            "protected_visual_anchors": [],
        },
    ]
    manifest = {
        "source": {"path": "source.png", "width_px": 640, "height_px": 360},
        "shapes": shapes,
        "text_boxes": [{"id": "title_text"}, {"id": "legend_text"}],
        "images": [],
        "image2ppt_region_decomposition": {
            "schema_version": "image2ppt-region-decomposition-v1",
            "page_complexity": "structured",
            "source_size_px": [640, 360],
            "regions": [*empty_regions, region],
        },
    }
    path = page / "manifest.json"
    write_json(path, manifest)
    return path


class RegionDecompositionTests(unittest.TestCase):
    def test_measured_knowledge_graph_nodes_and_edges_pass(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            path = knowledge_graph_manifest(Path(name))
            report = validate_manifest(read_json(path), path)
            self.assertTrue(report["passed"], report)
            self.assertEqual(report["summary"]["compound_regions"], 1)

    def test_distorted_circle_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            path = knowledge_graph_manifest(Path(name), distorted=True)
            report = validate_manifest(read_json(path), path)
            self.assertFalse(report["passed"])
            self.assertTrue(any("distorted ellipse" in item or "source size" in item for item in report["errors"]))

    def test_whole_compound_diagram_bitmap_strategy_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            path = knowledge_graph_manifest(Path(name), flattened=True)
            report = validate_manifest(read_json(path), path)
            self.assertFalse(report["passed"])
            self.assertTrue(any("cannot be replaced" in item for item in report["errors"]))


if __name__ == "__main__":
    unittest.main()
