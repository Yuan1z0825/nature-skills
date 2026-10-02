# -*- coding: utf-8 -*-
"""
国知局公布站「检索 + 解析」一步完成：内存中持有结果页 HTML，**默认不落盘**。

内部调用 ``cnipa_epub_crawler.search_epub_keyword``（等同先 ``fetch_epub_result_html`` 再
``parse_search_result_html``）。

**输出约定**（便于 Agent 抓取且不触发误判降级）：

- **stdout**：**仅一行** ``EPUB_HITS_JSON:`` + JSON 数组（UTF-8，含中文标题与 ``abstract``）。
- **stderr**：``EPUB_MERGE:`` / ``EPUB_NOTE:`` / ``EPUB_HINT:`` 等为 **ASCII**，减轻 PowerShell 把
  含中文的 stderr 当成 ``NativeCommandError``，以及 ``2>&1`` 合并流时的乱码。stdout 上 JSON 仍为 UTF-8
  中文。启动时 ``reconfigure`` UTF-8。

**检索词拆分（仅按空白）**：命令行中所有参数会按 **Python 空白规则**（`str.split()`）拆成多段；
**一段一查**，结果按公开号去重合并。**不在本脚本内**对长中文做自动分词或拆字——**相关度高的语义化
检索单位须在 Agent 生成 Bash 前完成**（见 ``references/disclosure/prior_art_search.md``「国知局检索词（生成阶段必做）」）。
若需**整句一次**向公布站提交（站内 AND），请改用 ``cnipa_epub_crawler.py`` 单传一句。

需已安装：pip install -r scripts/disclosure/requirements-cnipa.txt && python -m playwright install chromium

用法：

  python scripts/disclosure/cnipa_epub_search.py 词1
  python scripts/disclosure/cnipa_epub_search.py "短语 含 空格"
  python scripts/disclosure/cnipa_epub_search.py 词甲 词乙 词丙

**必须**至少有一个非空检索词；**不设默认**。

若需将结果页 HTML 保存到磁盘，请改用 ``cnipa_epub_crawler.py``；若只对已有 HTML 文件做解析，
请用 ``cnipa_epub_parse.py``。

环境变量：与 ``cnipa_epub_crawler.py`` 相同（如 ``EPUB_WAF_MAX_WAIT_SEC``、``PLAYWRIGHT_HEADED``）。
"""
from __future__ import annotations

import json
import os
import sys

_MAX_TERMS = 8


def _ensure_utf8_stdio() -> None:
    """在 Windows 等环境下将 stdout/stderr 设为 UTF-8，避免中文 JSON 在终端乱码导致误判检索失败。"""
    for stream in (sys.stdout, sys.stderr):
        try:
            if hasattr(stream, "reconfigure"):
                stream.reconfigure(encoding="utf-8", errors="replace")
        except (OSError, ValueError, TypeError):
            pass


def _terms_from_argv(argv: list[str]) -> list[str]:
    """从所有 argv 片段中按空白拆分（等价 str.split，连续空格视为一次分隔）。"""
    terms: list[str] = []
    for a in argv:
        for part in (a or "").split():
            p = part.strip()
            if p:
                terms.append(p)
    return terms


def _dedupe_hits(hits_lists: list) -> list:
    from cnipa_epub_parse import EpubSearchHit

    seen: set[str] = set()
    out: list[EpubSearchHit] = []
    for hits in hits_lists:
        for h in hits:
            key = h.pub_number or h.link or (h.title or "")[:120]
            if key in seen:
                continue
            seen.add(key)
            out.append(h)
    return out


def _usage() -> None:
    print("usage: python scripts/disclosure/cnipa_epub_search.py <term> [more terms...]", file=sys.stderr)
    print(
        "whitespace splits to multiple terms; one Playwright run per term; merge by pub_number.",
        file=sys.stderr,
    )
    print('example: python scripts/disclosure/cnipa_epub_search.py "batch 调度 异构"', file=sys.stderr)


def main(argv: list[str] | None = None) -> int:
    _ensure_utf8_stdio()
    argv = argv if argv is not None else sys.argv[1:]
    terms = _terms_from_argv(argv)
    if not terms:
        _usage()
        return 2
    if len(terms) > _MAX_TERMS:
        print(
            "ERROR: too many terms after split (%d > %d); shorten or run in batches."
            % (len(terms), _MAX_TERMS),
            file=sys.stderr,
        )
        return 2

    os.environ.setdefault("EPUB_WAF_MAX_WAIT_SEC", "180")

    try:
        import playwright  # noqa: F401
    except ImportError:
        print(
            "ERROR: pip install -r scripts/disclosure/requirements-cnipa.txt && python -m playwright install chromium",
            file=sys.stderr,
        )
        return 1

    from cnipa_epub_crawler import search_epub_keyword
    from cnipa_epub_parse import hits_to_jsonable

    multi = len(terms) > 1
    last_html = ""
    all_batches: list = []

    try:
        for kw in terms:
            html, hits = search_epub_keyword(kw)
            last_html = html
            all_batches.append(hits)
    except Exception as e:
        print("CNIPA_EPUB_ERROR:", e, file=sys.stderr)
        return 1

    if multi:
        hits = _dedupe_hits(all_batches)
        print(
            "EPUB_MERGE: terms=%d merged_hits=%d" % (len(terms), len(hits)),
            file=sys.stderr,
            flush=True,
        )
    else:
        hits = all_batches[0]

    if not hits and last_html and len(last_html) < 20_000:
        if multi:
            print(
                "EPUB_HINT: 0 hits after multi-term run; try broader terms or WebSearch (prior_art_search.md)",
                file=sys.stderr,
                flush=True,
            )
        else:
            print(
                "EPUB_HINT: 0 hits; try more terms (space-separated) or WebSearch",
                file=sys.stderr,
                flush=True,
            )

    print(
        "EPUB_NOTE: html_bytes=%d disk=0" % len(last_html),
        file=sys.stderr,
        flush=True,
    )
    # 仅此一行写入 stdout，供管道/Agent 稳定解析（勿混入多行文本，避免误判未命中）
    print(
        "EPUB_HITS_JSON:",
        json.dumps(hits_to_jsonable(hits), ensure_ascii=False),
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
