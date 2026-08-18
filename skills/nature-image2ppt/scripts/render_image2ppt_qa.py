#!/usr/bin/env python3
"""Render Image2PPT output with PowerPoint or project-local LibreOffice fallback."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any

from PIL import Image, ImageChops, ImageStat

from runtime_paths import resolve_inside


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def image_diff(source: Path, rendered: Path) -> dict[str, Any]:
    with Image.open(source).convert("RGB") as src, Image.open(rendered).convert("RGB") as rnd:
        original = list(rnd.size)
        if rnd.size != src.size:
            rnd = rnd.resize(src.size)
        diff = ImageChops.difference(src, rnd)
        stat = ImageStat.Stat(diff)
        extrema = diff.getextrema()
        return {
            "source_png": str(source),
            "rendered_png": str(rendered),
            "source_size": list(src.size),
            "rendered_original_size": original,
            "mean_abs_rgb_diff_0_255": round(sum(stat.mean) / len(stat.mean), 2),
            "max_abs_rgb_diff_0_255": max(channel[1] for channel in extrema),
            "note": "Indicative only; the page still requires visual review.",
        }


def render_existing(existing: Path, out_dir: Path) -> tuple[list[Path], dict[str, Any]]:
    if not existing.is_file():
        return [], {"status": "error", "renderer": "existing-rendered-png", "error": f"missing image: {existing}"}
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / "slide_01.png"
    if existing.resolve() != target.resolve():
        shutil.copy2(existing, target)
    return [target], {
        "status": "rendered",
        "renderer": "existing-rendered-png",
        "backend": "user-supplied-powerpoint-render",
        "slides": [str(target.resolve())],
    }


def powershell_quote(value: Path) -> str:
    return "'" + str(value).replace("'", "''") + "'"


def render_powerpoint(pptx: Path, out_dir: Path, timeout: int) -> tuple[list[Path], dict[str, Any]]:
    powershell = shutil.which("powershell.exe") or shutil.which("powershell")
    if not powershell:
        return [], {"status": "renderer-unavailable", "error": "PowerShell was not found for PowerPoint COM"}
    out_dir.mkdir(parents=True, exist_ok=True)
    # PowerPoint localizes exported slide filenames (for example, 幻灯片1.PNG).
    # Remove only prior generated PNG renders so a stale rendered.png cannot be
    # mistaken for the newest COM export on a repeat QA pass.
    for prior in list(out_dir.glob("*.PNG")) + list(out_dir.glob("*.png")):
        if prior.is_file():
            prior.unlink()
    script = (
        "$ErrorActionPreference='Stop';$app=$null;$deck=$null;"
        "try{$app=New-Object -ComObject PowerPoint.Application;"
        "$deck=$app.Presentations.Open(" + powershell_quote(pptx) + ",$true,$true,$false);"
        "$deck.Export(" + powershell_quote(out_dir) + ",'PNG')}"
        "finally{"
        "if($null -ne $deck){try{$deck.Close()}catch{};"
        "try{[System.Runtime.InteropServices.Marshal]::ReleaseComObject($deck)|Out-Null}catch{};$deck=$null};"
        "if($null -ne $app){try{$app.Quit()}catch{};"
        "try{[System.Runtime.InteropServices.Marshal]::ReleaseComObject($app)|Out-Null}catch{};$app=$null}"
        "}"
    )
    command = [powershell, "-NoProfile", "-NonInteractive", "-Command", script]
    try:
        proc = subprocess.run(command, text=True, capture_output=True, timeout=timeout, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return [], {"status": "error", "renderer": "powerpoint-com", "error": repr(exc), "command": command}
    rendered = sorted(out_dir.glob("*.PNG")) + sorted(out_dir.glob("*.png"))
    # De-duplicate on case-insensitive filesystems.
    rendered = list(dict.fromkeys(path.resolve() for path in rendered))
    return rendered, {
        "status": "rendered" if proc.returncode == 0 and rendered else "error",
        "renderer": "powerpoint-com",
        "backend": "powerpoint-export-png",
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "command": command,
        "slides": [str(path) for path in rendered],
    }


def render_libreoffice(pptx: Path, out_dir: Path, dpi: int, timeout: int) -> tuple[list[Path], dict[str, Any]]:
    soffice = shutil.which("libreoffice") or shutil.which("soffice")
    if not soffice:
        return [], {"status": "renderer-unavailable", "error": "LibreOffice/soffice not found"}
    out_dir.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    with tempfile.TemporaryDirectory(prefix="image2ppt-libreoffice-") as temp_name:
        temp_dir = Path(temp_name)
        profile = temp_dir / "profile"
        profile.mkdir()
        command = [
            soffice,
            "--headless",
            f"-env:UserInstallation={profile.as_uri()}",
            "--convert-to",
            "pdf",
            "--outdir",
            str(temp_dir),
            str(pptx),
        ]
        try:
            proc = subprocess.run(
                command,
                text=True,
                capture_output=True,
                timeout=timeout,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            return [], {
                "status": "error",
                "renderer": "libreoffice",
                "error": repr(exc),
                "command": command,
            }
        pdf = temp_dir / f"{pptx.stem}.pdf"
        if proc.returncode != 0 or not pdf.is_file():
            return [], {
                "status": "error",
                "renderer": "libreoffice",
                "returncode": proc.returncode,
                "stdout": proc.stdout,
                "stderr": proc.stderr,
                "command": command,
                "error": "LibreOffice did not create the expected PDF",
            }
        try:
            import pypdfium2 as pdfium

            document = pdfium.PdfDocument(str(pdf))
            rendered: list[Path] = []
            scale = dpi / 72.0
            try:
                for index in range(len(document)):
                    page = document[index]
                    bitmap = None
                    try:
                        target = out_dir / f"slide_{index + 1:02d}.png"
                        bitmap = page.render(
                            scale=scale,
                            fill_color=(255, 255, 255, 255),
                            draw_annots=True,
                        )
                        with bitmap.to_pil() as image:
                            rgb = image.convert("RGB")
                            try:
                                rgb.save(target)
                            finally:
                                rgb.close()
                        rendered.append(target)
                    finally:
                        if bitmap is not None:
                            bitmap.close()
                        page.close()
            finally:
                document.close()
        except Exception as exc:
            return [], {
                "status": "error",
                "renderer": "libreoffice",
                "error": repr(exc),
                "command": command,
            }
    raw = {
        "status": "rendered" if rendered else "error",
        "renderer": "libreoffice",
        "backend": "soffice-pdf-pdfium",
        "command": command,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "elapsed_seconds": round(time.perf_counter() - started, 3),
        "slides": [str(path.resolve()) for path in rendered],
    }
    return rendered, raw


def main() -> int:
    parser = argparse.ArgumentParser(description="Render PPTX for Image2PPT visual QA")
    parser.add_argument("pptx", type=Path)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--source", type=Path)
    parser.add_argument("--existing-rendered", type=Path)
    parser.add_argument("--dpi", type=int, default=150)
    parser.add_argument("--timeout", type=int, default=120)
    args = parser.parse_args()

    pptx = args.pptx.expanduser().resolve()
    scope = pptx.parent
    try:
        out_dir = resolve_inside(scope, args.out_dir)
        report_path = resolve_inside(scope, args.report)
        source = resolve_inside(scope, args.source) if args.source else None
        existing = resolve_inside(scope, args.existing_rendered) if args.existing_rendered else None
    except ValueError as exc:
        raise SystemExit(f"render QA paths must stay inside {scope}") from exc
    if existing and source and existing.is_file() and source.is_file() and sha256_file(existing) == sha256_file(source):
        report = {
            "schema_version": "image2ppt-render-qa-v1",
            "status": "error",
            "renderer": "existing-rendered-png",
            "pptx": str(pptx),
            "source_image": str(source),
            "rendered_png": str(existing),
            "error": "existing rendered image is byte-identical to source.png; source reuse cannot prove PPTX rendering",
        }
        write_json(report_path, report)
        print(json.dumps({"status": "error", "report": str(report_path), "error": report["error"]}, ensure_ascii=True))
        return 2
    if existing:
        rendered, raw = render_existing(existing, out_dir)
    elif platform.system().lower() == "windows":
        rendered, raw = render_powerpoint(pptx, out_dir, args.timeout)
    else:
        rendered, raw = render_libreoffice(pptx, out_dir, args.dpi, args.timeout)
    stable = None
    if rendered and source:
        stable = out_dir / "rendered.png"
        first = rendered[0]
        if first.resolve() != stable.resolve():
            first.replace(stable)
        rendered = [stable, *rendered[1:]]
        raw["slides"] = [str(path.resolve()) for path in rendered]
    status = "rendered" if rendered and (stable is None or stable.is_file()) else raw.get("status", "error")
    report: dict[str, Any] = {
        "schema_version": "image2ppt-render-qa-v1",
        "status": status,
        "renderer": raw.get("renderer"),
        "pptx": str(pptx),
        "out_dir": str(out_dir),
        "rendered_png": str(stable) if stable else None,
        "rendered_slides": [str(path) for path in rendered],
        "source_image": str(source) if source else None,
        "raw": raw,
    }
    if source and source.is_file() and stable:
        report["diff_metrics"] = image_diff(source, stable)
    write_json(report_path, report)
    print(json.dumps({"status": report["status"], "report": str(report_path)}, ensure_ascii=True))
    return 0 if report["status"] == "rendered" else 2


if __name__ == "__main__":
    raise SystemExit(main())
