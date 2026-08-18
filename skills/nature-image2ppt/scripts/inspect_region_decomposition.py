#!/usr/bin/env python3
"""Validate Image2PPT region evidence against standard manifest objects."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

from postprocess_manifest_arrows import load_run_manifests
from runtime_paths import resolve_inside


SCHEMA = "image2ppt-region-decomposition-v1"
STRATEGIES = {
    "native-object-decomposition",
    "mixed-reconstruction",
    "bounded-local-asset",
    "native-text-layout",
}
ANCHOR_KINDS = {
    "circle-node",
    "ellipse-node",
    "document-node",
    "node-boundary",
    "connector",
    "directed-connector",
    "dashed-relationship",
    "arrowhead",
    "route-line",
    "smooth-curve",
    "junction",
    "card-edge",
    "divider",
    "marker",
    "icon",
    "label-anchor",
}


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def numbers(value: Any, length: int) -> list[float] | None:
    if not isinstance(value, list) or len(value) != length:
        return None
    if any(isinstance(item, bool) or not isinstance(item, (int, float)) for item in value):
        return None
    result = [float(item) for item in value]
    return result if all(math.isfinite(item) for item in result) else None


def inside_bbox(box: list[float], width: float, height: float) -> bool:
    x, y, w, h = box
    return x >= 0 and y >= 0 and w > 0 and h > 0 and x + w <= width + 0.01 and y + h <= height + 0.01


def item_map(manifest: dict[str, Any], key: str) -> tuple[dict[str, dict[str, Any]], list[str]]:
    result: dict[str, dict[str, Any]] = {}
    errors: list[str] = []
    for index, item in enumerate(manifest.get(key) or []):
        item_id = str(item.get("id") or "").strip()
        if not item_id:
            errors.append(f"{key}[{index}] has no stable id")
        elif item_id in result:
            errors.append(f"duplicate {key} id: {item_id}")
        else:
            result[item_id] = item
    return result, errors


def close(actual: float, expected: float, tolerance: float) -> bool:
    return abs(actual - expected) <= tolerance + 1e-6


def validate_manifest(manifest: dict[str, Any], manifest_path: Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    shapes, item_errors = item_map(manifest, "shapes")
    errors.extend(item_errors)
    text_boxes, item_errors = item_map(manifest, "text_boxes")
    errors.extend(item_errors)
    images, item_errors = item_map(manifest, "images")
    errors.extend(item_errors)
    all_objects = {**shapes, **text_boxes, **images}

    block = manifest.get("image2ppt_region_decomposition")
    if not isinstance(block, dict):
        errors.append("manifest is missing image2ppt_region_decomposition")
        block = {}
    if block.get("schema_version") != SCHEMA:
        errors.append(f"region schema_version must be {SCHEMA}")

    source = manifest.get("source") or {}
    declared_size = numbers(block.get("source_size_px"), 2)
    manifest_size = numbers([source.get("width_px"), source.get("height_px")], 2)
    if not declared_size or declared_size[0] <= 0 or declared_size[1] <= 0:
        errors.append("source_size_px must contain positive source width and height")
        source_width, source_height = 1.0, 1.0
    else:
        source_width, source_height = declared_size
        if manifest_size and any(not close(a, b, 0.01) for a, b in zip(declared_size, manifest_size)):
            errors.append("source_size_px does not match manifest.source dimensions")

    complexity = block.get("page_complexity")
    if complexity not in {"simple", "structured"}:
        errors.append("page_complexity must be simple or structured")
    regions = block.get("regions")
    if not isinstance(regions, list) or not regions:
        errors.append("regions must be a non-empty list")
        regions = []
    if complexity == "structured" and not 3 <= len(regions) <= 5:
        errors.append("structured pages require 3-5 semantic regions")
    if complexity == "simple" and not 1 <= len(regions) <= 2:
        errors.append("simple pages require 1-2 semantic regions")

    seen_regions: set[str] = set()
    referenced: set[str] = set()
    region_results: list[dict[str, Any]] = []
    for region_index, region in enumerate(regions):
        prefix = f"regions[{region_index}]"
        region_errors: list[str] = []
        if not isinstance(region, dict):
            errors.append(f"{prefix} must be an object")
            continue
        region_id = str(region.get("id") or "").strip()
        if not region_id:
            region_errors.append("missing id")
        elif region_id in seen_regions:
            region_errors.append(f"duplicate region id: {region_id}")
        seen_regions.add(region_id)
        if not str(region.get("label") or "").strip():
            region_errors.append("missing label")
        bbox = numbers(region.get("source_bbox_px"), 4)
        if not bbox or not inside_bbox(bbox, source_width, source_height):
            region_errors.append("source_bbox_px is invalid or outside the source")
        risk = region.get("risk_level")
        if risk not in {"low", "medium", "high"}:
            region_errors.append("risk_level must be low, medium, or high")
        strategy = region.get("strategy")
        if strategy not in STRATEGIES:
            region_errors.append(f"unsupported strategy: {strategy}")
        if not str(region.get("reason") or "").strip():
            region_errors.append("strategy reason is required")

        ids = region.get("manifest_ids")
        if not isinstance(ids, dict):
            region_errors.append("manifest_ids is required")
            ids = {}
        for key, mapping in (("shapes", shapes), ("text_boxes", text_boxes), ("images", images)):
            values = ids.get(key, [])
            if not isinstance(values, list) or any(not isinstance(item, str) or not item for item in values):
                region_errors.append(f"manifest_ids.{key} must be a list of ids")
                continue
            for item_id in values:
                referenced.add(item_id)
                if item_id not in mapping:
                    region_errors.append(f"manifest_ids.{key} references missing object: {item_id}")
        if not any(ids.get(key) for key in ("shapes", "text_boxes", "images")):
            region_errors.append("region has no manifest object evidence")

        anchors = region.get("protected_visual_anchors", [])
        if not isinstance(anchors, list):
            region_errors.append("protected_visual_anchors must be a list")
            anchors = []
        if risk == "high" and not anchors:
            region_errors.append("high-risk region has no protected visual anchors")
        anchor_manifest_ids: set[str] = set()
        anchor_ids: set[str] = set()
        for anchor_index, anchor in enumerate(anchors):
            anchor_prefix = f"anchor[{anchor_index}]"
            if not isinstance(anchor, dict):
                region_errors.append(f"{anchor_prefix} must be an object")
                continue
            anchor_id = str(anchor.get("id") or "").strip()
            if not anchor_id or anchor_id in anchor_ids:
                region_errors.append(f"{anchor_prefix} needs a unique id")
            anchor_ids.add(anchor_id)
            if anchor.get("kind") not in ANCHOR_KINDS:
                region_errors.append(f"{anchor_prefix} has unsupported kind")
            manifest_id = str(anchor.get("manifest_id") or "").strip()
            if not manifest_id or manifest_id not in all_objects:
                region_errors.append(f"{anchor_prefix} references missing manifest object: {manifest_id}")
            anchor_manifest_ids.add(manifest_id)
            anchor_bbox = numbers(anchor.get("source_bbox_px"), 4)
            anchor_points = numbers(anchor.get("source_points_px"), 4)
            if anchor_bbox is None and anchor_points is None:
                region_errors.append(f"{anchor_prefix} needs source_bbox_px or source_points_px")
            if anchor_bbox is not None and not inside_bbox(anchor_bbox, source_width, source_height):
                region_errors.append(f"{anchor_prefix} source_bbox_px is outside the source")

        compound = region.get("compound_diagram")
        if compound is not None:
            if not isinstance(compound, dict):
                region_errors.append("compound_diagram must be an object")
                compound = {}
            if strategy == "bounded-local-asset":
                region_errors.append("compound diagrams cannot be replaced by one bounded-local-asset region")
            if compound.get("kind") not in {
                "knowledge-graph", "node-link-diagram", "workflow", "matrix", "compound-diagram"
            }:
                region_errors.append("compound_diagram.kind is unsupported")
            if compound.get("object_inventory_complete") is not True:
                region_errors.append("compound diagram object inventory is not marked complete")
            if compound.get("measurement_reviewed") is not True:
                region_errors.append("compound diagram measurements are not marked reviewed")
            if compound.get("native_object_policy") != "measured-simple-objects-native":
                region_errors.append("compound diagram must keep measurable simple objects native")

            compound_manifest_ids: set[str] = set()
            nodes = compound.get("nodes")
            if not isinstance(nodes, list) or not nodes:
                region_errors.append("compound diagram needs a non-empty nodes inventory")
                nodes = []
            for node_index, node in enumerate(nodes):
                node_prefix = f"node[{node_index}]"
                if not isinstance(node, dict):
                    region_errors.append(f"{node_prefix} must be an object")
                    continue
                manifest_id = str(node.get("manifest_id") or "").strip()
                compound_manifest_ids.add(manifest_id)
                shape = shapes.get(manifest_id)
                if shape is None:
                    region_errors.append(f"{node_prefix} references missing native shape: {manifest_id}")
                    continue
                center = numbers(node.get("source_center_px"), 2)
                size = numbers(node.get("source_size_px"), 2)
                box = numbers(shape.get("box_px"), 4)
                if not center or not size or not box or size[0] <= 0 or size[1] <= 0:
                    region_errors.append(f"{node_prefix} needs valid measured center/size and manifest box_px")
                    continue
                position_tolerance = float(node.get("position_tolerance_px", 2))
                size_tolerance = float(node.get("size_tolerance_px", 2))
                actual_center = [box[0] + box[2] / 2, box[1] + box[3] / 2]
                if any(not close(a, b, position_tolerance) for a, b in zip(actual_center, center)):
                    region_errors.append(f"{node_prefix} manifest center differs from reviewed source center")
                if any(not close(a, b, size_tolerance) for a, b in zip(box[2:], size)):
                    region_errors.append(f"{node_prefix} manifest size differs from reviewed source size")
                geometry = node.get("geometry")
                if geometry not in {"circle", "ellipse", "rect", "roundRect", "document", "complex-asset"}:
                    region_errors.append(f"{node_prefix} has unsupported geometry")
                if geometry == "circle":
                    if not close(size[0], size[1], size_tolerance):
                        region_errors.append(f"{node_prefix} reviewed circle width and height differ")
                    if not close(box[2], box[3], size_tolerance):
                        region_errors.append(f"{node_prefix} native circle is implemented as a distorted ellipse")
                    if str(shape.get("type") or shape.get("preset") or "").lower() not in {"ellipse", "oval"}:
                        region_errors.append(f"{node_prefix} circle is not an ellipse/oval native shape")

            edges = compound.get("edges", [])
            if not isinstance(edges, list):
                region_errors.append("compound_diagram.edges must be a list")
                edges = []
            for edge_index, edge in enumerate(edges):
                edge_prefix = f"edge[{edge_index}]"
                if not isinstance(edge, dict):
                    region_errors.append(f"{edge_prefix} must be an object")
                    continue
                manifest_id = str(edge.get("manifest_id") or "").strip()
                compound_manifest_ids.add(manifest_id)
                shape = shapes.get(manifest_id)
                if shape is None:
                    region_errors.append(f"{edge_prefix} references missing native connector: {manifest_id}")
                    continue
                expected_points = numbers(edge.get("source_points_px"), 4)
                actual_points = numbers(shape.get("points_px"), 4)
                tolerance = float(edge.get("position_tolerance_px", 3))
                if not expected_points or not actual_points:
                    region_errors.append(f"{edge_prefix} needs measured source_points_px and manifest points_px")
                elif any(not close(a, b, tolerance) for a, b in zip(actual_points, expected_points)):
                    region_errors.append(f"{edge_prefix} manifest endpoints differ from reviewed source endpoints")
                if str(shape.get("type") or "").lower() != "line":
                    region_errors.append(f"{edge_prefix} is not a native line/connector")
                line_style = edge.get("line_style")
                if line_style not in {"solid", "dashed"}:
                    region_errors.append(f"{edge_prefix} line_style must be solid or dashed")
                if line_style == "dashed" and not shape.get("dash"):
                    region_errors.append(f"{edge_prefix} reviewed dashed relationship is not dashed in manifest")
                direction = edge.get("direction")
                if direction not in {"none", "start", "end", "both"}:
                    region_errors.append(f"{edge_prefix} direction is invalid")
                if direction in {"start", "both"} and str(shape.get("start_arrow") or "none") == "none":
                    region_errors.append(f"{edge_prefix} is missing its start arrowhead")
                if direction in {"end", "both"} and str(shape.get("end_arrow") or "none") == "none":
                    region_errors.append(f"{edge_prefix} is missing its end arrowhead")

            missing_anchors = sorted(item for item in compound_manifest_ids if item and item not in anchor_manifest_ids)
            if missing_anchors:
                region_errors.append(
                    "compound nodes/edges missing protected anchors: " + ", ".join(missing_anchors)
                )

        errors.extend(f"{prefix}: {message}" for message in region_errors)
        region_results.append(
            {
                "id": region_id,
                "strategy": strategy,
                "risk_level": risk,
                "manifest_object_count": sum(len(ids.get(key, [])) for key in ("shapes", "text_boxes", "images")),
                "protected_anchor_count": len(anchors),
                "compound_diagram": compound is not None,
                "passed": not region_errors,
                "errors": region_errors,
            }
        )

    unassigned = sorted(set(all_objects) - referenced)
    if unassigned:
        errors.append("manifest objects are not assigned to semantic regions: " + ", ".join(unassigned))

    return {
        "manifest": str(manifest_path),
        "passed": not errors,
        "page_complexity": complexity,
        "region_count": len(regions),
        "regions": region_results,
        "summary": {
            "manifest_objects": len(all_objects),
            "assigned_objects": len(referenced),
            "protected_anchors": sum(item["protected_anchor_count"] for item in region_results),
            "compound_regions": sum(1 for item in region_results if item["compound_diagram"]),
        },
        "warnings": warnings,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate semantic regions and compound-diagram measurements")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--manifest", type=Path)
    source.add_argument("--run", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    if args.run:
        scope = args.run.expanduser().resolve()
        manifest_paths, _ = load_run_manifests(scope)
    else:
        manifest = args.manifest.expanduser().resolve()
        scope = manifest.parent
        manifest_paths = [manifest]
    try:
        out = resolve_inside(scope, args.out)
    except ValueError as exc:
        raise SystemExit(f"region report must stay inside {scope}: {args.out}") from exc
    pages: list[dict[str, Any]] = []
    errors: list[str] = []
    for path in manifest_paths:
        try:
            result = validate_manifest(read_json(path), path)
        except (OSError, ValueError, TypeError) as exc:
            result = {"manifest": str(path), "passed": False, "errors": [repr(exc)]}
        pages.append(result)
        errors.extend(f"{path.name}: {message}" for message in result.get("errors") or [])
    report = {
        "schema_version": "image2ppt-region-decomposition-report-v1",
        "passed": bool(pages) and all(page.get("passed") is True for page in pages),
        "pages": pages,
        "summary": {
            "pages": len(pages),
            "regions": sum(int(page.get("region_count") or 0) for page in pages),
            "compound_regions": sum(int((page.get("summary") or {}).get("compound_regions") or 0) for page in pages),
        },
        "errors": errors,
    }
    write_json(out, report)
    print(json.dumps(report, ensure_ascii=True, indent=2))
    return 0 if report["passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
