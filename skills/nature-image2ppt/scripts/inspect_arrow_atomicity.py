#!/usr/bin/env python3
"""Verify one manifest arrow maps to one named PowerPoint object."""

from __future__ import annotations

import argparse
import json
import re
import zipfile
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

from postprocess_manifest_arrows import (
    CONNECTOR_PRESETS,
    NS,
    arrow_end_value,
    arrow_items,
    load_run_manifests,
    normalized,
    read_json,
    slide_sort_key,
    write_json,
)
from runtime_paths import resolve_inside


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def object_map(xml: bytes) -> dict[str, list[ET.Element]]:
    root = ET.fromstring(xml)
    sp_tree = root.find(".//p:spTree", NS)
    result: dict[str, list[ET.Element]] = {}
    if sp_tree is None:
        return result
    for child in list(sp_tree):
        marker = child.find(".//p:cNvPr", NS)
        if marker is None:
            continue
        result.setdefault(str(marker.get("name") or ""), []).append(child)
    return result


def object_text(obj: ET.Element) -> str:
    paragraphs: list[str] = []
    for paragraph in obj.findall(".//a:p", NS):
        paragraphs.append("".join(node.text or "" for node in paragraph.findall(".//a:t", NS)))
    return "\n".join(paragraphs)


def inspect_arrow(obj: ET.Element, item: dict[str, Any], role: str) -> tuple[dict[str, Any], list[str]]:
    errors: list[str] = []
    geometry = obj.find(".//a:prstGeom", NS)
    preset = geometry.get("prst") if geometry is not None else None
    details: dict[str, Any] = {
        "kind": local_name(obj.tag),
        "preset": preset,
        "text": object_text(obj),
    }
    if role == "connector":
        connector = str(item.get("connector") or "straight").lower()
        expected_preset = CONNECTOR_PRESETS.get(connector)
        line = obj.find(".//a:ln", NS)
        head = line.find("a:headEnd", NS) if line is not None else None
        tail = line.find("a:tailEnd", NS) if line is not None else None
        details.update(
            {
                "connector": connector,
                "start_arrow": head.get("type") if head is not None else None,
                "end_arrow": tail.get("type") if tail is not None else None,
            }
        )
        if details["kind"] != "cxnSp":
            errors.append("connector is not one p:cxnSp object")
        if preset != expected_preset:
            errors.append(f"connector preset is {preset!r}, expected {expected_preset!r}")
        expected_start = arrow_end_value(item.get("start_arrow"))
        expected_end = arrow_end_value(item.get("end_arrow"))
        if details["start_arrow"] != expected_start:
            errors.append(f"start arrowhead is {details['start_arrow']!r}, expected {expected_start!r}")
        if details["end_arrow"] != expected_end:
            errors.append(f"end arrowhead is {details['end_arrow']!r}, expected {expected_end!r}")
    else:
        expected_preset = str(item.get("preset") or "")
        if details["kind"] != "sp":
            errors.append("filled arrow is not one p:sp AutoShape")
        if normalized(preset) != normalized(expected_preset):
            errors.append(f"filled arrow preset is {preset!r}, expected {expected_preset!r}")
        if "text" in item and details["text"] != str(item.get("text") or ""):
            errors.append(f"embedded arrow text is {details['text']!r}, expected {item.get('text')!r}")
    return details, errors


def inspect(manifests: list[dict[str, Any]], pptx: Path) -> dict[str, Any]:
    errors: list[str] = []
    inspected: list[dict[str, Any]] = []
    with zipfile.ZipFile(pptx) as archive:
        slide_names = sorted(
            [name for name in archive.namelist() if re.fullmatch(r"ppt/slides/slide\d+\.xml", name)],
            key=slide_sort_key,
        )
        if len(slide_names) != len(manifests):
            errors.append(f"PPTX has {len(slide_names)} slides but {len(manifests)} manifests were supplied")
        for slide_index, (slide_name, manifest) in enumerate(zip(slide_names, manifests), start=1):
            objects = object_map(archive.read(slide_name))
            seen_ids: set[str] = set()
            for shape_index, item, role in arrow_items(manifest):
                object_id = str(item.get("id") or "").strip()
                if not object_id:
                    errors.append(f"slide {slide_index} shapes[{shape_index}] has no arrow id")
                    continue
                if object_id in seen_ids:
                    errors.append(f"slide {slide_index} repeats arrow id {object_id!r}")
                    continue
                seen_ids.add(object_id)
                matches = objects.get(object_id, [])
                if len(matches) != 1:
                    errors.append(
                        f"slide {slide_index} arrow {object_id!r} maps to {len(matches)} PowerPoint objects; expected exactly one"
                    )
                    continue
                details, object_errors = inspect_arrow(matches[0], item, role)
                errors.extend(f"slide {slide_index} {object_id}: {error}" for error in object_errors)
                inspected.append(
                    {
                        "slide_index": slide_index,
                        "shape_index": shape_index,
                        "id": object_id,
                        "role": role,
                        "pptx_object": details,
                    }
                )
    expected = sum(len(arrow_items(manifest)) for manifest in manifests)
    return {
        "schema_version": "image2ppt-manifest-arrow-inspection-v1",
        "passed": not errors and len(inspected) == expected,
        "pptx": str(pptx.resolve()),
        "errors": errors,
        "summary": {
            "expected_arrows": expected,
            "inspected_arrows": len(inspected),
            "connectors": sum(item["role"] == "connector" for item in inspected),
            "filled_arrows": sum(item["role"] == "filled" for item in inspected),
            "fragmented_or_missing": len(errors),
        },
        "arrows": inspected,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect Image2PPT arrows in an image2ppt-built PPTX")
    parser.add_argument("pptx", type=Path)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--manifest", type=Path)
    source.add_argument("--run", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.run:
        scope = args.run.expanduser().resolve()
        paths, _default = load_run_manifests(scope)
    else:
        manifest = args.manifest.expanduser().resolve()
        scope = manifest.parent
        paths = [manifest]
    try:
        pptx = resolve_inside(scope, args.pptx)
        out = resolve_inside(scope, args.out)
    except ValueError as exc:
        raise SystemExit(f"arrow inspection paths must stay inside {scope}") from exc
    try:
        report = inspect([read_json(path) for path in paths], pptx)
    except Exception as exc:
        report = {
            "schema_version": "image2ppt-manifest-arrow-inspection-v1",
            "passed": False,
            "errors": [repr(exc)],
            "summary": {"fragmented_or_missing": 1},
        }
    write_json(out, report)
    print(json.dumps(report, ensure_ascii=True, indent=2))
    return 0 if report["passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
