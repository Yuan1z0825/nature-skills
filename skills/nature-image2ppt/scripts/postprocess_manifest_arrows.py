#!/usr/bin/env python3
"""Apply Image2PPT arrow extensions to an image2ppt-built PPTX.

The local builder remains the sole packager.  This script only rewrites
the slide XML objects that correspond to arrow-enabled ``shapes[]`` entries in
the authoritative standard ``manifest.json``.  Every other package part,
including speaker notes and media, is copied byte-for-byte.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
import zipfile
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

from runtime_paths import resolve_inside


NS = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
}
for prefix, uri in NS.items():
    ET.register_namespace(prefix, uri)


ARROW_PRESETS = {
    "rightarrow",
    "leftarrow",
    "uparrow",
    "downarrow",
    "leftrightarrow",
    "updownarrow",
    "quadarrow",
    "leftrightuparrow",
    "bentarrow",
    "uturnarrow",
    "stripedrightarrow",
    "notchedrightarrow",
    "chevron",
    "homeplate",
}
CONNECTOR_PRESETS = {
    "straight": "line",
    "elbow": "bentConnector3",
    "curve": "curvedConnector3",
    "curved": "curvedConnector3",
}
ARROW_TYPES = {
    "arrow": "arrow",
    "triangle": "triangle",
    "stealth": "stealth",
    "diamond": "diamond",
    "oval": "oval",
}
ARROW_SIZES = {"sm", "med", "lg"}


def qname(prefix: str, local: str) -> str:
    return f"{{{NS[prefix]}}}{local}"


def normalized(value: Any) -> str:
    return re.sub(r"[^a-z0-9]", "", str(value or "").lower())


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def arrow_role(item: dict[str, Any]) -> str | None:
    if str(item.get("type") or "").lower() == "line":
        start = normalized(item.get("start_arrow"))
        end = normalized(item.get("end_arrow"))
        if start not in {"", "none", "false", "0"} or end not in {"", "none", "false", "0"}:
            return "connector"
    preset = normalized(item.get("preset"))
    if preset in ARROW_PRESETS:
        return "filled"
    return None


def arrow_items(manifest: dict[str, Any]) -> list[tuple[int, dict[str, Any], str]]:
    return [
        (index, item, role)
        for index, item in enumerate(manifest.get("shapes") or [])
        if (role := arrow_role(item)) is not None
    ]


def shape_object_ids(manifest: dict[str, Any]) -> dict[int, int]:
    """Mirror the local builder's stable z-order-to-OOXML-id mapping."""

    layered: list[tuple[float, int, str, int]] = []
    for index, item in enumerate(manifest.get("shapes") or []):
        layered.append((float(item.get("z_index", 100)), index, "shape", index))
    for index, item in enumerate(manifest.get("images") or []):
        layered.append((float(item.get("z_index", 200)), index, "image", index))
    for index, item in enumerate(manifest.get("text_boxes") or []):
        layered.append((float(item.get("z_index", 300)), index, "text", index))
    result: dict[int, int] = {}
    # Python's stable sort preserves the source builder's append order for ties.
    for object_id, entry in enumerate(sorted(layered, key=lambda value: (value[0], value[1])), start=2):
        if entry[2] == "shape":
            result[entry[3]] = object_id
    return result


def find_object(sp_tree: ET.Element, object_id: int) -> ET.Element | None:
    for child in list(sp_tree):
        marker = child.find(".//p:cNvPr", NS)
        if marker is not None and marker.get("id") == str(object_id):
            return child
    return None


def set_object_name(obj: ET.Element, value: str) -> None:
    marker = obj.find(".//p:cNvPr", NS)
    if marker is None:
        raise ValueError("PowerPoint object has no p:cNvPr marker")
    marker.set("name", value)


def arrow_end_value(value: Any) -> str | None:
    if value is True:
        return "triangle"
    if value is False or value is None:
        return None
    token = normalized(value)
    if token in {"", "none", "false", "0"}:
        return None
    if token not in ARROW_TYPES:
        raise ValueError(f"unsupported arrowhead type: {value!r}")
    return ARROW_TYPES[token]


def set_arrow_end(line: ET.Element, tag: str, value: Any, item: dict[str, Any]) -> str | None:
    existing = line.find(f"a:{tag}", NS)
    if existing is not None:
        line.remove(existing)
    arrow_type = arrow_end_value(value)
    if arrow_type is None:
        return None
    node = ET.Element(qname("a", tag), {"type": arrow_type})
    width = str(item.get("arrow_width") or "med").lower()
    length = str(item.get("arrow_length") or "med").lower()
    if width not in ARROW_SIZES or length not in ARROW_SIZES:
        raise ValueError("arrow_width and arrow_length must be sm, med, or lg")
    node.set("w", width)
    node.set("len", length)
    line.append(node)
    return arrow_type


def convert_connector(obj: ET.Element, item: dict[str, Any]) -> dict[str, Any]:
    if obj.tag not in {qname("p", "sp"), qname("p", "cxnSp")}:
        raise ValueError(f"expected a shape for connector, found {obj.tag}")
    obj.tag = qname("p", "cxnSp")
    nv = obj.find("p:nvSpPr", NS)
    if nv is None:
        nv = obj.find("p:nvCxnSpPr", NS)
    if nv is None:
        raise ValueError("connector object has no non-visual properties")
    nv.tag = qname("p", "nvCxnSpPr")
    connector_props = nv.find("p:cNvSpPr", NS)
    if connector_props is None:
        connector_props = nv.find("p:cNvCxnSpPr", NS)
    if connector_props is None:
        raise ValueError("connector object has no cNv connector properties")
    connector_props.tag = qname("p", "cNvCxnSpPr")
    text_body = obj.find("p:txBody", NS)
    if text_body is not None:
        obj.remove(text_body)

    sp_pr = obj.find("p:spPr", NS)
    if sp_pr is None:
        raise ValueError("connector object has no p:spPr")
    geometry = sp_pr.find("a:prstGeom", NS)
    if geometry is None:
        raise ValueError("connector object has no preset geometry")
    connector = str(item.get("connector") or "straight").lower()
    if connector not in CONNECTOR_PRESETS:
        raise ValueError(f"unsupported connector: {connector!r}")
    geometry.set("prst", CONNECTOR_PRESETS[connector])
    line = sp_pr.find("a:ln", NS)
    if line is None:
        line = ET.SubElement(sp_pr, qname("a", "ln"))
    start = set_arrow_end(line, "headEnd", item.get("start_arrow"), item)
    end = set_arrow_end(line, "tailEnd", item.get("end_arrow"), item)
    if start is None and end is None:
        raise ValueError("an Image2PPT connector arrow must have at least one arrowhead")
    return {
        "kind": "cxnSp",
        "connector": connector,
        "geometry": CONNECTOR_PRESETS[connector],
        "start_arrow": start,
        "end_arrow": end,
    }


def text_alignment(value: Any) -> str:
    return {"left": "l", "l": "l", "center": "ctr", "ctr": "ctr", "right": "r", "r": "r"}.get(
        str(value or "center").lower(), "ctr"
    )


def text_anchor(value: Any) -> str:
    return {"top": "t", "t": "t", "middle": "ctr", "center": "ctr", "ctr": "ctr", "bottom": "b", "b": "b"}.get(
        str(value or "middle").lower(), "ctr"
    )


def color_value(value: Any) -> str:
    token = str(value or "#111111").strip().lstrip("#")
    if not re.fullmatch(r"[0-9A-Fa-f]{6}", token):
        raise ValueError(f"invalid RGB color: {value!r}")
    return token.upper()


def add_run(paragraph: ET.Element, text: str, item: dict[str, Any]) -> None:
    run = ET.SubElement(paragraph, qname("a", "r"))
    size = int(round(float(item.get("font_size", 12)) * 100))
    attrs = {"lang": str(item.get("lang") or "zh-CN"), "sz": str(size)}
    if item.get("bold"):
        attrs["b"] = "1"
    if item.get("italic"):
        attrs["i"] = "1"
    props = ET.SubElement(run, qname("a", "rPr"), attrs)
    solid = ET.SubElement(props, qname("a", "solidFill"))
    ET.SubElement(solid, qname("a", "srgbClr"), {"val": color_value(item.get("text_color") or item.get("color"))})
    font = str(item.get("font") or item.get("font_face") or "Microsoft YaHei")
    ET.SubElement(props, qname("a", "latin"), {"typeface": font})
    ET.SubElement(props, qname("a", "ea"), {"typeface": font})
    ET.SubElement(props, qname("a", "cs"), {"typeface": font})
    ET.SubElement(run, qname("a", "t")).text = text


def install_shape_text(obj: ET.Element, item: dict[str, Any]) -> str:
    text = str(item.get("text") or "")
    old = obj.find("p:txBody", NS)
    if old is not None:
        obj.remove(old)
    body = ET.SubElement(obj, qname("p", "txBody"))
    margin = int(round(float(item.get("text_margin_pt", 3)) * 12700))
    wrap = str(item.get("wrap") or ("square" if item.get("word_wrap", True) else "none"))
    body_pr = ET.SubElement(
        body,
        qname("a", "bodyPr"),
        {
            "wrap": wrap,
            "anchor": text_anchor(item.get("valign")),
            "lIns": str(margin),
            "tIns": str(margin),
            "rIns": str(margin),
            "bIns": str(margin),
        },
    )
    ET.SubElement(body_pr, qname("a", "noAutofit"))
    ET.SubElement(body, qname("a", "lstStyle"))
    size = int(round(float(item.get("font_size", 12)) * 100))
    for line in text.splitlines() or [""]:
        paragraph = ET.SubElement(body, qname("a", "p"))
        ET.SubElement(paragraph, qname("a", "pPr"), {"algn": text_alignment(item.get("align"))})
        add_run(paragraph, line, item)
        ET.SubElement(paragraph, qname("a", "endParaRPr"), {"lang": str(item.get("lang") or "zh-CN"), "sz": str(size)})
    return text


def convert_filled_arrow(obj: ET.Element, item: dict[str, Any]) -> dict[str, Any]:
    if obj.tag != qname("p", "sp"):
        raise ValueError("filled arrow must remain one p:sp AutoShape")
    preset = str(item.get("preset") or "")
    if normalized(preset) not in ARROW_PRESETS:
        raise ValueError(f"unsupported filled arrow preset: {preset!r}")
    sp_pr = obj.find("p:spPr", NS)
    geometry = sp_pr.find("a:prstGeom", NS) if sp_pr is not None else None
    if geometry is None:
        raise ValueError("filled arrow has no preset geometry")
    geometry.set("prst", preset)
    text = install_shape_text(obj, item) if "text" in item else ""
    return {"kind": "sp", "preset": preset, "embedded_text": text}


def transform_slide(xml: bytes, manifest: dict[str, Any], slide_index: int) -> tuple[bytes, list[dict[str, Any]], list[str]]:
    profiled = arrow_items(manifest)
    if not profiled:
        return xml, [], []
    root = ET.fromstring(xml)
    sp_tree = root.find(".//p:spTree", NS)
    if sp_tree is None:
        return xml, [], [f"slide {slide_index}: missing p:spTree"]
    ids = shape_object_ids(manifest)
    operations: list[dict[str, Any]] = []
    errors: list[str] = []
    seen_names: set[str] = set()
    for shape_index, item, role in profiled:
        name = str(item.get("id") or "").strip()
        if not name:
            errors.append(f"slide {slide_index} shapes[{shape_index}]: profiled arrow requires a stable id")
            continue
        if name in seen_names:
            errors.append(f"slide {slide_index}: duplicate arrow id {name!r}")
            continue
        seen_names.add(name)
        object_id = ids.get(shape_index)
        obj = find_object(sp_tree, object_id) if object_id is not None else None
        if obj is None:
            errors.append(f"slide {slide_index} {name}: could not resolve local object id {object_id}")
            continue
        try:
            set_object_name(obj, name)
            details = convert_connector(obj, item) if role == "connector" else convert_filled_arrow(obj, item)
            operations.append(
                {
                    "slide_index": slide_index,
                    "shape_index": shape_index,
                    "object_id": object_id,
                    "name": name,
                    "role": role,
                    **details,
                }
            )
        except (TypeError, ValueError) as exc:
            errors.append(f"slide {slide_index} {name}: {exc}")
    if errors:
        return xml, operations, errors
    return ET.tostring(root, encoding="utf-8", xml_declaration=True), operations, []


def slide_sort_key(name: str) -> int:
    match = re.search(r"slide(\d+)\.xml$", name)
    return int(match.group(1)) if match else 10**9


def load_run_manifests(run_dir: Path) -> tuple[list[Path], Path]:
    run_dir = run_dir.expanduser().resolve()
    deck_path = resolve_inside(run_dir, "deck_manifest.json")
    deck = read_json(deck_path)
    manifests: list[Path] = []
    for page in deck.get("pages") or []:
        manifests.append(resolve_inside(run_dir, str(page.get("manifest") or "")))
    output = resolve_inside(run_dir, deck.get("output") or "final/deck_edited.pptx")
    return manifests, output


def postprocess_pptx(pptx: Path, manifest_paths: list[Path], report_path: Path | None = None) -> dict[str, Any]:
    pptx = pptx.expanduser().resolve()
    report_path = report_path.expanduser().resolve() if report_path else pptx.with_name("arrow_postprocess_report.json")
    report: dict[str, Any] = {
        "schema_version": "image2ppt-manifest-arrow-postprocess-v1",
        "passed": False,
        "pptx": str(pptx),
        "manifests": [str(path) for path in manifest_paths],
        "operations": [],
        "errors": [],
        "preservation": {},
    }
    temp_path: Path | None = None
    try:
        if not pptx.is_file() or pptx.suffix.lower() != ".pptx":
            raise FileNotFoundError(f"missing PPTX: {pptx}")
        manifests = [read_json(path) for path in manifest_paths]
        before_hash = sha256_file(pptx)
        with zipfile.ZipFile(pptx, "r") as source_zip:
            slide_names = sorted(
                [name for name in source_zip.namelist() if re.fullmatch(r"ppt/slides/slide\d+\.xml", name)],
                key=slide_sort_key,
            )
            if len(slide_names) != len(manifests):
                raise ValueError(f"PPTX has {len(slide_names)} slides but {len(manifests)} manifests were supplied")
            non_slide_hashes = {
                info.filename: sha256_bytes(source_zip.read(info.filename))
                for info in source_zip.infolist()
                if info.filename not in slide_names
            }
            handle = tempfile.NamedTemporaryFile(prefix=".image2ppt-arrows-", suffix=".pptx", dir=pptx.parent, delete=False)
            temp_path = Path(handle.name)
            handle.close()
            with zipfile.ZipFile(temp_path, "w") as target_zip:
                for info in source_zip.infolist():
                    data = source_zip.read(info.filename)
                    if info.filename in slide_names:
                        index = slide_names.index(info.filename)
                        data, operations, errors = transform_slide(data, manifests[index], index + 1)
                        report["operations"].extend(operations)
                        report["errors"].extend(errors)
                    target_zip.writestr(info, data)
        if report["errors"]:
            raise ValueError("one or more manifest arrow transformations failed")
        with zipfile.ZipFile(temp_path, "r") as check_zip:
            mismatches = [
                name
                for name, digest in non_slide_hashes.items()
                if name not in check_zip.namelist() or sha256_bytes(check_zip.read(name)) != digest
            ]
            bad_member = check_zip.testzip()
        if mismatches or bad_member:
            raise ValueError(f"package preservation failed; mismatches={mismatches}, bad_member={bad_member}")
        notes_parts = [name for name in non_slide_hashes if name.startswith("ppt/notes")]
        os.replace(temp_path, pptx)
        temp_path = None
        report["passed"] = True
        report["input_sha256"] = before_hash
        report["output_sha256"] = sha256_file(pptx)
        report["summary"] = {
            "slides": len(manifests),
            "profiled_arrows": len(report["operations"]),
            "connectors": sum(item["role"] == "connector" for item in report["operations"]),
            "filled_arrows": sum(item["role"] == "filled" for item in report["operations"]),
        }
        report["preservation"] = {
            "non_slide_parts_preserved": True,
            "non_slide_part_count": len(non_slide_hashes),
            "notes_parts_preserved": True,
            "notes_part_count": len(notes_parts),
        }
    except Exception as exc:
        if str(exc) not in report["errors"]:
            report["errors"].append(str(exc))
    finally:
        if temp_path is not None and temp_path.exists():
            temp_path.unlink()
        write_json(report_path, report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply Image2PPT arrow fields from standard manifest.json files")
    parser.add_argument("pptx", nargs="?", type=Path, help="Page or final PPTX; optional with --run")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--manifest", type=Path, help="One page manifest.json")
    source.add_argument("--run", type=Path, help="image2ppt run directory containing deck_manifest.json")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    if args.run:
        run_dir = args.run.expanduser().resolve()
        manifests, default_pptx = load_run_manifests(run_dir)
        pptx = resolve_inside(run_dir, args.pptx) if args.pptx else default_pptx
        report_path = resolve_inside(run_dir, args.report) if args.report else None
    else:
        manifest = args.manifest.expanduser().resolve()
        page_dir = manifest.parent
        manifests = [manifest]
        if args.pptx is None:
            raise SystemExit("a PPTX path is required with --manifest")
        pptx = resolve_inside(page_dir, args.pptx)
        report_path = resolve_inside(page_dir, args.report) if args.report else None
    report = postprocess_pptx(pptx, manifests, report_path)
    print(json.dumps(report, ensure_ascii=True, indent=2))
    return 0 if report["passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
