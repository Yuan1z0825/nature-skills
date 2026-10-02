#!/usr/bin/env python3
r"""
将 Markdown 中的 LaTeX 公式渲染为 PNG（matplotlib mathtext），**保留 `$...$` / `\(...\)` / `$$...$$` / `\[...\]` 原文**，
图片引用写入 HTML 注释 ``<!-- ![...](path) -->``（预览不显示图，Word 仍嵌入）。

支持（失败时**保留原文**，不中断）：

- **块级**：``$$ ... $$``（可跨行）、单行 ``$$...$$``、``\\[ ... \\]``
- **行内**：``$...$``、``\(...\)``（渲染失败则保留原文）

用法：

  python scripts/disclosure/math_render.py -i draft.md -o draft_with_math.md
  python scripts/disclosure/math_render.py -i draft.md -o out.md --assets-dir math_figures

依赖：``pip install matplotlib``（见仓库根 ``requirements.txt``）。
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

_DEFAULT_ASSETS = "math_figures"
_INLINE_RE = re.compile(
    r"(?<!\$)\$(?!\$)((?:\\.|[^$\n])+?)\$(?!\$)(?!\s*<!--)"
)
_INLINE_PAREN_RE = re.compile(r"\\\(((?:\\.|[^)])+?)\\\)(?!\s*<!--)")
_HIDDEN_IMG_COMMENT_RE = re.compile(
    r"<!--\s*!\[[^\]]*\]\([^)]+\)\s*-->"
)

# matplotlib mathtext 不识别部分 LaTeX 简写；按「长命令优先」映射为 mathtext 符号
_LATEX_CMD_ALIASES: tuple[tuple[str, str], ...] = (
    ("geqslant", "geq"),
    ("leqslant", "leq"),
    ("geqq", "geq"),
    ("leqq", "leq"),
    ("ge", "geq"),
    ("le", "leq"),
    ("ne", "neq"),
    ("land", "wedge"),
    ("lor", "vee"),
    ("gets", "leftarrow"),
    ("to", "rightarrow"),
    ("iff", "Longleftrightarrow"),
    ("implies", "Rightarrow"),
)


def normalize_latex_for_mathtext(body: str) -> str:
    """将常见 LaTeX 命令转为 matplotlib mathtext 可解析形式。"""
    out = body
    for short, repl in _LATEX_CMD_ALIASES:
        if short == repl:
            continue
        out = re.sub(rf"\\{short}(?![A-Za-z])", rf"\\{repl}", out)
    # 交底书 Word 正文为常规宋体，公式图不做数学粗体
    for cmd in ("mathbf", "bm", "boldsymbol", "textbf"):
        prev = None
        while prev != out:
            prev = out
            out = re.sub(rf"\\{cmd}\{{([^{{}}]+)\}}", r"\1", out)
    # mathtext 不支持 amsmath 编号/标签；块级公式内换行也会解析失败
    out = re.sub(r"\\label\s*\{[^{}]*\}", "", out)
    out = re.sub(r"\\tag\s*\{([^{}]*)\}", r"\\quad (\1)", out)
    out = re.sub(r"\\notag\b", "", out)
    out = re.sub(r"\s+", " ", out).strip()
    return out


def render_latex_to_png(
    latex: str,
    png_path: Path,
    *,
    dpi: int = 200,
    fontsize: float = 14.0,
) -> None:
    """用 matplotlib mathtext 将 LaTeX 片段写入 PNG（无坐标轴/网格）。"""
    import matplotlib

    matplotlib.use("Agg")
    from matplotlib import mathtext
    from matplotlib.font_manager import FontProperties

    body = latex.strip()
    if body.startswith("$") and body.endswith("$") and not body.startswith("$$"):
        body = body[1:-1].strip()
    if body.startswith("\\(") and body.endswith("\\)"):
        body = body[2:-2].strip()

    body = normalize_latex_for_mathtext(body)

    png_path.parent.mkdir(parents=True, exist_ok=True)
    mathtext.math_to_image(
        f"${body}$",
        str(png_path),
        prop=FontProperties(size=fontsize, weight="normal"),
        dpi=dpi,
        format="png",
    )


def _next_eq_name(counter: dict[str, int], kind: str) -> str:
    counter[kind] = counter.get(kind, 0) + 1
    n = counter[kind]
    if kind == "inline":
        return f"inline_{n:03d}.png"
    return f"eq_{n:03d}.png"


def _try_render(
    latex: str,
    png_path: Path,
    *,
    dpi: int,
    fontsize: float,
) -> bool:
    try:
        render_latex_to_png(latex, png_path, dpi=dpi, fontsize=fontsize)
        return png_path.is_file() and png_path.stat().st_size > 0
    except Exception as e:
        snippet = latex.strip().replace("\n", " ")[:120]
        print(f"[math_render] 渲染失败（将保留原文）：{snippet}", file=sys.stderr)
        print(f"  {e}", file=sys.stderr)
        return False


def _replace_inline_math(
    text: str,
    assets_dir: Path,
    assets_rel: str,
    counter: dict[str, int],
    *,
    dpi: int,
    fontsize: float,
) -> tuple[str, int, int]:
    ok = 0
    failed = 0

    def render_one(inner: str, wrapper: str) -> str:
        nonlocal ok, failed
        fname = _next_eq_name(counter, "inline")
        png_path = assets_dir / fname
        if _try_render(inner, png_path, dpi=dpi, fontsize=fontsize):
            ok += 1
            rel = f"{assets_rel.strip('/')}/{fname}".replace("\\", "/")
            return f"{wrapper}<!-- ![公式·行内]({rel}) -->"
        failed += 1
        return wrapper

    def repl_dollar(m: re.Match[str]) -> str:
        inner = m.group(1)
        return render_one(inner, f"${inner}$")

    def repl_paren(m: re.Match[str]) -> str:
        inner = m.group(1)
        return render_one(inner, f"\\({inner}\\)")

    text = _INLINE_RE.sub(repl_dollar, text)
    text = _INLINE_PAREN_RE.sub(repl_paren, text)
    return text, ok, failed


def render_markdown_math(
    md_text: str,
    *,
    out_md_path: Path,
    assets_rel: str = _DEFAULT_ASSETS,
    dpi: int = 200,
    block_fontsize: float = 10.5,
    inline_fontsize: float = 10.5,
) -> tuple[str, int, int]:
    """
    返回 (新 markdown, 成功渲染数, 失败保留原文数)。
    PNG 目录：``out_md_path.parent / assets_rel``。
    """
    assets_dir = out_md_path.parent / assets_rel.strip("/\\")
    assets_dir.mkdir(parents=True, exist_ok=True)
    counter: dict[str, int] = {}
    ok = 0
    failed = 0

    lines = md_text.splitlines(keepends=True)
    out: list[str] = []
    i = 0

    while i < len(lines):
        stripped = lines[i].strip()

        # 块级 $$ ... $$
        if stripped == "$$":
            i += 1
            body_lines: list[str] = []
            while i < len(lines) and lines[i].strip() != "$$":
                body_lines.append(lines[i])
                i += 1
            closing = i < len(lines)
            if closing:
                i += 1
            if i < len(lines) and _HIDDEN_IMG_COMMENT_RE.match(lines[i].strip()):
                out.append("$$\n")
                out.extend(body_lines)
                out.append("$$\n")
                out.append(lines[i])
                i += 1
                continue
            latex = "".join(body_lines).strip()
            if not latex:
                out.append("$$\n")
                if body_lines:
                    out.extend(body_lines)
                if closing:
                    out.append("$$\n")
                continue
            fname = _next_eq_name(counter, "block")
            png_path = assets_dir / fname
            if _try_render(latex, png_path, dpi=dpi, fontsize=block_fontsize):
                ok += 1
                rel = f"{assets_rel.strip('/')}/{fname}".replace("\\", "/")
                out.append("$$\n")
                out.extend(body_lines)
                out.append("$$\n")
                out.append(f"<!-- ![公式]({rel}) -->\n")
            else:
                failed += 1
                out.append("$$\n")
                out.extend(body_lines)
                if not body_lines or not body_lines[-1].endswith("\n"):
                    pass
                out.append("$$\n")
            continue

        # 单行 $$...$$
        if (
            stripped.startswith("$$")
            and stripped.endswith("$$")
            and len(stripped) > 4
        ):
            latex = stripped[2:-2].strip()
            fname = _next_eq_name(counter, "block")
            png_path = assets_dir / fname
            if _try_render(latex, png_path, dpi=dpi, fontsize=block_fontsize):
                ok += 1
                rel = f"{assets_rel.strip('/')}/{fname}".replace("\\", "/")
                out.append(f"$${latex}$$\n")
                out.append(f"<!-- ![公式]({rel}) -->\n")
            else:
                failed += 1
                out.append(lines[i])
            i += 1
            continue

        # 块级 \[ ... \]
        if stripped.startswith("\\["):
            if stripped.endswith("\\]") and len(stripped) > 4:
                latex = stripped[2:-2].strip()
                fname = _next_eq_name(counter, "block")
                png_path = assets_dir / fname
                if _try_render(latex, png_path, dpi=dpi, fontsize=block_fontsize):
                    ok += 1
                    rel = f"{assets_rel.strip('/')}/{fname}".replace("\\", "/")
                    out.append(f"\\[{latex}\\]\n")
                    out.append(f"<!-- ![公式]({rel}) -->\n")
                else:
                    failed += 1
                    out.append(lines[i])
                i += 1
                continue
            i += 1
            body_lines = []
            while i < len(lines) and "\\]" not in lines[i]:
                body_lines.append(lines[i])
                i += 1
            tail = lines[i] if i < len(lines) else ""
            if i < len(lines):
                i += 1
            if i < len(lines) and _HIDDEN_IMG_COMMENT_RE.match(lines[i].strip()):
                out.append("\\[\n")
                out.extend(body_lines)
                out.append(tail if tail.endswith("\n") else tail + "\n")
                out.append(lines[i])
                i += 1
                continue
            latex = "".join(body_lines) + tail
            latex = latex.replace("\\[", "", 1).replace("\\]", "").strip()
            fname = _next_eq_name(counter, "block")
            png_path = assets_dir / fname
            if latex and _try_render(latex, png_path, dpi=dpi, fontsize=block_fontsize):
                ok += 1
                rel = f"{assets_rel.strip('/')}/{fname}".replace("\\", "/")
                out.append("\\[\n")
                out.extend(body_lines)
                out.append(tail if tail.endswith("\n") else tail + "\n")
                out.append(f"<!-- ![公式]({rel}) -->\n")
            else:
                failed += 1
                out.append("\\[\n")
                out.extend(body_lines)
                out.append(tail if tail.endswith("\n") else tail + "\n")
            continue

        # 围栏代码 / mermaid：不处理行内 $
        if stripped.startswith("```"):
            out.append(lines[i])
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                out.append(lines[i])
                i += 1
            if i < len(lines):
                out.append(lines[i])
                i += 1
            continue

        # 标题、图片行、空行：原样（图片行不跑行内替换）
        if (
            not stripped
            or stripped.startswith("#")
            or (stripped.startswith("![") and "](" in stripped)
        ):
            out.append(lines[i])
            i += 1
            continue

        new_line, i_ok, i_fail = _replace_inline_math(
            lines[i],
            assets_dir,
            assets_rel,
            counter,
            dpi=dpi,
            fontsize=inline_fontsize,
        )
        ok += i_ok
        failed += i_fail
        out.append(new_line if new_line.endswith("\n") else new_line + "\n")
        i += 1

    return "".join(out), ok, failed


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Markdown LaTeX 公式 → PNG")
    p.add_argument("-i", "--input", required=True, type=Path)
    p.add_argument("-o", "--output", required=True, type=Path)
    p.add_argument(
        "--assets-dir",
        default=_DEFAULT_ASSETS,
        help=f"PNG 相对输出 .md 的子目录（默认 {_DEFAULT_ASSETS}）",
    )
    p.add_argument("--dpi", type=int, default=200)
    p.add_argument("--block-fontsize", type=float, default=10.5)
    p.add_argument("--inline-fontsize", type=float, default=10.5)
    args = p.parse_args(argv)

    in_path = args.input.resolve()
    if not in_path.is_file():
        print(f"错误：找不到输入 {in_path}", file=sys.stderr)
        return 1

    try:
        import matplotlib  # noqa: F401
    except ImportError:
        print("请先安装: pip install matplotlib", file=sys.stderr)
        return 1

    out_path = args.output.resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    md = in_path.read_text(encoding="utf-8")

    new_md, ok, failed = render_markdown_math(
        md,
        out_md_path=out_path,
        assets_rel=args.assets_dir.strip("/\\") or _DEFAULT_ASSETS,
        dpi=args.dpi,
        block_fontsize=args.block_fontsize,
        inline_fontsize=args.inline_fontsize,
    )
    out_path.write_text(new_md, encoding="utf-8")
    msg = f"已写入 {out_path}（公式：{ok} 处已转为 PNG"
    if failed:
        msg += f"，{failed} 处失败已保留原文"
    print(msg + "）", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
