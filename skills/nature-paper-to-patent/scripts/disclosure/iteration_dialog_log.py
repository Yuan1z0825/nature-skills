#!/usr/bin/env python3
"""
在案件目录追加「交底书修订对话记录.md」一条：含记录时间（本地 + UTC）、用户说明摘要、交付文件名、合并/纠正摘要摘录。
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_LOG = "交底书修订对话记录.md"

FILE_HEADER = """# 交底书修订对话记录

> 由 `iteration_dialog_log.py` 或 Agent 按 `references/disclosure/iteration_context.md` 追加；每条含**记录时间**与本轮说明。请勿删除既有条目。

"""


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Append one revision dialog entry to case-dir log markdown"
    )
    parser.add_argument(
        "--case-dir",
        type=Path,
        required=True,
        help="案件产出目录（与交底书 .md 同级或为其父目录，须已存在）",
    )
    parser.add_argument(
        "--kind",
        choices=("merge", "correct"),
        required=True,
        help="merge=合并迭代；correct=纠正迭代",
    )
    parser.add_argument(
        "--user",
        default="",
        help="用户本轮说明摘要（建议 1–8 句）",
    )
    parser.add_argument(
        "--summary",
        default="",
        help="合并摘要 / 纠正摘要的简短摘录（可与对话中留档段落一致）",
    )
    parser.add_argument(
        "--artifacts",
        default="",
        help="本轮交付文件名，多个用英文逗号分隔，如：一种XX_20260408143025.md,一种XX_20260408143025.docx",
    )
    parser.add_argument(
        "--log-name",
        default=DEFAULT_LOG,
        help=f"日志文件名（默认：{DEFAULT_LOG}）",
    )
    args = parser.parse_args()

    case_dir = args.case_dir.expanduser().resolve()
    if not case_dir.is_dir():
        print(f"ERROR: 目录不存在或不是目录: {case_dir}", file=sys.stderr)
        return 2

    log_path = case_dir / args.log_name
    now_local = datetime.now().astimezone()
    now_utc = datetime.now(timezone.utc)
    kind_zh = "合并迭代" if args.kind == "merge" else "纠正迭代"

    user_block = (args.user or "").strip() or "（未传入 --user，请 Agent 用编辑工具在本条内补写用户说明摘要。）"
    summary_block = (args.summary or "").strip() or "—"
    art = (args.artifacts or "").strip()
    if art:
        art_lines = "\n".join(f"- `{x.strip()}`" for x in art.split(",") if x.strip())
    else:
        art_lines = "—"

    entry = f"""## {now_local.strftime("%Y-%m-%d %H:%M:%S")}（本地） · {now_utc.strftime("%Y-%m-%dT%H:%M:%SZ")}（UTC）

**类型**：{kind_zh}

**用户说明摘要**：

{user_block}

**本轮交付文件**：

{art_lines}

**合并/纠正摘要摘录**：

{summary_block}

---

"""

    if log_path.exists():
        prev = log_path.read_text(encoding="utf-8")
        if prev and not prev.endswith("\n"):
            prev += "\n"
        log_path.write_text(prev + "\n" + entry, encoding="utf-8")
    else:
        log_path.write_text(FILE_HEADER + "\n" + entry, encoding="utf-8")

    print(f"LOG_FILE={log_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
