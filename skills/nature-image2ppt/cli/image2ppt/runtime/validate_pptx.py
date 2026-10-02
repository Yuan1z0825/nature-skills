#!/usr/bin/env python3
import argparse
import hashlib
import json
import posixpath
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

from build_pptx_from_manifest import TEXT_ALIGNMENTS, TEXT_VERTICAL_ALIGNMENTS, normalize_manifest
from deck_run_state import resolve_inside


NS = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "rel": "http://schemas.openxmlformats.org/package/2006/relationships",
}

ALLOWED_SOURCE_TYPES = {
    "asset-sheet-separated",
    "imagegen",
    "latex-rendered-formula",
    "user-provided",
    "user-approved-rasterization",
}
REQUIRED_QUALITY_CHECKS = {
    "font_size_calibrated",
    "visual_inventory_matched",
    "background_strategy_checked",
    "shape_corner_geometry_checked",
}
VISUAL_KINDS = {"background", "foreground-asset", "native-structure", "formula"}
VISUAL_REPRESENTATIONS = {
    "native",
    "asset-sheet-separated",
    "source-preserving-local-cleanup",
    "imagegen",
    "latex-rendered-formula",
}
REPRESENTATIONS_BY_KIND = {
    "background": {"native", "source-preserving-local-cleanup", "imagegen"},
    "foreground-asset": {"asset-sheet-separated"},
    "native-structure": {"native"},
    "formula": {"latex-rendered-formula"},
}
FOREGROUND_TERMS = {
    "badge",
    "decorative",
    "foreground",
    "hand-drawn",
    "icon",
    "illustration",
    "image block",
    "logo",
    "mark",
    "photo",
    "pictogram",
    "screenshot",
    "semantic",
    "sticker",
    "symbol",
    "trend",
    "visual object",
    "前景",
    "图标",
    "照片",
    "截图",
    "徽章",
    "贴纸",
    "语义",
    "视觉对象",
}
NON_FOREGROUND_TERMS = {
    "background",
    "clean base",
    "formula",
    "latex",
    "native structural",
    "structural shape",
    "背景",
    "公式",
    "结构",
}
ASSET_SHEET_TERMS = {
    "asset-sheet",
    "asset sheet",
    "asset_sheet",
    "image edit",
    "imagegen",
    "separated",
    "source-faithful",
    "source faithful",
    "split",
    "分离",
}
FORBIDDEN_FOREGROUND_FALLBACK_TERMS = {
    "approximate",
    "approximation",
    "approximated",
    "crop",
    "cropped",
    "direct crop",
    "direct source",
    "emoji",
    "fallback",
    "native approximation",
    "source crop",
    "source snippet",
    "text symbol",
    "warning only",
    "warning_only",
    "近似",
    "裁切",
    "裁剪",
    "降级",
}


def read_manifest(path):
    if not path:
        return {}
    return json.loads(Path(path).read_text(encoding="utf-8"))


def compact_text(value):
    if value is None:
        return ""
    if isinstance(value, str):
        return value.lower()
    if isinstance(value, (int, float, bool)):
        return str(value).lower()
    if isinstance(value, dict):
        return " ".join(compact_text(item) for item in value.values())
    if isinstance(value, (list, tuple, set)):
        return " ".join(compact_text(item) for item in value)
    return str(value).lower()


def contains_any(text, terms):
    return any(term in text for term in terms)


def manifest_schema_version(manifest):
    try:
        return int(manifest.get("schema_version", 1))
    except (TypeError, ValueError):
        return 1


def visual_item_path(item):
    for key in ("path", "asset", "asset_path", "image", "image_path", "corresponding_asset"):
        value = item.get(key) if isinstance(item, dict) else None
        if isinstance(value, str) and value.strip():
            return Path(value).as_posix()
    return None


def is_foreground_visual_item(item):
    text = compact_text(item)
    if contains_any(text, NON_FOREGROUND_TERMS):
        return False
    return contains_any(text, FOREGROUND_TERMS)


def foreground_asset_contract_violations(manifest):
    violations = []
    provenance_by_path = {
        Path(entry.get("path", "")).as_posix(): entry
        for entry in manifest.get("asset_provenance", [])
        if entry.get("path")
    }

    structured_paths = set()
    for index, item in enumerate(manifest.get("visual_inventory", [])):
        if not isinstance(item, dict):
            continue
        text = compact_text(item)
        field = f"visual_inventory[{index}]"
        kind = item.get("kind")
        representation = item.get("representation")
        structured = kind is not None or representation is not None or manifest_schema_version(manifest) >= 2
        if structured:
            if kind not in VISUAL_KINDS:
                violations.append(
                    {"field": f"{field}.kind", "reason": f"kind must be one of {sorted(VISUAL_KINDS)}"}
                )
            if representation not in VISUAL_REPRESENTATIONS:
                violations.append(
                    {
                        "field": f"{field}.representation",
                        "reason": f"representation must be one of {sorted(VISUAL_REPRESENTATIONS)}",
                    }
                )
            if kind in REPRESENTATIONS_BY_KIND and representation not in REPRESENTATIONS_BY_KIND[kind]:
                violations.append(
                    {
                        "field": f"{field}.representation",
                        "reason": f"{kind} requires one of {sorted(REPRESENTATIONS_BY_KIND[kind])}",
                    }
                )
            path = visual_item_path(item)
            if path:
                structured_paths.add(path)
            if kind == "foreground-asset":
                if not path:
                    violations.append(
                        {"field": field, "reason": "foreground-asset requires a path to its separated asset"}
                    )
                else:
                    provenance = provenance_by_path.get(path, {})
                    if provenance.get("source_type") != "asset-sheet-separated":
                        violations.append(
                            {
                                "field": field,
                                "path": path,
                                "reason": "foreground-asset provenance must use source_type asset-sheet-separated",
                            }
                        )
            continue
        if contains_any(text, FORBIDDEN_FOREGROUND_FALLBACK_TERMS):
            violations.append(
                {
                    "field": field,
                    "reason": "foreground visual decisions must not use direct crops, native approximations, emoji/text symbols, warning-only fallbacks, or similar shortcuts",
                }
            )
        if not is_foreground_visual_item(item):
            continue
        if not contains_any(text, ASSET_SHEET_TERMS):
            violations.append(
                {
                    "field": field,
                    "reason": "foreground visual objects must explicitly use source-faithful asset-sheet separation",
                }
            )
        path = visual_item_path(item)
        if path:
            provenance = provenance_by_path.get(path, {})
            source_type = provenance.get("source_type")
            if source_type in {"user-provided", "user-approved-rasterization"}:
                violations.append(
                    {
                        "field": field,
                        "path": path,
                        "reason": "foreground visual objects cannot use user-provided/direct raster provenance; use asset-sheet separation",
                    }
                )

    for index, entry in enumerate(manifest.get("asset_provenance", [])):
        if not isinstance(entry, dict):
            continue
        text = compact_text(entry)
        source_type = entry.get("source_type")
        path = Path(entry.get("path", "")).as_posix()
        field = f"asset_provenance[{index}]"
        if path in structured_paths:
            continue
        if source_type in {"user-provided", "user-approved-rasterization"} and contains_any(
            text, FOREGROUND_TERMS | FORBIDDEN_FOREGROUND_FALLBACK_TERMS
        ):
            violations.append(
                {
                    "field": field,
                    "path": path,
                    "reason": "foreground-like raster provenance cannot be direct user-provided/cropped source material",
                }
            )
        if contains_any(text, FORBIDDEN_FOREGROUND_FALLBACK_TERMS):
            violations.append(
                {
                    "field": field,
                    "path": path,
                    "reason": "asset provenance records a forbidden foreground fallback such as crop, approximation, or warning-only delivery",
                }
            )

    return violations


def is_full_slide_image(item, slide):
    width = float(slide.get("width", 13.333))
    height = float(slide.get("height", 7.5))
    left = float(item.get("left", 0))
    top = float(item.get("top", 0))
    image_width = float(item.get("width", 0))
    image_height = float(item.get("height", 0))
    return (
        abs(left) <= 0.02
        and abs(top) <= 0.02
        and image_width >= width * 0.98
        and image_height >= height * 0.98
    )


def page_contract_violations(manifest):
    violations = []
    slide = manifest.get("slide", {})
    images = manifest.get("images", [])
    text_boxes = manifest.get("text_boxes", [])
    provenance_by_path = {
        Path(entry.get("path", "")).as_posix(): entry
        for entry in manifest.get("asset_provenance", [])
        if entry.get("path")
    }
    for image in images:
        path = Path(image.get("path", "")).as_posix()
        provenance = provenance_by_path.get(path, {})
        source_type = provenance.get("source_type")
        if is_full_slide_image(image, slide) and Path(path).name == "source.png" and text_boxes:
            violations.append(
                {
                    "field": "images",
                    "path": path,
                    "reason": "full-slide source.png background with editable text overlays causes baked-text overlap",
                }
            )
        if (
            is_full_slide_image(image, slide)
            and source_type in {"user-provided", "user-approved-rasterization"}
            and text_boxes
        ):
            violations.append(
                {
                    "field": "asset_provenance",
                    "path": path,
                    "reason": "full-slide raster background cannot be assembled with editable text",
                }
            )

    return violations


def quality_contract_violations(manifest):
    violations = []

    if "visual_inventory" not in manifest:
        violations.append(
            {
                "field": "visual_inventory",
                "reason": "page manifest must record the non-text visual inventory, even when it is empty",
            }
        )
    elif not isinstance(manifest.get("visual_inventory"), list):
        violations.append({"field": "visual_inventory", "reason": "visual_inventory must be a list"})

    background_strategy = manifest.get("background_strategy")
    if not background_strategy:
        violations.append(
            {
                "field": "background_strategy",
                "reason": "page manifest must record how the background was rebuilt or preserved",
            }
        )

    quality_checks = manifest.get("quality_checks")
    if not isinstance(quality_checks, dict):
        violations.append({"field": "quality_checks", "reason": "quality_checks must be an object"})
    else:
        for key in sorted(REQUIRED_QUALITY_CHECKS):
            if quality_checks.get(key) is not True:
                violations.append(
                    {
                        "field": f"quality_checks.{key}",
                        "reason": "required page QA check must be explicitly true",
                    }
                )

    if manifest_schema_version(manifest) >= 2:
        quality_evidence = manifest.get("quality_evidence")
        if not isinstance(quality_evidence, dict):
            violations.append(
                {"field": "quality_evidence", "reason": "schema v2 requires structured quality evidence"}
            )
        else:
            for key in sorted(REQUIRED_QUALITY_CHECKS):
                evidence = quality_evidence.get(key)
                observation = evidence.get("observation") if isinstance(evidence, dict) else None
                if not isinstance(observation, str) or len(re.sub(r"\s+", "", observation)) < 12:
                    violations.append(
                        {
                            "field": f"quality_evidence.{key}.observation",
                            "reason": "quality evidence requires a specific observation of at least 12 characters",
                        }
                    )

    for index, shape in enumerate(manifest.get("shapes", [])):
        is_round_rect = shape.get("type") == "roundRect" or shape.get("preset") == "roundRect"
        if is_round_rect and not shape.get("source_corner_radius_px"):
            violations.append(
                {
                    "field": f"shapes[{index}]",
                    "reason": "roundRect requires source_corner_radius_px; use rect for source straight-corner containers",
                }
            )
        if is_round_rect and shape.get("source_corner_radius_px") and shape.get("box_px"):
            box = shape.get("box_px")
            radius = float(shape.get("source_corner_radius_px") or 0)
            min_dim = max(1.0, min(float(box[2]), float(box[3])))
            if radius > min_dim / 2:
                violations.append(
                    {
                        "field": f"shapes[{index}].source_corner_radius_px",
                        "reason": "roundRect source radius cannot exceed half of the smaller shape dimension",
                    }
                )

    for index, text_box in enumerate(manifest.get("text_boxes", [])):
        align = str(text_box.get("align", "left") or "left").strip().lower()
        if align not in TEXT_ALIGNMENTS:
            violations.append(
                {
                    "field": f"text_boxes[{index}].align",
                    "reason": "text align must be left, center, right, or the equivalent DrawingML token l, ctr, r",
                }
            )
        valign = str(text_box.get("valign", "top") or "top").strip().lower()
        if valign not in TEXT_VERTICAL_ALIGNMENTS:
            violations.append(
                {
                    "field": f"text_boxes[{index}].valign",
                    "reason": "text valign must be top, middle, bottom, or the equivalent DrawingML token t, ctr, b",
                }
            )

    violations.extend(foreground_asset_contract_violations(manifest))
    violations.extend(formula_contract_violations(manifest))
    return violations


def formula_contract_violations(manifest):
    violations = []
    formula_inventory = manifest.get("formula_inventory", [])
    inventory_ids = {
        str(item.get("id"))
        for item in formula_inventory
        if isinstance(item, dict) and item.get("id")
    }
    inventory_paths = {
        Path(item.get("image", "")).as_posix()
        for item in formula_inventory
        if isinstance(item, dict) and item.get("image")
    }
    for index, visual in enumerate(manifest.get("visual_inventory", [])):
        if not isinstance(visual, dict) or visual.get("kind") != "formula":
            continue
        visual_id = str(visual.get("id") or "")
        visual_path = visual_item_path(visual)
        if visual_id not in inventory_ids and visual_path not in inventory_paths:
            violations.append(
                {
                    "field": f"visual_inventory[{index}]",
                    "reason": "formula visual requires a matching formula_inventory entry",
                }
            )
    images = {
        Path(item.get("path", "")).as_posix(): item
        for item in manifest.get("images", [])
        if isinstance(item, dict) and item.get("path")
    }
    provenance = {
        Path(item.get("path", "")).as_posix(): item
        for item in manifest.get("asset_provenance", [])
        if isinstance(item, dict) and item.get("path")
    }
    for index, formula in enumerate(formula_inventory):
        field = f"formula_inventory[{index}]"
        if not isinstance(formula, dict):
            violations.append({"field": field, "reason": "formula inventory item must be an object"})
            continue
        status = str(formula.get("status") or "rendered").strip().lower()
        if status in {"failed", "missing", "blocked"}:
            if formula.get("user_approved_exception") is not True:
                violations.append(
                    {
                        "field": field,
                        "reason": "an unrendered formula is a hard failure unless user_approved_exception is true",
                    }
                )
            note = formula.get("approval_note")
            if formula.get("user_approved_exception") is True and (
                not isinstance(note, str) or len(note.strip()) < 12
            ):
                violations.append(
                    {"field": f"{field}.approval_note", "reason": "approved formula exception requires a concrete note"}
                )
            continue
        image_path = formula.get("image")
        if not image_path:
            violations.append({"field": f"{field}.image", "reason": "rendered formula requires an image path"})
            continue
        key = Path(image_path).as_posix()
        if key not in images:
            violations.append({"field": f"{field}.image", "reason": "formula image is missing from images[]"})
        if provenance.get(key, {}).get("source_type") != "latex-rendered-formula":
            violations.append(
                {"field": f"{field}.image", "reason": "formula image requires latex-rendered-formula provenance"}
            )
    return violations


def pixel_authoring_violations(manifest):
    violations = []
    source = manifest.get("source", {})
    if not source.get("width_px") or not source.get("height_px"):
        violations.append(
            {
                "field": "source.width_px/source.height_px",
                "reason": "page manifest must record the source image pixel size",
            }
        )

    for section in ("text_boxes", "images"):
        for index, item in enumerate(manifest.get(section, [])):
            if "box_px" not in item:
                violations.append(
                    {
                        "field": f"{section}[{index}].box_px",
                        "reason": "positioned text and image objects must use source-image pixel coordinates",
                    }
                )

    for index, item in enumerate(manifest.get("shapes", [])):
        if item.get("type") == "line":
            if "points_px" not in item:
                violations.append(
                    {
                        "field": f"shapes[{index}].points_px",
                        "reason": "line shapes must use source-image pixel endpoints",
                    }
                )
        elif item.get("type") == "bezier":
            if "box_px" not in item:
                violations.append(
                    {
                        "field": f"shapes[{index}].box_px",
                        "reason": "Bezier shapes must use a source-image pixel bounding box",
                    }
                )
            segments = item.get("bezier_px")
            if not isinstance(segments, list) or not segments or any(not isinstance(segment, list) or len(segment) != 8 for segment in segments):
                violations.append(
                    {
                        "field": f"shapes[{index}].bezier_px",
                        "reason": "Bezier shapes require cubic segments [x1,y1,c1x,c1y,c2x,c2y,x2,y2]",
                    }
                )
        elif "box_px" not in item:
            violations.append(
                {
                    "field": f"shapes[{index}].box_px",
                    "reason": "positioned shapes must use source-image pixel coordinates",
                }
            )

    return violations


def normalize_for_validation(manifest):
    violations = pixel_authoring_violations(manifest)
    try:
        return normalize_manifest(manifest), violations
    except Exception as exc:
        violations.append({"field": "manifest", "reason": str(exc)})
        return manifest, violations


def sha256_text(value):
    return hashlib.sha256(str(value).encode("utf-8")).hexdigest()


def flatten_required_text(value):
    """Return exact text strings that should be verified in the PPTX."""
    items = []
    if value is None:
        return items
    if isinstance(value, str):
        text = value.strip()
        return [text] if text else []
    if isinstance(value, (int, float)):
        return [str(value)]
    if isinstance(value, dict):
        if "required_text" in value:
            return flatten_required_text(value.get("required_text"))
        if "items" in value:
            return flatten_required_text(value.get("items"))
        if "texts" in value:
            return flatten_required_text(value.get("texts"))
        if "text" in value:
            return flatten_required_text(value.get("text"))
        return items
    if isinstance(value, (list, tuple, set)):
        for item in value:
            items.extend(flatten_required_text(item))
    return items


def required_texts_from_manifest(manifest):
    required = []
    required.extend(flatten_required_text(manifest.get("required_text", [])))
    required.extend(flatten_required_text(manifest.get("text_inventory", [])))
    return required


def collect_text(xml_bytes):
    root = ET.fromstring(xml_bytes)
    paragraphs = []
    for paragraph in root.findall(".//a:p", NS):
        text = "".join(node.text or "" for node in paragraph.findall(".//a:t", NS)).strip()
        if text:
            paragraphs.append(text)
    # Keep readable word boundaries across explicit line/paragraph breaks. This
    # lets required-text checks validate visual multi-line labels such as
    # "Format\nReward" without forcing them into an overflowing single line.
    return " ".join(paragraphs)


def collect_paragraph_text(xml_bytes):
    root = ET.fromstring(xml_bytes)
    paragraphs = []
    for paragraph in root.findall(".//a:p", NS):
        text = "".join(node.text or "" for node in paragraph.findall(".//a:t", NS))
        if text:
            paragraphs.append(text)
    return "\n".join(paragraphs)


def collect_notes_texts(z, names):
    notes = {}
    for name in sorted(n for n in names if re.match(r"ppt/notesSlides/notesSlide\d+\.xml$", n)):
        match = re.search(r"notesSlide(\d+)\.xml$", name)
        if not match:
            continue
        notes[int(match.group(1))] = collect_paragraph_text(z.read(name))
    return notes


def validate_deck(args):
    deck_path = Path(args.deck_manifest).resolve()
    deck = read_manifest(deck_path)
    root = deck_path.parent
    expected_pages = int(deck.get("page_count", len(deck.get("pages", []))))
    notes_manifest = {}
    deck_path_violations = []
    notes_path = deck.get("notes_manifest")
    if notes_path:
        try:
            notes_file = resolve_inside(root, notes_path)
            if notes_file.exists():
                notes_manifest = read_manifest(notes_file)
        except ValueError as exc:
            deck_path_violations.append({"field": "notes_manifest", "reason": str(exc)})

    report = {
        "pptx": str(Path(args.pptx).resolve()),
        "deck_manifest": str(deck_path),
        "expected_pages": expected_pages,
        "slides": 0,
        "page_manifests_missing": [],
        "page_validation_missing": [],
        "failed_page_validations": [],
        "page_contract_violations": (
            [{"page_id": None, "manifest": str(deck_path), "violations": deck_path_violations}]
            if deck_path_violations
            else []
        ),
        "notes_expected": len(notes_manifest.get("notes", [])),
        "notes_found": 0,
        "notes_hash_mismatches": [],
        "missing_parts": [],
        "warnings": [],
        "passed": False,
    }

    for page in deck.get("pages", []):
        try:
            manifest_path = resolve_inside(root, page.get("manifest", ""))
            validation_path = resolve_inside(root, page.get("validation", ""))
        except ValueError as exc:
            report["page_contract_violations"].append(
                {
                    "page_id": page.get("page_id"),
                    "manifest": str(page.get("manifest", "")),
                    "violations": [{"field": "page path", "reason": str(exc)}],
                }
            )
            continue
        if not manifest_path.exists():
            report["page_manifests_missing"].append(str(manifest_path))
        else:
            try:
                raw_manifest = read_manifest(manifest_path)
                normalized_manifest, authoring_violations = normalize_for_validation(raw_manifest)
                violations = (
                    authoring_violations
                    + page_contract_violations(normalized_manifest)
                    + quality_contract_violations(raw_manifest)
                )
                if violations:
                    report["page_contract_violations"].append(
                        {
                            "page_id": page.get("page_id"),
                            "manifest": str(manifest_path),
                            "violations": violations,
                        }
                    )
            except Exception as exc:
                report["page_contract_violations"].append(
                    {
                        "page_id": page.get("page_id"),
                        "manifest": str(manifest_path),
                        "violations": [{"field": "manifest", "reason": str(exc)}],
                    }
                )
        if not validation_path.exists():
            report["page_validation_missing"].append(str(validation_path))
        else:
            try:
                page_report = read_manifest(validation_path)
                if page_report.get("passed") is False:
                    report["failed_page_validations"].append(str(validation_path))
            except Exception as exc:
                report["failed_page_validations"].append(f"{validation_path}: {exc}")

    try:
        with zipfile.ZipFile(args.pptx) as z:
            names = z.namelist()
            report["slides"] = len([n for n in names if re.match(r"ppt/slides/slide\d+\.xml$", n)])
            for part in ("[Content_Types].xml", "_rels/.rels", "ppt/presentation.xml", "ppt/_rels/presentation.xml.rels"):
                if part not in names:
                    report["missing_parts"].append(part)
            notes_texts = collect_notes_texts(z, names)
            report["notes_found"] = len(notes_texts)
            for entry in notes_manifest.get("notes", []):
                page_index = int(entry.get("page_index", 0))
                expected_hash = entry.get("text_sha256", sha256_text(entry.get("text", "")))
                actual = notes_texts.get(page_index)
                if actual is None:
                    report["notes_hash_mismatches"].append({"page_index": page_index, "reason": "missing notes slide"})
                elif sha256_text(actual) != expected_hash:
                    report["notes_hash_mismatches"].append({"page_index": page_index, "reason": "text hash mismatch"})
    except Exception as exc:
        report["warnings"].append(f"Unable to read pptx: {exc}")

    report["passed"] = (
        report["slides"] == expected_pages
        and not report["page_manifests_missing"]
        and not report["page_validation_missing"]
        and not report["failed_page_validations"]
        and not report["page_contract_violations"]
        and not report["missing_parts"]
        and not report["notes_hash_mismatches"]
    )
    output = json.dumps(report, ensure_ascii=False, indent=2)
    if args.report:
        Path(args.report).parent.mkdir(parents=True, exist_ok=True)
        Path(args.report).write_text(output + "\n", encoding="utf-8")
    print(output)
    raise SystemExit(0 if report["passed"] else 1)


def rel_source_part(rels_name):
    if not rels_name.endswith(".rels"):
        return posixpath.dirname(rels_name)
    directory = posixpath.dirname(rels_name)
    if directory.endswith("/_rels"):
        directory = posixpath.dirname(directory)
    source = posixpath.basename(rels_name)[:-5]
    return posixpath.normpath(posixpath.join(directory, source))


def resolve_target(rels_name, target):
    if not target or re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target):
        return None
    source = rel_source_part(rels_name)
    return posixpath.normpath(posixpath.join(posixpath.dirname(source), target))


def relationship_targets(z, rels_name, names):
    if rels_name not in names:
        return []
    root = ET.fromstring(z.read(rels_name))
    targets = []
    for rel in root.findall("rel:Relationship", NS):
        mode = rel.attrib.get("TargetMode")
        target = rel.attrib.get("Target")
        resolved = resolve_target(rels_name, target)
        targets.append(
            {
                "id": rel.attrib.get("Id"),
                "type": rel.attrib.get("Type", ""),
                "target": target,
                "resolved": resolved,
                "external": mode == "External",
            }
        )
    return targets


def file_sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("pptx")
    parser.add_argument("--manifest")
    parser.add_argument("--deck-manifest")
    parser.add_argument("--required-text", action="append", default=[])
    parser.add_argument("--report")
    args = parser.parse_args()

    if args.deck_manifest:
        deck_root = Path(args.deck_manifest).expanduser().resolve().parent
        args.pptx = str(resolve_inside(deck_root, args.pptx))
        if args.report:
            args.report = str(resolve_inside(deck_root, args.report))
        validate_deck(args)

    if not args.manifest:
        parser.error("--manifest is required unless --deck-manifest is used")
    manifest_base = Path(args.manifest).expanduser().resolve().parent
    args.pptx = str(resolve_inside(manifest_base, args.pptx))
    if args.report:
        args.report = str(resolve_inside(manifest_base, args.report))

    raw_manifest = read_manifest(args.manifest)
    manifest, authoring_violations = normalize_for_validation(raw_manifest)
    required = list(args.required_text)
    required.extend(required_texts_from_manifest(manifest))

    report = {
        "pptx": str(Path(args.pptx).resolve()),
        "zip_ok": False,
        "slides": 0,
        "images": 0,
        "editable_text_shapes": 0,
        "shape_count": 0,
        "all_text": "",
        "required_text": required,
        "missing_required_text": [],
        "missing_parts": [],
        "missing_relationship_targets": [],
        "missing_asset_provenance": [],
        "missing_manifest_images": [],
        "missing_provenance_sources": [],
        "invalid_asset_provenance": [],
        "media_hash_mismatches": [],
        "asset_provenance_checked": 0,
        "manifest_image_count": len(manifest.get("images", [])),
        "media_manifest_mismatch": False,
        "relationship_targets_checked": 0,
        "warnings": [],
        "page_contract_violations": [],
    }

    try:
        with zipfile.ZipFile(args.pptx) as z:
            bad = z.testzip()
            report["zip_ok"] = bad is None
            if bad:
                report["warnings"].append(f"Bad zip member: {bad}")
            names = z.namelist()
            required_parts = [
                "[Content_Types].xml",
                "_rels/.rels",
                "ppt/presentation.xml",
                "ppt/_rels/presentation.xml.rels",
            ]
            for part in required_parts:
                if part not in names:
                    report["missing_parts"].append(part)
            slide_names = sorted(n for n in names if re.match(r"ppt/slides/slide\d+\.xml$", n))
            report["slides"] = len(slide_names)
            report["images"] = len([n for n in names if n.startswith("ppt/media/")])
            report["media_manifest_mismatch"] = report["images"] != report["manifest_image_count"]
            for index, image in enumerate(manifest.get("images", []), start=1):
                image_path = image.get("path")
                if not image_path:
                    continue
                ext = Path(image_path).suffix.lower()
                if ext == ".jpeg":
                    ext = ".jpg"
                media_name = f"ppt/media/image{index}{ext}"
                source_path = Path(image_path)
                try:
                    source_path = resolve_inside(manifest_base, source_path)
                except ValueError:
                    report["missing_manifest_images"].append(str(image_path))
                    continue
                if media_name not in names:
                    report["media_hash_mismatches"].append(
                        {"path": image_path, "media": media_name, "reason": "missing media part"}
                    )
                    continue
                if source_path.exists():
                    manifest_hash = file_sha256(source_path)
                    media_hash = hashlib.sha256(z.read(media_name)).hexdigest()
                    if manifest_hash != media_hash:
                        report["media_hash_mismatches"].append(
                            {"path": image_path, "media": media_name, "reason": "hash mismatch"}
                        )
                else:
                    report["missing_manifest_images"].append(str(image_path))
            for slide_name in slide_names:
                rels_name = f"{posixpath.dirname(slide_name)}/_rels/{posixpath.basename(slide_name)}.rels"
                if rels_name not in names:
                    report["missing_parts"].append(rels_name)
            rel_files = [name for name in names if name.endswith(".rels")]
            for rels_name in rel_files:
                for target in relationship_targets(z, rels_name, names):
                    if target["external"] or not target["resolved"]:
                        continue
                    report["relationship_targets_checked"] += 1
                    if target["resolved"] not in names:
                        report["missing_relationship_targets"].append(
                            {
                                "rels": rels_name,
                                "id": target["id"],
                                "target": target["target"],
                                "resolved": target["resolved"],
                            }
                        )
            texts = []
            for slide_name in slide_names:
                xml = z.read(slide_name)
                root = ET.fromstring(xml)
                shapes = root.findall(".//p:sp", NS)
                report["shape_count"] += len(shapes)
                report["editable_text_shapes"] += sum(1 for shape in shapes if shape.findall(".//a:t", NS))
                texts.append(collect_text(xml))
            report["all_text"] = "\n".join(texts)
    except Exception as exc:
        report["warnings"].append(f"Unable to read pptx: {exc}")

    # Required-text validation is about semantic content, not visual line
    # wrapping. PowerPoint stores explicit line breaks as paragraph boundaries,
    # and vertical CJK labels may place one character per paragraph. Compare a
    # whitespace-free form as well so editable multi-line layout does not create
    # false missing-text failures.
    all_text_compact = re.sub(r"\s+", "", report["all_text"])
    for text in required:
        text_compact = re.sub(r"\s+", "", str(text))
        if text and text not in report["all_text"] and text_compact not in all_text_compact:
            report["missing_required_text"].append(text)

    provenance = {}
    for entry in manifest.get("asset_provenance", []):
        path = entry.get("path")
        if path:
            provenance[Path(path).as_posix()] = entry

    for image in manifest.get("images", []):
        image_path = image.get("path")
        if not image_path:
            continue
        key = Path(image_path).as_posix()
        entry = provenance.get(key)
        if not entry:
            report["missing_asset_provenance"].append(key)
            continue
        report["asset_provenance_checked"] += 1
        source_type = entry.get("source_type")
        provenance_note = entry.get("provenance_note")
        if source_type not in ALLOWED_SOURCE_TYPES:
            report["invalid_asset_provenance"].append(
                {"path": key, "field": "source_type", "value": source_type}
            )
        if not provenance_note:
            report["invalid_asset_provenance"].append(
                {"path": key, "field": "provenance_note", "value": provenance_note}
            )
        if source_type == "user-approved-rasterization" and not entry.get("approval_note"):
            report["invalid_asset_provenance"].append(
                {"path": key, "field": "approval_note", "value": entry.get("approval_note")}
            )
        source = entry.get("source")
        if not source:
            report["missing_provenance_sources"].append({"path": key, "source": source})
            continue
        try:
            source_path = resolve_inside(manifest_base, source)
        except ValueError:
            report["missing_provenance_sources"].append(
                {"path": key, "source": str(source), "reason": "source is outside manifest directory"}
            )
            continue
        if not source_path.exists():
            report["missing_provenance_sources"].append({"path": key, "source": str(source)})
    report["page_contract_violations"] = (
        authoring_violations + page_contract_violations(manifest) + quality_contract_violations(raw_manifest)
    )

    report["passed"] = (
        report["zip_ok"]
        and report["slides"] >= 1
        and not report["media_manifest_mismatch"]
        and not report["missing_parts"]
        and not report["missing_relationship_targets"]
        and not report["media_hash_mismatches"]
        and not report["missing_required_text"]
        and not report["missing_asset_provenance"]
        and not report["missing_manifest_images"]
        and not report["missing_provenance_sources"]
        and not report["invalid_asset_provenance"]
        and not report["page_contract_violations"]
        and (report["editable_text_shapes"] > 0 or not required)
    )

    output = json.dumps(report, ensure_ascii=False, indent=2)
    if args.report:
        Path(args.report).parent.mkdir(parents=True, exist_ok=True)
        Path(args.report).write_text(output + "\n", encoding="utf-8")
    print(output)
    raise SystemExit(0 if report["passed"] else 1)


if __name__ == "__main__":
    main()
