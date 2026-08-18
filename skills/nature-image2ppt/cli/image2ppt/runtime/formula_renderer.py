#!/usr/bin/env python3
"""Render LaTeX formulas into image assets for page manifests."""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from deck_run_state import resolve_inside


DEFAULT_ENGINE_CANDIDATES = ("xelatex", "lualatex", "pdflatex")
DEFAULT_TIMEOUT = 120
DEFAULT_DPI = 300
SUPPORTED_FORMATS = {"svg", "png", "pdf"}


class FormulaRenderError(RuntimeError):
    pass


def select_latex_engine(engine: str | None = None) -> str:
    if engine and engine != "auto":
        resolved = shutil.which(engine)
        if not resolved:
            raise FormulaRenderError(f"LaTeX engine not found: {engine}")
        return resolved
    for candidate in DEFAULT_ENGINE_CANDIDATES:
        resolved = shutil.which(candidate)
        if resolved:
            return resolved
    raise FormulaRenderError(
        "No LaTeX engine found. Install a TeX distribution that provides xelatex, lualatex, or pdflatex."
    )


def render_latex_asset(
    *,
    tex: str,
    out: str | Path,
    page_dir: str | Path | None = None,
    output_format: str | None = None,
    engine: str | None = None,
    preamble: str = "",
    full_document: bool = False,
    display: bool = True,
    dpi: int = DEFAULT_DPI,
    timeout: int = DEFAULT_TIMEOUT,
    shell_escape: bool = False,
    keep_workdir: str | Path | None = None,
) -> dict[str, Any]:
    if not tex.strip():
        raise FormulaRenderError("LaTeX input is empty.")
    out_path = resolve_output_path(out, page_dir)
    fmt = normalise_format(output_format, out_path)
    source_tex = out_path.with_suffix(".tex")
    source_tex.parent.mkdir(parents=True, exist_ok=True)
    document = build_latex_document(tex, preamble=preamble, full_document=full_document, display=display)
    source_tex.write_text(document, encoding="utf-8")

    resolved_engine = select_latex_engine(engine)
    with tempfile.TemporaryDirectory() as tmp:
        workdir = Path(tmp)
        work_tex = workdir / "formula.tex"
        work_tex.write_text(document, encoding="utf-8")
        command = [
            resolved_engine,
            "-interaction=nonstopmode",
            "-halt-on-error",
            "-file-line-error",
        ]
        if shell_escape:
            command.append("-shell-escape")
        command.append(work_tex.name)
        result = subprocess.run(
            command,
            cwd=workdir,
            text=True,
            capture_output=True,
            timeout=timeout,
        )
        if result.returncode != 0:
            _maybe_keep_workdir(workdir, keep_workdir)
            raise FormulaRenderError(_latex_error_message(result))
        pdf = workdir / "formula.pdf"
        if not pdf.exists():
            _maybe_keep_workdir(workdir, keep_workdir)
            raise FormulaRenderError("LaTeX completed but formula.pdf was not produced.")
        converter = convert_pdf(pdf, out_path, fmt, dpi=dpi, timeout=timeout)
        _maybe_keep_workdir(workdir, keep_workdir)
    return {
        "out": str(out_path),
        "format": fmt,
        "tex_source": str(source_tex),
        "engine": Path(resolved_engine).name,
        "converter": converter,
    }


def build_latex_document(tex: str, *, preamble: str = "", full_document: bool = False, display: bool = True) -> str:
    if full_document:
        return tex if tex.endswith("\n") else tex + "\n"
    body = tex.strip()
    if display:
        body = "\\[\n" + body + "\n\\]"
    else:
        body = "$" + body + "$"
    return (
        "\\documentclass[border=2pt]{standalone}\n"
        "\\usepackage{amsmath,amssymb,mathtools,bm}\n"
        "\\usepackage{xcolor}\n"
        f"{preamble.strip()}\n"
        "\\begin{document}\n"
        f"{body}\n"
        "\\end{document}\n"
    )


def convert_pdf(pdf: Path, out_path: Path, fmt: str, *, dpi: int, timeout: int) -> str:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if fmt == "pdf":
        shutil.copy2(pdf, out_path)
        return "copy-pdf"
    if fmt == "svg":
        dvisvgm = shutil.which("dvisvgm")
        if dvisvgm:
            command = [dvisvgm, "--pdf", "--no-fonts", "--exact", "--output", str(out_path), str(pdf)]
            _run_converter(command, timeout)
            return "dvisvgm"
        pdf2svg = shutil.which("pdf2svg")
        if pdf2svg:
            command = [pdf2svg, str(pdf), str(out_path)]
            _run_converter(command, timeout)
            return "pdf2svg"
        raise FormulaRenderError("SVG output requires dvisvgm or pdf2svg.")
    if fmt == "png":
        magick = shutil.which("magick") or shutil.which("convert")
        if not magick:
            raise FormulaRenderError("PNG output requires ImageMagick (`magick` or `convert`).")
        command = [magick, "-density", str(dpi), str(pdf), "-trim", "+repage", str(out_path)]
        _run_converter(command, timeout)
        return Path(magick).name
    raise FormulaRenderError(f"Unsupported formula output format: {fmt}")


def formula_image_fragment(
    *,
    formula_id: str,
    image_path: str | Path,
    tex_source: str | Path,
    box_px: str | list[Any],
    page_dir: str | Path | None = None,
    z_index: int = 220,
    alt: str | None = None,
) -> dict[str, Any]:
    path_for_manifest = manifest_path(image_path, page_dir)
    tex_for_manifest = manifest_path(tex_source, page_dir)
    return {
        "schema_version": 1,
        "type": "latex-formula-image-fragment",
        "images": [
            {
                "id": formula_id,
                "path": path_for_manifest,
                "box_px": parse_box_px(box_px),
                "alt": alt or f"LaTeX rendered formula {formula_id}",
                "z_index": z_index,
            }
        ],
        "asset_provenance": [
            {
                "path": path_for_manifest,
                "source": tex_for_manifest,
                "source_type": "latex-rendered-formula",
                "provenance_note": "Rendered from LaTeX by image2ppt formula render-latex; visual fidelity is prioritized over formula editability.",
            }
        ],
        "formula_inventory": [
            {
                "id": formula_id,
                "decision": "latex-rendered-image",
                "editable": False,
                "image": path_for_manifest,
                "tex_source": tex_for_manifest,
            }
        ],
    }


def write_json(payload: dict[str, Any], path: str | Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def resolve_output_path(out: str | Path, page_dir: str | Path | None = None) -> Path:
    path = Path(out)
    if page_dir:
        try:
            return resolve_inside(page_dir, path)
        except ValueError as exc:
            raise FormulaRenderError(f"Formula output must stay inside page_dir: {out}") from exc
    return path.resolve()


def normalise_format(output_format: str | None, out_path: Path) -> str:
    fmt = (output_format or out_path.suffix.lstrip(".") or "svg").lower()
    if fmt == "jpg":
        fmt = "jpeg"
    if fmt not in SUPPORTED_FORMATS:
        raise FormulaRenderError(f"Unsupported formula output format: {fmt}. Use svg, png, or pdf.")
    return fmt


def parse_box_px(value: str | list[Any]) -> list[float]:
    parts = [part.strip() for part in value.split(",")] if isinstance(value, str) else list(value)
    if len(parts) != 4:
        raise FormulaRenderError("box_px must be x,y,width,height")
    return [float(part) for part in parts]


def manifest_path(path: str | Path, page_dir: str | Path | None = None) -> str:
    resolved = Path(path).resolve()
    if page_dir:
        root = Path(page_dir).resolve()
        try:
            return resolved.relative_to(root).as_posix()
        except ValueError:
            pass
    return resolved.as_posix()


def _run_converter(command: list[str], timeout: int) -> None:
    result = subprocess.run(command, text=True, capture_output=True, timeout=timeout)
    if result.returncode != 0:
        raise FormulaRenderError(
            "Formula conversion failed: "
            + " ".join(command)
            + "\n"
            + "\n".join((result.stderr or result.stdout or "").splitlines()[-20:])
        )


def _latex_error_message(result: subprocess.CompletedProcess[str]) -> str:
    log = result.stdout or result.stderr or ""
    tail = "\n".join(log.splitlines()[-30:])
    return f"LaTeX render failed with exit code {result.returncode}.\n{tail}"


def _maybe_keep_workdir(workdir: Path, keep_workdir: str | Path | None) -> None:
    if not keep_workdir:
        return
    target = Path(keep_workdir)
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(workdir, target)
