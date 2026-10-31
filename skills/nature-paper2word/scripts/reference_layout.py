#!/usr/bin/env python3
"""Map explicitly selected reference paragraphs to md-to-word format rules.

Run with the Python environment containing md-to-word-docx. Paragraph and run
indices are zero-based and come from ``inspect``; no semantic role is guessed.
"""
from __future__ import annotations

import argparse
import json
from copy import deepcopy
from pathlib import Path

from lxml import etree
from md_to_word.spec.constants import STYLE_CN, STYLE_MAP
from md_to_word.template.extractor import Ref, _build_draft, clauses_for, q


def paragraphs(ref):
    root = etree.fromstring(ref.parts["word/document.xml"])
    return root.findall(f'.//{q("body")}//{q("p")}')


def text(node):
    return "".join(node.itertext(q("t")))


def style_id(properties, tag):
    item = properties.find(q(tag)) if properties is not None else None
    return item.get(q("val"), "") if item is not None else ""


def default_style(ref):
    return next((sid for sid, node in ref.by_id.items()
                 if node.get(q("type")) == "paragraph"
                 and node.get(q("default")) in {"1", "true"}), "")


def style_chain(ref, sid):
    """Normalize every basedOn hop, including custom mixed-case style IDs."""
    chain, seen = [], set()
    while sid:
        sid = sid.replace(" ", "").lower()
        if sid in seen or sid not in ref.by_id:
            break
        seen.add(sid)
        node = ref.by_id[sid]
        chain.append(node)
        sid = style_id(node, "basedOn")
    return chain


def inspect_reference(source):
    ref = Ref(source)
    names = {sid: (node.find(q("name")).get(q("val"))
                   if node.find(q("name")) is not None else sid)
             for sid, node in ref.by_id.items()}
    samples = []
    for index, paragraph in enumerate(paragraphs(ref)):
        sid = style_id(paragraph.find(q("pPr")), "pStyle") or default_style(ref)
        runs = [{"run": i, "text": text(run),
                 "style": style_id(run.find(q("rPr")), "rStyle")}
                for i, run in enumerate(paragraph.iter(q("r")))]
        samples.append({"paragraph": index, "text": text(paragraph), "style": sid,
                        "style_name": names.get(sid.replace(" ", "").lower(), sid),
                        "in_table": any(a.tag == q("tc") for a in paragraph.iterancestors()),
                        "runs": runs})
    return {"source": str(source.resolve()), "index_base": 0,
            "roles": sorted(STYLE_MAP), "paragraphs": samples}


def merge_properties(target, source):
    """Overlay individual OOXML attributes, retaining inherited sibling values."""
    if source is None:
        return
    # An explicit font name supersedes a theme reference for that slot.
    groups = {q("rFonts"): [("ascii", "asciiTheme"), ("hAnsi", "hAnsiTheme"),
                             ("eastAsia", "eastAsiaTheme"), ("cs", "cstheme")],
              q("spacing"): [("before", "beforeLines"), ("after", "afterLines")],
              q("ind"): [("firstLine", "firstLineChars", "hanging", "hangingChars"),
                          ("left", "leftChars"), ("right", "rightChars")]}
    for group in groups.get(source.tag, []):
        if any(q(key) in source.attrib for key in group):
            for key in group:
                target.attrib.pop(q(key), None)
    target.attrib.update(source.attrib)
    for item in source:
        existing = target.find(item.tag)
        if existing is None:
            target.append(deepcopy(item))
        elif item.tag == q("tabs"):
            target.replace(existing, deepcopy(item))
        else:
            # Toggle properties may use an empty element to mean enabled.
            if item.tag in {q("b"), q("i")}:
                existing.attrib.clear()
            merge_properties(existing, item)


def sample_style(ref, paragraph, run):
    synthetic = etree.Element(q("style"))
    ppr, rpr = etree.SubElement(synthetic, q("pPr")), etree.SubElement(synthetic, q("rPr"))
    defaults = ref.doc_defaults
    if defaults is not None:
        merge_properties(ppr, defaults.find(f'{q("pPrDefault")}/{q("pPr")}'))
        merge_properties(rpr, defaults.find(f'{q("rPrDefault")}/{q("rPr")}'))
    direct_p = paragraph.find(q("pPr"))
    sid = style_id(direct_p, "pStyle") or default_style(ref)
    for node in reversed(style_chain(ref, sid)):
        merge_properties(ppr, node.find(q("pPr")))
        merge_properties(rpr, node.find(q("rPr")))
    merge_properties(ppr, direct_p)
    direct_r = run.find(q("rPr"))
    for node in reversed(style_chain(ref, style_id(direct_r, "rStyle"))):
        merge_properties(rpr, node.find(q("rPr")))
    merge_properties(rpr, direct_r)
    return synthetic


def build_reference(source, mapping):
    ref = Ref(source)
    blocks = paragraphs(ref)
    selected = []
    if not isinstance(mapping, dict) or not mapping:
        raise ValueError("Role map must be a nonempty object")
    for role, sample in mapping.items():
        if role not in STYLE_MAP:
            raise ValueError(f"Use a supported role from inspect: {role}")
        role = STYLE_CN[STYLE_MAP[role]]
        pi, ri = sample["paragraph"], sample["run"]
        if type(pi) is not int or type(ri) is not int or pi < 0 or ri < 0:
            raise ValueError(f"{role}: indices must be nonnegative integers")
        if pi >= len(blocks):
            raise ValueError(f"{role}: paragraph index out of range")
        runs = list(blocks[pi].iter(q("r")))
        if ri >= len(runs) or not text(runs[ri]).strip():
            raise ValueError(f"{role}: select an existing run containing sample text")
        sid = STYLE_MAP[role].replace(" ", "").lower()
        # A private entry leaves the original reference style chains intact.
        synthetic_id = "_sample_" + sid
        ref.by_id[synthetic_id] = sample_style(ref, blocks[pi], runs[ri])
        if sid in ref.base_borders:
            ref.base_borders.add(synthetic_id)
        clauses, notes, _ = clauses_for(ref, synthetic_id)
        selected.append((role, pi, ri, sid, synthetic_id, clauses, notes))
    # Resolve every sample against the original styles before replacing entries.
    for _, _, _, sid, synthetic_id, _, _ in selected:
        ref.by_id[sid] = ref.by_id[synthetic_id]
    draft, _, _ = _build_draft(ref, "zh")
    lines, additions, doubts = draft.splitlines(), [], []
    for role, pi, ri, _, _, clauses, notes in selected:
        aliases = {name for name, word in STYLE_MAP.items() if word == STYLE_MAP[role]}
        lines = [line for line in lines
                 if line.split("：", 1)[0] not in aliases
                 and not any(line.startswith(f"# {name}：") for name in aliases)]
        additions += [f"# {role} 来源: {source.name}; paragraph={pi}; run={ri}",
                      f"{role}：" + " ".join(clauses)]
        doubts += [f"# {role}：{note}" for note in notes]
    # Mapped rules precede the remaining engine-generated review notes.
    split = next((i for i, line in enumerate(lines) if line.startswith("# ──")), len(lines))
    lines[split:split] = additions + [""]
    if doubts:
        lines += ["", "# ── 映射样本需确认 ──"] + doubts
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for command in ("inspect", "build"):
        sub = commands.add_parser(command)
        sub.add_argument("reference", type=Path)
        sub.add_argument("-o", "--output", type=Path, required=True)
        if command == "build":
            sub.add_argument("--map", dest="mapping", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "inspect":
            result = json.dumps(inspect_reference(args.reference), ensure_ascii=False, indent=2) + "\n"
        else:
            mapping = json.loads(args.mapping.read_text(encoding="utf-8-sig"))
            result = build_reference(args.reference, mapping)
        if args.output.resolve() == args.reference.resolve():
            raise ValueError("Output must differ from the reference document")
        args.output.write_text(result, encoding="utf-8")
    except (ValueError, OSError, KeyError, etree.XMLSyntaxError) as exc:
        parser.exit(1, f"reference_layout: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
