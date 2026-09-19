# -*- coding: utf-8 -*-
"""
Multi-source citation downloader with format conversion.
Sources: PubMed (NCBI E-utilities), CrossRef (REST API), arXiv (Atom API).
Outputs: .nbib (PubMed only), .ris, .bib, .enw.

Usage:
  python format-converter.py --pmid 28344011
  python format-converter.py --pmid 28344011,10645439 --format ris
  python format-converter.py --doi 10.1038/nature14539 --format bib
  python format-converter.py --arxiv 1706.03762 --format ris
  python format-converter.py --query "TB-Profiler AND Bioinformatics[Journal]"
  python format-converter.py --input refs.txt
  python format-converter.py --input refs.txt --format ris
  python format-converter.py --interactive

refs.txt format:
  PMID:28344011
  DOI:10.1038/nature14539
  ARXIV:1706.03762
  QUERY:TB-Profiler AND Bioinformatics[Journal]
  AUTHOR:Dheda TITLE:drug-resistant tuberculosis
  # Lines starting with # are comments
"""

import os
import sys
import time
import json
import argparse
import defusedxml.ElementTree as ET
import requests
from urllib.parse import urlencode

from converters import (
    convert_from_medline,
    convert_from_crossref,
    convert_from_arxiv,
    get_extension,
)

EUTILS_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
CROSSREF_BASE = "https://api.crossref.org/works"
ARXIV_BASE = "https://export.arxiv.org/api/query"
DELAY = 0.5


# ── PubMed ──────────────────────────────────────────────────────

def esearch(query, max_results=5):
    params = {"db": "pubmed", "term": query, "retmax": max_results, "retmode": "xml"}
    url = f"{EUTILS_BASE}/esearch.fcgi?{urlencode(params)}"
    try:
        resp = requests.get(url, timeout=30)
        xml_data = resp.text
        root = ET.fromstring(xml_data)
        id_list = root.find("IdList")
        if id_list is not None:
            return [e.text for e in id_list.findall("Id")]
        return []
    except Exception as e:
        print(f"  ESearch error: {e}")
        return []


def efetch_medline(pmid, retries=1):
    params = {"db": "pubmed", "id": pmid, "rettype": "medline", "retmode": "text"}
    url = f"{EUTILS_BASE}/efetch.fcgi?{urlencode(params)}"
    for attempt in range(retries):
        try:
            with urlopen(url, timeout=30) as resp:
                return resp.read().decode("utf-8")
        except Exception as e:
            if attempt == retries - 1:
                print(f"  EFetch error for PMID {pmid}: {e}")
                return None
            time.sleep(DELAY * (attempt + 1))


def download_pubmed(pmid, output_dir, fmt, retries=1):
    """Download citation by PMID. Returns (success, filename_or_error)."""
    pmid = pmid.strip()
    if not pmid:
        return False, "Empty PMID"

    print(f"  Downloading PMID: {pmid}")
    time.sleep(DELAY)
    nbib_text = efetch_medline(pmid, retries=retries)

    if not nbib_text or not nbib_text.strip():
        return False, f"PMID {pmid} not found or empty response"

    content = convert_from_medline(nbib_text, fmt)
    ext = get_extension(fmt)
    filename = f"pubmed-{pmid}{ext}"
    filepath = os.path.join(output_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    # Extract title for display
    for line in nbib_text.split("\n"):
        if line.startswith("TI  -"):
            print(f"  Title: {line[5:].strip()[:100]}")
            break

    print(f"  Saved: {filename} (format: {fmt})")
    return True, filename


def search_pubmed(query, output_dir, fmt, retries=1):
    print(f"  Searching: {query[:80]}...")
    time.sleep(DELAY)
    pmids = esearch(query)
    if not pmids:
        return False, f"No results for query: {query[:60]}"
    pmid = pmids[0]
    print(f"  Found PMID: {pmid}")
    return download_pubmed(pmid, output_dir, fmt, retries=retries)


# ── CrossRef ────────────────────────────────────────────────────

def download_crossref(doi, output_dir, fmt, retries=1):
    """Download citation by DOI from CrossRef. Returns (success, filename_or_error)."""
    doi = doi.strip()
    if not doi:
        return False, "Empty DOI"

    print(f"  Downloading DOI: {doi}")
    time.sleep(DELAY)
    url = f"{CROSSREF_BASE}/{doi}"
    for attempt in range(retries):
        try:
            with urlopen(url, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            break
        except Exception as e:
            if attempt == retries - 1:
                return False, f"CrossRef API error for DOI {doi}: {e}"
            time.sleep(DELAY * (attempt + 1))

    content = convert_from_crossref(data, fmt)
    ext = get_extension(fmt)
    safe_doi = doi.replace("/", "_").replace(".", "_")[:60]
    filename = f"crossref-{safe_doi}{ext}"
    filepath = os.path.join(output_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    msg = data.get("message", data)
    title = msg.get("title", [])
    if title:
        print(f"  Title: {title[0][:100]}")

    print(f"  Saved: {filename} (format: {fmt})")
    return True, filename


# ── arXiv ───────────────────────────────────────────────────────

def download_arxiv(arxiv_id, output_dir, fmt, retries=1):
    """Download citation by arXiv ID. Returns (success, filename_or_error)."""
    arxiv_id = arxiv_id.strip()
    if not arxiv_id:
        return False, "Empty arXiv ID"

    print(f"  Downloading arXiv: {arxiv_id}")
    time.sleep(DELAY)
    params = {"id_list": arxiv_id, "max_results": 1}
    url = f"{ARXIV_BASE}?{urlencode(params)}"
    for attempt in range(retries):
        try:
            with urlopen(url, timeout=30) as resp:
                xml_data = resp.read().decode("utf-8")
            break
        except Exception as e:
            if attempt == retries - 1:
                return False, f"arXiv API error for ID {arxiv_id}: {e}"
            time.sleep(DELAY * (attempt + 1))

    root = ET.fromstring(xml_data)
    content = convert_from_arxiv(root, fmt)
    if not content:
        return False, f"arXiv ID {arxiv_id}: no entry found in response"

    ext = get_extension(fmt)
    safe_id = arxiv_id.replace("/", "_")[:60]
    filename = f"arxiv-{safe_id}{ext}"
    filepath = os.path.join(output_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"  Saved: {filename} (format: {fmt})")
    return True, filename


# ── Input parsing ───────────────────────────────────────────────

def parse_input_line(line):
    """Parse a single input line into (type, value)."""
    line = line.strip()
    if not line or line.startswith("#"):
        return None, None

    upper = line.upper()
    if upper.startswith("PMID:"):
        return "pmid", line[5:].strip()
    if upper.startswith("DOI:"):
        return "doi", line[4:].strip()
    if upper.startswith("ARXIV:"):
        return "arxiv", line[6:].strip()
    if upper.startswith("QUERY:"):
        return "query", line[6:].strip()
    if upper.startswith("AUTHOR:"):
        parts = line.split("TITLE:", 1)
        author = parts[0][7:].strip()
        title = parts[1].strip() if len(parts) > 1 else ""
        return "author_title", (author, title)

    # Default: free-text search query
    return "query", line


def process_entry(entry_type, value, output_dir, fmt, retries=1):
    if entry_type == "pmid":
        return download_pubmed(value, output_dir, fmt, retries=retries)
    elif entry_type == "doi":
        return download_crossref(value, output_dir, fmt, retries=retries)
    elif entry_type == "arxiv":
        return download_arxiv(value, output_dir, fmt, retries=retries)
    elif entry_type == "author_title":
        author, title = value
        query_parts = []
        if author:
            query_parts.append(f"{author}[Author]")
        if title:
            query_parts.append(f"{title}[Title]")
        query = " AND ".join(query_parts) if query_parts else ""
        if not query:
            return False, "Empty author and title"
        return search_pubmed(query, output_dir, fmt, retries=retries)
    elif entry_type == "query":
        return search_pubmed(value, output_dir, fmt, retries=retries)
    return False, f"Unknown entry type: {entry_type}"


def process_file(input_file, output_dir, fmt, retries=1):
    if not os.path.exists(input_file):
        print(f"Error: Input file not found: {input_file}")
        return 0, 0, [f"File not found: {input_file}"]

    with open(input_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    success, failed, errors = 0, 0, []
    for i, line in enumerate(lines, 1):
        entry_type, value = parse_input_line(line)
        if entry_type is None:
            continue
        print(f"\n[Line {i}] Processing: {line.strip()[:60]}")
        ok, result = process_entry(entry_type, value, output_dir, fmt, retries=retries)
        if ok:
            success += 1
        else:
            failed += 1
            errors.append(f"Line {i}: {result}")
    return success, failed, errors


def interactive_mode(output_dir, fmt, retries=1):
    print(f"Interactive mode (format: {fmt}) - enter references (one per line, empty line to finish):")
    print("Formats: PMID:12345 | DOI:10.xxx | ARXIV:2301.xxx | AUTHOR:Name TITLE:keywords | QUERY:...")
    print("-" * 60)

    success, failed, errors = 0, 0, []
    while True:
        try:
            line = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not line:
            break
        entry_type, value = parse_input_line(line)
        if entry_type is None:
            continue
        ok, result = process_entry(entry_type, value, output_dir, fmt, retries=retries)
        if ok:
            success += 1
        else:
            failed += 1
            errors.append(result)
    return success, failed, errors


# ── Main ────────────────────────────────────────────────────────

def self_test():
    """Run self-check on format converter pipeline."""
    print("FORMAT CONVERTER SELF-TEST")
    print("-" * 40)

    # 1. Module import check
    try:
        from converters import convert_from_medline, convert_from_crossref, convert_from_arxiv
        print("  [OK] Module imports")
    except Exception as e:
        print(f"  [FAIL] Module imports: {e}")
        return

    # 2. PubMed endpoint (known PMID: 28344011)
    pmid = "28344011"
    print(f"  Testing PubMed (PMID {pmid})...")
    try:
        import time
        time.sleep(0.5)
        nbib_text = efetch_medline(pmid)
        if nbib_text and nbib_text.strip():
            ris_content = convert_from_medline(nbib_text, "ris")
            bib_content = convert_from_medline(nbib_text, "bib")
            enw_content = convert_from_medline(nbib_text, "enw")
            if ris_content.strip() and bib_content.strip() and enw_content.strip():
                print(f"  [OK] PubMed endpoint (RIS: {len(ris_content)}B, BibTeX: {len(bib_content)}B, ENW: {len(enw_content)}B)")
            else:
                print(f"  [FAIL] PubMed conversion produced empty output")
        else:
            print(f"  [FAIL] PubMed returned empty response for PMID {pmid}")
    except Exception as e:
        print(f"  [FAIL] PubMed endpoint: {e}")

    # 3. CrossRef endpoint (known DOI)
    doi = "10.1038/nature14539"
    print(f"  Testing CrossRef (DOI {doi})...")
    try:
        from urllib.request import urlopen
        import json
        time.sleep(0.5)
        url = f"https://api.crossref.org/works/{doi}"
        with urlopen(url, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        ris_content = convert_from_crossref(data, "ris")
        bib_content = convert_from_crossref(data, "bib")
        enw_content = convert_from_crossref(data, "enw")
        if ris_content.strip() and bib_content.strip() and enw_content.strip():
            print(f"  [OK] CrossRef endpoint (RIS: {len(ris_content)}B, BibTeX: {len(bib_content)}B, ENW: {len(enw_content)}B)")
        else:
            print(f"  [FAIL] CrossRef conversion produced empty output")
    except Exception as e:
        print(f"  [FAIL] CrossRef endpoint: {e}")

    print("-" * 40)
    print("Self-test complete.")


def main():
    parser = argparse.ArgumentParser(
        description="Multi-source citation downloader with format conversion (.nbib/.ris/.bib)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --pmid 28344011
  %(prog)s --pmid 28344011,10645439 --format ris
  %(prog)s --doi 10.1038/nature14539 --format bib
  %(prog)s --doi 10.1038/nature14539,10.1038/s41586-020-2649-2 --format ris
  %(prog)s --arxiv 1706.03762 --format bib
  %(prog)s --arxiv 1706.03762,2302.13971 --format ris
  %(prog)s --query "TB-Profiler AND Bioinformatics[Journal]"
  %(prog)s --input refs.txt
  %(prog)s --input refs.txt --format ris
  %(prog)s --interactive

refs.txt format:
  PMID:28344011
  DOI:10.1038/nature14539
  ARXIV:1706.03762
  QUERY:TB-Profiler AND Bioinformatics[Journal]
  AUTHOR:Dheda TITLE:drug-resistant tuberculosis
  # Lines starting with # are comments
        """,
    )
    parser.add_argument("--pmid", help="PMID(s), comma-separated")
    parser.add_argument("--doi", help="DOI(s), comma-separated")
    parser.add_argument("--arxiv", help="arXiv ID(s), comma-separated")
    parser.add_argument("--author", help="Author name for PubMed search")
    parser.add_argument("--title", help="Title keywords for PubMed search")
    parser.add_argument("--query", help="PubMed search query")
    parser.add_argument("--input", help="Input file with references")
    parser.add_argument("--interactive", action="store_true", help="Interactive mode")
    parser.add_argument(
        "--format", choices=["nbib", "ris", "bib", "enw"], default="nbib",
        help="Output format: nbib (default, MEDLINE), ris (EndNote/Zotero), bib (BibTeX/LaTeX), enw (EndNote tagged)",
    )
    parser.add_argument(
        "--output", default="./references/",
        help="Output directory (default: ./references/)",
    )
    parser.add_argument("--version", action="version", version="format-converter 1.0.0")
    parser.add_argument("--test", action="store_true", help="Run self-test on format converter pipeline")
    parser.add_argument("--retry", type=int, default=1, help="Retry count for HTTP calls")
    parser.add_argument("--preflight", action="store_true", help="Run connectivity check on API endpoints")

    args = parser.parse_args()

    if args.test:
        self_test()
        return

    if args.preflight:
        import sys as _sys
        _sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from preflight import check_endpoints
        results = check_endpoints()
        # Print report
        print("PRE-FLIGHT REPORT")
        all_ok = True
        for name, info in results.items():
            status = "OK" if info["ok"] else "FAIL"
            detail = f"({info['time']:.1f}s)" if info["ok"] else f"({info['error']})"
            print(f"  {name:25s}: {status} {detail}")
            if not info["ok"]:
                all_ok = False
        reachable = sum(1 for v in results.values() if v["ok"])
        total = len(results)
        print(f"  {reachable}/{total} endpoints reachable.")
        if not all_ok:
            print("  Affected: format-converter downloads for unreachable endpoints (MCP tools unaffected).")
            _sys.exit(1)
        return

    if not any([args.pmid, args.doi, args.arxiv, args.author, args.query, args.input, args.interactive]):
        parser.error("Specify at least one input method")

    fmt = args.format
    output_dir = os.path.abspath(args.output)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")

    print(f"Output directory: {output_dir}")
    print(f"Format: {fmt}")
    print("=" * 60)

    total_success, total_failed, all_errors = 0, 0, []

    def handle_list(ids_str, handler, retries=1):
        nonlocal total_success, total_failed
        ids = [x.strip() for x in ids_str.split(",") if x.strip()]
        for item_id in ids:
            print(f"\nProcessing: {item_id}")
            ok, result = handler(item_id, output_dir, fmt, retries=retries)
            if ok:
                total_success += 1
            else:
                total_failed += 1
                all_errors.append(result)

    # --pmid
    if args.pmid:
        handle_list(args.pmid, download_pubmed, retries=args.retry)

    # --doi
    if args.doi:
        if fmt == "nbib":
            print("Warning: CrossRef does not provide .nbib (MEDLINE) format. Falling back to .ris")
            fmt = "ris"
        handle_list(args.doi, download_crossref, retries=args.retry)

    # --arxiv
    if args.arxiv:
        if fmt == "nbib":
            print("Warning: arXiv does not provide .nbib (MEDLINE) format. Falling back to .ris")
            fmt = "ris"
        handle_list(args.arxiv, download_arxiv, retries=args.retry)

    # --author / --title / --query
    if args.author or args.title or args.query:
        if args.query:
            query = args.query
        else:
            query_parts = []
            if args.author:
                query_parts.append(f"{args.author}[Author]")
            if args.title:
                query_parts.append(f"{args.title}[Title]")
            query = " AND ".join(query_parts)
        print(f"\nProcessing search: {query}")
        ok, result = search_pubmed(query, output_dir, fmt, retries=args.retry)
        if ok:
            total_success += 1
        else:
            total_failed += 1
            all_errors.append(result)

    # --input
    if args.input:
        print(f"\nProcessing file: {args.input}")
        s, f, e = process_file(args.input, output_dir, fmt, retries=args.retry)
        total_success += s
        total_failed += f
        all_errors.extend(e)

    # --interactive
    if args.interactive:
        s, f, e = interactive_mode(output_dir, fmt, retries=args.retry)
        total_success += s
        total_failed += f
        all_errors.extend(e)

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print(f"  Success: {total_success}")
    print(f"  Failed:  {total_failed}")
    if all_errors:
        print("  Errors:")
        for err in all_errors:
            print(f"    - {err}")
    print(f"  Output:  {output_dir}")
    print("=" * 60)


if __name__ == "__main__":
    main()
