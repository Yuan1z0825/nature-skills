#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""No-MCP fallback search for nature-academic-search (OpenAlex, stdlib only).

This is the graceful-degradation path for agents/environments that do not mount
the MCP server (plain CLI use, skill auto-discovery, CI). It mirrors what
`nature-citation/scripts/nature_citation.py` already does for CrossRef: a single
self-contained file hitting a public HTTP API with no third-party dependencies.

Source: OpenAlex (https://openalex.org). Basic queries work without a key, but
since 2026 OpenAlex meters usage per API key (a free key raises the daily budget
10x) and no longer uses the `mailto` polite pool. OpenAlex indexes
CrossRef, PubMed and arXiv-deposited works, so one endpoint covers journals,
preprints and most of the T1/T2/T3 sources for *discovery*. Pair it with
`format-converter.py` to download/convert the chosen DOIs/PMIDs into
.ris/.bib/.enw citation files — together they make the search→export workflow
runnable without MCP.

Usage:
    # By topic
    python3 academic_search.py "deep potential molecular dynamics" [--limit 10] [--year-from 2020] [--sort cited_by_count|relevance_score|publication_date]
    # By author (resolves the name to OpenAlex author IDs, merging same-name/same-institution entries)
    python3 academic_search.py --author "Wanshui Han"
    # By author + topic within that author's works
    python3 academic_search.py "wave load" --author "Wanshui Han" --sort publication_date
    # By author CONSTRAINED to an institution (disambiguates common/romanised names)
    python3 academic_search.py --author "Shenghua Zhou" --affiliation "Hong Kong"
    # List every same-name author cluster, then pick the right institution / ID
    python3 academic_search.py --author "Shenghua Zhou" --list-authors
    # By ORCID (unambiguous, best for common Chinese names)
    python3 academic_search.py --orcid 0000-0002-1825-0097
    # By exact author ID (skip name resolution)
    python3 academic_search.py --author-id A5055881494

API key: create a free key at https://openalex.org and pass --api-key KEY or set
OPENALEX_API_KEY. It is sent as an `Authorization: Bearer` header, so it never
appears in URLs or logs. --mailto / OPENALEX_MAILTO are accepted for backward
compatibility but ignored (OpenAlex retired the polite pool).

Output: JSON list of papers with title, DOI, authors, year, citation count, abstract.
Per-source failures (HTTP 429 rate-limit, timeouts, network errors) are reported
on stderr and exit non-zero, so a caller can treat this source independently and
fall back to another tool.
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.parse
import urllib.error


OPENALEX_API = "https://api.openalex.org/works"
AUTHORS_API = "https://api.openalex.org/authors"
# OpenAlex API key; set from --api-key or OPENALEX_API_KEY in main(). Empty = keyless.
API_KEY = ""

# When re-ranking a query's results by citations/date, drop candidates whose
# relevance_score is below this fraction of the top hit's score. OpenAlex's
# relevance_score carries a citation boost, so a handful of weakly-matching but
# ultra-cited papers (e.g. a 3000-cite medical paper for a civil-engineering query)
# sneak into the pool; without this floor, re-ranking by citations floats them to
# the top. Empirically off-topic papers score ~0.2x the top hit while on-topic ones
# stay above ~0.3x, so 0.3 cleanly separates them.
RELEVANCE_FLOOR = 0.3


def _institution(author: dict) -> str:
    insts = author.get("last_known_institutions") or []
    if isinstance(insts, list) and insts:
        return insts[0].get("display_name", "") or ""
    # Fall back to the most recent listed affiliation if no last-known institution.
    for aff in (author.get("affiliations") or []):
        n = (aff.get("institution") or {}).get("display_name")
        if n:
            return n
    return ""


def _aff_match(author: dict, affiliation: str) -> bool:
    """True if `affiliation` matches the author's PRIMARY (last-known) institution.

    Matching only the last-known institution-rather than every historical
    affiliation-keeps a high-volume namesake with a tenuous past link to the
    target institution from hijacking the result (e.g. a 273-paper radar
    "Shenghua Zhou" who once brushed against "Hong Kong" must not outrank the
    real civil-engineering one whose last-known institution *is* Hong Kong).
    """
    aff = affiliation.lower()
    names = [inst.get("display_name", "") for inst in (author.get("last_known_institutions") or [])]
    if not names:
        names = [_institution(author)]  # fall back to most recent listed affiliation
    return any(aff in (n or "").lower() for n in names)


def _cluster_summary(results: list[dict]) -> list[dict]:
    """Collapse author records into (name, institution) clusters, most-prolific first.

    Lets callers see the *distinct* people behind a colliding name (e.g. a
    medical and a civil-engineering "Shenghua Zhou") instead of silently
    inheriting whichever cluster happens to be largest.
    """
    clusters: dict[tuple, dict] = {}
    for a in results:
        key = ((a.get("display_name") or "").lower(), _institution(a))
        c = clusters.setdefault(key, {
            "name": a.get("display_name", ""),
            "institution": _institution(a),
            "works_count": 0,
            "ids": [],
        })
        c["works_count"] += a.get("works_count") or 0
        c["ids"].append((a.get("id") or "").rsplit("/", 1)[-1])
    return sorted(clusters.values(), key=lambda c: -c["works_count"])


def _get_json(url: str) -> dict:
    """GET an OpenAlex URL, authenticating with the API key when one is set."""
    headers = {"Accept": "application/json"}
    if API_KEY:
        headers["Authorization"] = f"Bearer {API_KEY}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())


def fetch_author_candidates(name: str, per_page: int = 50) -> list[dict]:
    params = {"search": name, "per_page": per_page}
    data = _get_json(f"{AUTHORS_API}?{urllib.parse.urlencode(params)}")
    return data.get("results", [])


def resolve_author(name: str, affiliation: str | None = None) -> dict | None:
    """Resolve an author name to OpenAlex author ID(s).

    OpenAlex often splits one real person into several records, and common
    (e.g. romanised Chinese) names collide across unrelated people. We therefore:
      1. optionally keep only candidates whose affiliation matches `affiliation`
         (case-insensitive substring over the last-known institution); then
      2. pick the most prolific institution-bearing candidate as the anchor; then
      3. merge namesakes that share the anchor's name and institution.
    The returned dict always carries a `candidates` cluster summary so callers
    can detect/repair a wrong pick. When `affiliation` matches nothing, returns
    a dict with empty `ids` and `no_affiliation_match` set (not None).
    """
    results = fetch_author_candidates(name)
    if not results:
        return None

    clusters = _cluster_summary(results)
    pool = results
    if affiliation:
        pool = [a for a in results if _aff_match(a, affiliation)]
        if not pool:
            return {"ids": [], "display_name": name, "institution": "",
                    "works_count": 0, "candidates": clusters,
                    "no_affiliation_match": affiliation}

    # Prefer candidates that have a known institution, then the most prolific.
    pool = sorted(pool, key=lambda a: (_institution(a) == "", -(a.get("works_count") or 0)))
    best = pool[0]
    best_name = (best.get("display_name") or "").lower()
    best_inst = _institution(best)

    ids, works = [], 0
    for a in results:
        if (a.get("display_name") or "").lower() != best_name:
            continue
        # Only merge namesakes that share the institution; if the anchor has
        # no institution we can't disambiguate, so keep that single record.
        if best_inst:
            if _institution(a) != best_inst:
                continue
        elif a is not best:
            continue
        ids.append((a.get("id") or "").rsplit("/", 1)[-1])
        works += a.get("works_count") or 0

    return {
        "ids": ids,
        "display_name": best.get("display_name", ""),
        "institution": best_inst,
        "works_count": works,
        "candidates": clusters,
    }


def resolve_by_orcid(orcid: str) -> dict | None:
    """Resolve an ORCID (bare 0000-... or full URL) to its OpenAlex author ID(s)."""
    oid = orcid.strip().rsplit("/", 1)[-1]
    # 0000-0000-0000-0000 is a checksum-valid but unassigned placeholder some
    # records carry; reject it so it can't resolve to whoever holds that junk tag.
    if set(oid) <= {"0", "-"}:
        return None
    params = {"filter": f"orcid:{oid}"}
    data = _get_json(f"{AUTHORS_API}?{urllib.parse.urlencode(params)}")
    results = data.get("results", [])
    # Defensive: only keep records that actually carry the requested ORCID, so a
    # server-side filter miss can't resolve to an unrelated author. OpenAlex
    # stores orcid as a full URL, e.g. https://orcid.org/0000-....
    results = [a for a in results if (a.get("orcid") or "").rstrip("/").endswith(oid)]
    if not results:
        return None
    best = results[0]
    return {
        "ids": [(a.get("id") or "").rsplit("/", 1)[-1] for a in results],
        "display_name": best.get("display_name", ""),
        "institution": _institution(best),
        "works_count": sum(a.get("works_count") or 0 for a in results),
        "candidates": _cluster_summary(results),
    }


def _normalise_date(value: str) -> str:
    """Coerce a date argument to the YYYY-MM-DD OpenAlex expects.

    Accepts YYYY-MM-DD, YYYY/MM/DD, or a bare YYYY (which OpenAlex treats as
    YYYY-01-01). Raises ValueError on anything else so a malformed argument
    fails loudly instead of silently widening the window.
    """
    text = value.strip().replace("/", "-")
    parts = text.split("-")
    if len(parts) == 1 and len(parts[0]) == 4 and parts[0].isdigit():
        return f"{parts[0]}-01-01"
    if len(parts) == 3 and all(p.isdigit() for p in parts):
        return f"{int(parts[0]):04d}-{int(parts[1]):02d}-{int(parts[2]):02d}"
    raise ValueError(f"Invalid date {value!r}; expected YYYY-MM-DD")


def search(query: str | None = None, limit: int = 10, year_from: int | None = None,
           sort: str = "relevance_score", author_id: str | None = None,
           date_from: str | None = None, date_to: str | None = None) -> list[dict]:
    # A text query is ranked by relevance. Asking OpenAlex to sort that query by
    # cited_by_count / publication_date *server-side* discards relevance entirely
    # and surfaces off-topic mega-cited (or merely newest) papers that only loosely
    # match. So when a query and a non-relevance sort are combined, fetch a larger
    # relevance-ranked candidate pool and re-sort it locally (see end of function),
    # keeping only the topically relevant top results. Without a query (e.g. author
    # browse) there is no relevance to preserve, so sort server-side as before.
    rerank = bool(query) and sort != "relevance_score"
    per_page = min(max(limit * 5, limit), 200) if rerank else min(limit, 50)

    params = {
        "per_page": per_page,
    }
    if query:
        params["search"] = query
    if not rerank:
        if sort != "relevance_score":
            params["sort"] = sort + ":desc"
        elif not query:
            # Author-only browse: relevance is meaningless, default to most-cited.
            params["sort"] = "cited_by_count:desc"

    filters = []
    if year_from:
        filters.append(f"from_publication_date:{year_from}-01-01")
    # Explicit date window (YYYY-MM-DD). OpenAlex filters natively, so a caller
    # that needs "papers published since <date>" gets a correct window instead of
    # a relevance pool that merely happens to contain recent work. An explicit
    # from-date supersedes the coarser year_from.
    if date_from:
        filters = [f for f in filters if not f.startswith("from_publication_date:")]
        filters.append(f"from_publication_date:{_normalise_date(date_from)}")
    if date_to:
        filters.append(f"to_publication_date:{_normalise_date(date_to)}")
    if author_id:
        # Accept a bare ID, a full URL, or an OR-list; normalise each segment.
        ids = "|".join(p.rsplit("/", 1)[-1] for p in author_id.split("|"))
        filters.append(f"author.id:{ids}")
    if filters:
        params["filter"] = ",".join(filters)

    data = _get_json(f"{OPENALEX_API}?{urllib.parse.urlencode(params)}")

    results = []
    for work in data.get("results", []):
        authors = [
            a.get("author", {}).get("display_name", "")
            for a in work.get("authorships", [])
        ]
        doi = work.get("doi", "")
        if doi and doi.startswith("https://doi.org/"):
            doi = doi[len("https://doi.org/"):]

        abstract_index = work.get("abstract_inverted_index")
        abstract = ""
        if abstract_index:
            # Reconstruct abstract from inverted index
            word_positions = []
            for word, positions in abstract_index.items():
                for pos in positions:
                    word_positions.append((pos, word))
            word_positions.sort()
            abstract = " ".join(w for _, w in word_positions)

        results.append({
            "title": work.get("title", ""),
            "doi": doi,
            "authors": authors[:5],  # first 5 authors
            "year": work.get("publication_year"),
            "publication_date": work.get("publication_date", ""),
            "cited_by_count": work.get("cited_by_count", 0),
            # OpenAlex returns source=null for repository deposits / some preprints,
            # so guard with `or {}` instead of relying on .get's default.
            "journal": ((work.get("primary_location") or {}).get("source") or {}).get("display_name", ""),
            "abstract": abstract[:500] if abstract else "",
            "openalex_id": work.get("id", ""),
            # Present only for query searches (server orders by relevance then).
            "relevance_score": work.get("relevance_score"),
        })

    if rerank:
        # Drop weak matches before re-ranking, so an off-topic ultra-cited paper
        # can't float to the top (see RELEVANCE_FLOOR).
        scores = [r["relevance_score"] for r in results if r.get("relevance_score")]
        if scores:
            cutoff = RELEVANCE_FLOOR * max(scores)
            results = [r for r in results if (r.get("relevance_score") or 0) >= cutoff]
        sort_keys = {
            "cited_by_count": lambda r: r.get("cited_by_count") or 0,
            "publication_date": lambda r: r.get("publication_date") or "",
        }
        results.sort(key=sort_keys[sort], reverse=True)

    # We may have over-fetched a candidate pool; return only the requested number.
    return results[:limit]


def main():
    parser = argparse.ArgumentParser(description="No-MCP literature search via OpenAlex")
    parser.add_argument("query", nargs="?", default=None,
                        help="Search query (optional when --author/--author-id/--orcid is given)")
    parser.add_argument("--author", default=None,
                        help="Filter by author name (resolved to OpenAlex author IDs)")
    parser.add_argument("--affiliation", default=None,
                        help="Constrain --author to an institution (case-insensitive substring); "
                             "disambiguates colliding names")
    parser.add_argument("--orcid", default=None,
                        help="Resolve author by ORCID (unambiguous); takes precedence over --author")
    parser.add_argument("--list-authors", action="store_true",
                        help="List same-name author clusters for --author and exit (for disambiguation)")
    parser.add_argument("--author-id", default=None,
                        help="Filter by exact OpenAlex author ID(s), e.g. A5055881494 (OR-join with '|')")
    parser.add_argument("--limit", type=int, default=10, help="Number of results (max 50)")
    parser.add_argument("--year-from", type=int, default=None, help="Filter papers from this year")
    parser.add_argument("--date-from", default=None, metavar="YYYY-MM-DD",
                        help="Only papers published on/after this date (OpenAlex "
                             "from_publication_date). Supersedes --year-from when both are given")
    parser.add_argument("--date-to", default=None, metavar="YYYY-MM-DD",
                        help="Only papers published on/before this date "
                             "(OpenAlex to_publication_date)")
    parser.add_argument("--sort", default="relevance_score",
                        choices=["relevance_score", "cited_by_count", "publication_date"],
                        help="Sort order. With a query, cited_by_count/publication_date "
                             "re-rank within the relevance-matched pool (not the whole DB)")
    parser.add_argument("--api-key", default=None,
                        help="OpenAlex API key (falls back to OPENALEX_API_KEY env); "
                             "sent as a Bearer header")
    parser.add_argument("--mailto", default=None,
                        help="Deprecated and ignored: OpenAlex retired the mailto polite pool")
    parser.add_argument("--compact", action="store_true", help="Compact output (one line per paper)")
    args = parser.parse_args()

    # Resolve the API key: --api-key > OPENALEX_API_KEY. Empty means keyless.
    global API_KEY
    API_KEY = (args.api_key or os.environ.get("OPENALEX_API_KEY") or "").strip()

    if (not args.query and not args.author and not args.author_id
            and not args.orcid and not args.list_authors):
        parser.error("provide a search query, or use --author / --author-id / --orcid")

    def _fmt_cluster(c: dict) -> str:
        return f"  {(c['institution'] or 'unknown institution'):<42} | {c['works_count']:>5} works | {'|'.join(c['ids'])}"

    # --list-authors: dump the distinct same-name clusters and exit.
    if args.list_authors:
        if not args.author:
            parser.error("--list-authors requires --author")
        try:
            cands = _cluster_summary(fetch_author_candidates(args.author))
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError) as e:
            print(f"ERROR: author lookup failed: {e}", file=sys.stderr)
            return 1
        if not cands:
            print(f"ERROR: no author found in OpenAlex: {args.author}", file=sys.stderr)
            return 1
        print(f"Same-name author clusters for \"{args.author}\" (by works count, desc):", file=sys.stderr)
        for c in cands[:15]:
            print(_fmt_cluster(c))
        print("-> use --affiliation \"keyword\" or --author-id <ID> to pin the right person", file=sys.stderr)
        return 0

    author_id = args.author_id
    matched = None
    if not author_id and (args.orcid or args.author):
        try:
            matched = (resolve_by_orcid(args.orcid) if args.orcid
                       else resolve_author(args.author, args.affiliation))
        except urllib.error.HTTPError as e:
            print(f"ERROR: author lookup returned HTTP {e.code}: {e.reason}", file=sys.stderr)
            return 1
        except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError) as e:
            print(f"ERROR: author lookup failed: {e}", file=sys.stderr)
            return 1
        if not matched or not matched.get("ids"):
            if matched and matched.get("no_affiliation_match"):
                print(f"ERROR: author \"{args.author}\" has no record at institution "
                      f"\"{matched['no_affiliation_match']}\". Options (by works count):", file=sys.stderr)
                for c in (matched.get("candidates") or [])[:10]:
                    print(_fmt_cluster(c), file=sys.stderr)
            elif args.orcid:
                print(f"ERROR: no author found in OpenAlex for ORCID: {args.orcid}", file=sys.stderr)
            else:
                print(f"ERROR: no author found in OpenAlex: {args.author}", file=sys.stderr)
            return 1
        author_id = "|".join(matched["ids"])
        inst = matched["institution"] or "unknown institution"
        print(f"Matched author: {matched['display_name']} | {inst} | "
              f"merged {len(matched['ids'])} author record(s), ~{matched['works_count']} works | "
              f"{author_id}", file=sys.stderr)
        # Warn on silent collisions: same name, other institutions present, and the
        # caller didn't pin it down with --affiliation/--orcid.
        if args.author and not args.affiliation and not args.orcid:
            others = [c for c in (matched.get("candidates") or [])
                      if c["institution"] and c["institution"] != matched["institution"]]
            if others:
                tops = "; ".join(f"{c['institution']} ({c['works_count']} works)" for c in others[:3])
                print(f"WARNING: same-name authors at other institutions exist; "
                      f"if this is the wrong one add --affiliation or --orcid: {tops}",
                      file=sys.stderr)

    if args.query and args.sort != "relevance_score":
        print(f"INFO: recalled a relevance-ranked pool first, then re-ranked by {args.sort} "
              f"and kept the top {args.limit} (avoids pulling in off-topic high-cited/newest papers)",
              file=sys.stderr)

    try:
        results = search(args.query, args.limit, args.year_from, args.sort, author_id,
                         date_from=args.date_from, date_to=args.date_to)
    except urllib.error.HTTPError as e:
        if e.code in (401, 403):
            hint = " (API key missing or invalid: set OPENALEX_API_KEY or pass --api-key)"
        elif e.code == 429:
            hint = (" (429 = rate-limited or daily budget used up; retry later, lower --limit, "
                    "or set OPENALEX_API_KEY / --api-key for a 10x larger budget)")
        else:
            hint = ""
        print(f"ERROR: OpenAlex returned HTTP {e.code}: {e.reason}{hint}", file=sys.stderr)
        return 1
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        print(f"ERROR: network request failed (check connectivity): {e}", file=sys.stderr)
        return 1
    except json.JSONDecodeError:
        print("ERROR: OpenAlex returned a non-JSON response (service may be down; retry)", file=sys.stderr)
        return 1

    if args.compact:
        for r in results:
            authors_str = ", ".join(r["authors"][:3])
            if len(r["authors"]) > 3:
                authors_str += " et al."
            print(f"[{r['year']}] {r['title']} | {authors_str} | {r['journal']} | DOI:{r['doi']} | Cited:{r['cited_by_count']}")
    else:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
