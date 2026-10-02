#!/usr/bin/env python3
"""
将 Word（.docx）转为 Markdown，并把内嵌图片抽取到磁盘，便于 Step 2 扫描与 Agent Read。

依赖 mammoth（见仓库根目录 requirements.txt）。

用法:
  python docx_to_md.py --input design.docx --output outputs/case/design.md
  python docx_to_md.py -i a.docx -o b/out.md --media-dir b/my_images

默认图片目录：与输出 .md 同级的「{md 文件名}_media/」，Markdown 中为相对路径引用。
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _require_mammoth():
    try:
        import mammoth
    except ImportError:
        print(
            "缺少依赖 mammoth。请在技能根目录执行: pip install -r requirements.txt",
            file=sys.stderr,
        )
        sys.exit(1)
    return mammoth


def _extension_for_content_type(content_type: str) -> str:
    subtype = (content_type or "").split("/")[-1].lower().strip()
    if not subtype or subtype == "octet-stream":
        return "bin"
    if subtype == "jpeg":
        return "jpg"
    return subtype[:12]


def _run(
    input_docx: Path,
    output_md: Path,
    media_dir: Path | None,
) -> int:
    mammoth = _require_mammoth()

    if not input_docx.is_file():
        print(f"输入文件不存在: {input_docx}", file=sys.stderr)
        return 2
    if input_docx.suffix.lower() != ".docx":
        print("警告: 期望 .docx（Office Open XML）；旧版 .doc 不支持。", file=sys.stderr)

    output_md = output_md.resolve()
    output_md.parent.mkdir(parents=True, exist_ok=True)

    if media_dir is None:
        media_dir = output_md.parent / f"{output_md.stem}_media"
    else:
        media_dir = media_dir.resolve()
    media_dir.mkdir(parents=True, exist_ok=True)

    counter = [0]

    def save_image(image):
        counter[0] += 1
        ext = _extension_for_content_type(getattr(image, "content_type", "") or "")
        filename = f"img_{counter[0]:04d}.{ext}"
        out_path = media_dir / filename
        try:
            with image.open() as f:
                out_path.write_bytes(f.read())
        except Exception as e:
            print(f"警告: 抽取图片失败 ({filename}): {e}", file=sys.stderr)
            return {"src": "", "alt": ""}

        try:
            rel = out_path.relative_to(output_md.parent).as_posix()
        except ValueError:
            rel = out_path.as_posix()
        alt = getattr(image, "alt_text", None) or ""
        return {"src": rel, "alt": alt}

    image_converter = mammoth.images.img_element(save_image)

    with input_docx.open("rb") as docx_file:
        result = mammoth.convert_to_markdown(docx_file, convert_image=image_converter)

    for msg in result.messages:
        text = getattr(msg, "message", str(msg))
        typ = getattr(msg, "type", "message")
        print(f"mammoth [{typ}]: {text}", file=sys.stderr)

    text = (result.value or "").strip()
    header = (
        f"<!-- 由 docx_to_md.py 自 {input_docx.name} 转换，勿手改本行元信息 -->\n\n"
    )
    output_md.write_text(header + text + ("\n" if text else ""), encoding="utf-8")

    print(f"已写入: {output_md}")
    print(f"图片目录: {media_dir}")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="Word (.docx) → Markdown + 抽取图片")
    p.add_argument("-i", "--input", required=True, type=Path, help="输入 .docx 路径")
    p.add_argument("-o", "--output", required=True, type=Path, help="输出 .md 路径")
    p.add_argument(
        "--media-dir",
        type=Path,
        default=None,
        help="图片输出目录（默认：与 .md 同级的 {md 主名}_media）",
    )
    args = p.parse_args()
    return _run(args.input, args.output, args.media_dir)


if __name__ == "__main__":
    raise SystemExit(main())
