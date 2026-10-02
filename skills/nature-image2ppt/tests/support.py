from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

from PIL import Image


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = SKILL_ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from runtime_paths import image2ppt_command, image2ppt_runtime_script


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def complete_visual_review_evidence(template: Path, evidence: Path) -> None:
    payload = json.loads(template.read_text(encoding="utf-8"))
    for page in payload.get("pages", []):
        page["reviewed"] = True
        page_id = page.get("page_id", "page")
        for check in page.get("checks", {}):
            page["checks"][check] = (
                f"Verified {check} for {page_id} against the current source and rendered slide."
            )
    write_json(evidence, payload)


def base_manifest(page_dir: Path, shape: dict, *, text_inventory: list[str] | None = None) -> Path:
    page_dir.mkdir(parents=True, exist_ok=True)
    source = page_dir / "source.png"
    Image.new("RGB", (1280, 720), "white").save(source)
    if shape.get("points_px"):
        anchor = {
            "id": f"anchor-{shape['id']}",
            "kind": "directed-connector" if shape.get("end_arrow") not in {None, "none"} else "connector",
            "manifest_id": shape["id"],
            "source_points_px": shape["points_px"],
        }
    else:
        anchor = {
            "id": f"anchor-{shape['id']}",
            "kind": "route-line" if shape.get("preset") else "node-boundary",
            "manifest_id": shape["id"],
            "source_bbox_px": shape["box_px"],
        }
    manifest = {
        "schema_version": 2,
        "slide": {"width": 13.333, "height": 7.5, "background": "#FFFFFF"},
        "content_box": {"left": 0, "top": 0, "width": 13.333, "height": 7.5},
        "source": {"path": "source.png", "width_px": 1280, "height_px": 720},
        "page_strategy": "native-structure",
        "text_inventory": text_inventory or [],
        "visual_inventory": [
            {
                "id": shape["id"],
                "kind": "native-structure",
                "representation": "native",
                "description": "Measured native structural fixture object.",
            }
        ],
        "background_strategy": {
            "mode": "native-or-script",
            "reason": "solid white fixture background",
            "comparison_note": "fixture background matched",
        },
        "quality_checks": {
            "font_size_calibrated": True,
            "visual_inventory_matched": True,
            "background_strategy_checked": True,
            "shape_corner_geometry_checked": True,
        },
        "quality_evidence": {
            "font_size_calibrated": {"observation": "Fixture text sizing was checked against the source geometry."},
            "visual_inventory_matched": {"observation": "Fixture object inventory matches the single source object."},
            "background_strategy_checked": {"observation": "Solid white fixture background was compared with the source."},
            "shape_corner_geometry_checked": {"observation": "Fixture object corner and boundary geometry were reviewed."},
        },
        "text_boxes": [],
        "shapes": [shape],
        "images": [],
        "asset_provenance": [],
        "image2ppt_region_decomposition": {
            "schema_version": "image2ppt-region-decomposition-v1",
            "page_complexity": "simple",
            "source_size_px": [1280, 720],
            "regions": [
                {
                    "id": "fixture-region",
                    "label": "Fixture region",
                    "source_bbox_px": [0, 0, 1280, 720],
                    "risk_level": "low",
                    "strategy": "native-object-decomposition",
                    "reason": "Single measured native fixture object.",
                    "manifest_ids": {"shapes": [shape["id"]], "text_boxes": [], "images": []},
                    "protected_visual_anchors": [anchor],
                }
            ],
        },
    }
    path = page_dir / "manifest.json"
    write_json(path, manifest)
    write_json(page_dir / "imagegen-jobs.json", {"schema_version": 1, "jobs": []})
    return path


def connector_manifest(page_dir: Path, connector: str = "straight") -> Path:
    return base_manifest(
        page_dir,
        {
            "id": f"arrow-{connector}",
            "type": "line",
            "points_px": [350, 360, 900, 360],
            "stroke": "#2563EB",
            "stroke_width": 2.5,
            "connector": connector,
            "start_arrow": "none",
            "end_arrow": "triangle",
            "arrow_width": "med",
            "arrow_length": "lg",
            "z_index": 140,
        },
    )


def filled_arrow_manifest(page_dir: Path, text: str = "下一阶段") -> Path:
    return base_manifest(
        page_dir,
        {
            "id": "arrow-filled",
            "type": "shape",
            "preset": "rightArrow",
            "box_px": [410, 300, 300, 84],
            "fill": "#2563EB",
            "stroke": "none",
            "text": text,
            "font": "Microsoft YaHei",
            "font_size": 16,
            "text_color": "#FFFFFF",
            "align": "center",
            "valign": "middle",
            "z_index": 140,
        },
        text_inventory=[text],
    )


def build_page(page_dir: Path) -> Path:
    result = subprocess.run(
        [*image2ppt_command(), "page", "build", str(page_dir)],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise AssertionError(result.stdout + result.stderr)
    return page_dir / "page.pptx"


def build_deck(deck_manifest: Path, out: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(image2ppt_runtime_script("build_pptx_from_manifest.py")),
            "--deck-manifest",
            str(deck_manifest),
            "--out",
            str(out),
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise AssertionError(result.stdout + result.stderr)
