#!/usr/bin/env python3
"""Check mechanical consistency across a LaTeX revision package."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


DEFAULT_QUOTE_MACROS = ("RevisedExcerpt", "revtext", "oldtext")
MARKUP_MACROS = ("revised", "added", "changed")
DELETION_MACROS = ("deletedtext", "deleted")
INPUT_PATTERN = re.compile(r"\\(?:input|include)\s*\{([^{}]+)\}")


@dataclass(frozen=True)
class Finding:
    code: str
    message: str
    source: str


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def read_latex_project(path: Path, ancestors: tuple[Path, ...] = ()) -> str:
    """Read a LaTeX root file and expand existing static input/include files."""
    path = path.resolve()
    if path in ancestors:
        chain = " -> ".join(str(item) for item in (*ancestors, path))
        raise ValueError(f"cyclic LaTeX include detected: {chain}")

    text = strip_comments(read_text(path))

    def expand(match: re.Match[str]) -> str:
        raw_target = match.group(1).strip()
        if not raw_target or "\\" in raw_target:
            return match.group(0)
        target = Path(raw_target)
        if not target.suffix:
            target = target.with_suffix(".tex")
        if not target.is_absolute():
            target = path.parent / target
        if not target.is_file():
            return match.group(0)
        return read_latex_project(target, (*ancestors, path))

    return INPUT_PATTERN.sub(expand, text)


def matching_brace(text: str, opening: int) -> int | None:
    depth = 0
    escaped = False
    for index in range(opening, len(text)):
        char = text[index]
        if escaped:
            escaped = False
            continue
        if char == "\\":
            escaped = True
            continue
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return index
    return None


def extract_macro_arguments(text: str, macro_names: Iterable[str]) -> list[tuple[str, str]]:
    names = tuple(dict.fromkeys(macro_names))
    if not names:
        return []
    pattern = re.compile(r"\\(" + "|".join(re.escape(name) for name in names) + r")\s*\{")
    results: list[tuple[str, str]] = []
    for match in pattern.finditer(text):
        opening = match.end() - 1
        closing = matching_brace(text, opening)
        if closing is not None:
            results.append((match.group(1), text[opening + 1 : closing]))
    return results


def unwrap_single_argument_macros(text: str, macro_names: Iterable[str]) -> str:
    names = tuple(dict.fromkeys(macro_names))
    if not names:
        return text
    pattern = re.compile(r"\\(" + "|".join(re.escape(name) for name in names) + r")\s*\{")
    while True:
        match = pattern.search(text)
        if not match:
            return text
        opening = match.end() - 1
        closing = matching_brace(text, opening)
        if closing is None:
            return text
        text = text[: match.start()] + text[opening + 1 : closing] + text[closing + 1 :]


def remove_single_argument_macros(text: str, macro_names: Iterable[str]) -> str:
    names = tuple(dict.fromkeys(macro_names))
    if not names:
        return text
    pattern = re.compile(r"\\(" + "|".join(re.escape(name) for name in names) + r")\s*\{")
    while True:
        match = pattern.search(text)
        if not match:
            return text
        opening = match.end() - 1
        closing = matching_brace(text, opening)
        if closing is None:
            return text
        text = text[: match.start()] + text[closing + 1 :]


def strip_comments(text: str) -> str:
    return re.sub(r"(?<!\\)%.*$", "", text, flags=re.MULTILINE)


def strip_revision_markup(text: str) -> str:
    text = remove_single_argument_macros(text, DELETION_MACROS)
    text = unwrap_single_argument_macros(text, MARKUP_MACROS)
    text = re.sub(r"\\color\s*\{[^{}]*\}", "", text)
    text = re.sub(r"\\textcolor\s*\{[^{}]*\}\s*\{([^{}]*)\}", r"\1", text)
    return text


def normalize_latex(text: str) -> str:
    text = strip_comments(text)
    text = strip_revision_markup(text)
    replacements = {
        r"\%": "%",
        r"\&": "&",
        r"\_": "_",
        r"\#": "#",
        "~": " ",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    text = re.sub(r"\\(?:label|ref|pageref|cite|citep|citet)\s*\{[^{}]*\}", " ", text)
    text = re.sub(r"\\[A-Za-z@]+\*?(?:\[[^\]]*\])?", " ", text)
    text = text.replace("{", " ").replace("}", " ")
    return " ".join(text.split())


def check_quotes(
    manuscript_text: str,
    response_text: str,
    response_name: str,
    quote_macros: Iterable[str],
    minimum_quote_length: int,
) -> list[Finding]:
    manuscript = normalize_latex(manuscript_text)
    findings: list[Finding] = []
    for index, (macro, raw_quote) in enumerate(
        extract_macro_arguments(response_text, quote_macros), 1
    ):
        quote = normalize_latex(raw_quote)
        if len(quote) < minimum_quote_length:
            continue
        if quote not in manuscript:
            preview = quote[:120] + ("..." if len(quote) > 120 else "")
            findings.append(
                Finding(
                    code="QUOTE_NOT_IN_MANUSCRIPT",
                    message=f"{macro} quote {index} is not verbatim in the manuscript: {preview}",
                    source=response_name,
                )
            )
    return findings


def check_response_counts(response_text: str, response_name: str) -> list[Finding]:
    comments = len(extract_macro_arguments(response_text, ("ReviewerComment",)))
    responses = len(extract_macro_arguments(response_text, ("AuthorResponse",)))
    if comments == responses:
        return []
    return [
        Finding(
            code="COMMENT_RESPONSE_COUNT_MISMATCH",
            message=f"reviewer comments={comments}, author responses={responses}",
            source=response_name,
        )
    ]


def check_clean_marked(
    clean_text: str,
    marked_text: str,
    clean_name: str,
    marked_name: str,
) -> list[Finding]:
    clean = normalize_latex(clean_text)
    marked = normalize_latex(marked_text)
    if clean == marked:
        return []
    return [
        Finding(
            code="CLEAN_MARKED_TEXT_MISMATCH",
            message="clean and marked manuscripts differ after revision markup is removed",
            source=f"{clean_name} <-> {marked_name}",
        )
    ]


def run_checks(
    manuscript: Path,
    response: Path,
    clean: Path | None = None,
    marked: Path | None = None,
    quote_macros: Iterable[str] = DEFAULT_QUOTE_MACROS,
    minimum_quote_length: int = 40,
    substitutions: Iterable[tuple[str, str]] = (),
) -> list[Finding]:
    manuscript_text = read_latex_project(manuscript)
    response_text = read_latex_project(response)
    for source, rendered in substitutions:
        manuscript_text = manuscript_text.replace(source, rendered)
    findings = check_quotes(
        manuscript_text,
        response_text,
        str(response),
        quote_macros,
        minimum_quote_length,
    )
    findings.extend(check_response_counts(response_text, str(response)))
    if clean is not None and marked is not None:
        findings.extend(
            check_clean_marked(
                read_latex_project(clean),
                read_latex_project(marked),
                str(clean),
                str(marked),
            )
        )
    return findings


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Check LaTeX response quotes, response counts, and clean/marked equivalence."
    )
    parser.add_argument("--manuscript", type=Path, required=True)
    parser.add_argument("--response", type=Path, required=True)
    parser.add_argument("--clean", type=Path)
    parser.add_argument("--marked", type=Path)
    parser.add_argument(
        "--quote-macro",
        action="append",
        dest="quote_macros",
        help="LaTeX macro whose braced argument is a manuscript quote. Repeat as needed.",
    )
    parser.add_argument("--minimum-quote-length", type=int, default=40)
    parser.add_argument(
        "--substitution",
        action="append",
        default=[],
        metavar="SOURCE=RENDERED",
        help=(
            "Declare a deliberate source-to-rendered substitution used in a response quote, "
            "for example 'Table \\ref{tab:main}=Table 1'. Repeat as needed."
        ),
    )
    parser.add_argument("--json", action="store_true", dest="as_json")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if (args.clean is None) != (args.marked is None):
        parser.error("--clean and --marked must be supplied together")
    if args.minimum_quote_length < 1:
        parser.error("--minimum-quote-length must be positive")

    substitutions: list[tuple[str, str]] = []
    for raw in args.substitution:
        source, separator, rendered = raw.partition("=")
        if not separator or not source or not rendered:
            parser.error("--substitution must use non-empty SOURCE=RENDERED syntax")
        substitutions.append((source, rendered))

    findings = run_checks(
        manuscript=args.manuscript,
        response=args.response,
        clean=args.clean,
        marked=args.marked,
        quote_macros=args.quote_macros or DEFAULT_QUOTE_MACROS,
        minimum_quote_length=args.minimum_quote_length,
        substitutions=substitutions,
    )
    if args.as_json:
        print(json.dumps([asdict(item) for item in findings], ensure_ascii=False, indent=2))
    elif findings:
        for item in findings:
            print(f"{item.code}\t{item.source}\t{item.message}")
    else:
        print("Package consistency checks passed.")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
