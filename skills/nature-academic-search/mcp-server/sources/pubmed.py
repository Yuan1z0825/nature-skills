"""PubMed data source via NCBI E-utilities API."""

from __future__ import annotations

import re
import time
from typing import Any

import defusedxml.ElementTree as ET

import requests

from utils.config import get_config
from utils.errors import DataSourceError
from utils.logging import setup_logging

logger = setup_logging()

BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
SOURCE_NAME = "pubmed"

# Rate limit: 3 req/s without key, 10 req/s with key
_REQ_INTERVAL_WITH_KEY = 0.11
_REQ_INTERVAL_WITHOUT_KEY = 0.35

_last_request_ts: float = 0.0


def _throttle(api_key: str) -> None:
    """Enforce NCBI rate limits."""
    global _last_request_ts
    interval = _REQ_INTERVAL_WITH_KEY if api_key else _REQ_INTERVAL_WITHOUT_KEY
    elapsed = time.monotonic() - _last_request_ts
    if elapsed < interval:
        time.sleep(interval - elapsed)
    _last_request_ts = time.monotonic()


def _get(endpoint: str, params: dict[str, Any], timeout: int = 30) -> requests.Response:
    """Send GET request to NCBI E-utilities with throttling and error handling."""
    cfg = get_config()
    api_key = cfg.pubmed_api_key

    _throttle(api_key)

    merged = dict(params)
    if cfg.pubmed_email:
        merged["email"] = cfg.pubmed_email
    if api_key:
        merged["api_key"] = api_key

    url = BASE_URL + endpoint
    try:
        resp = requests.get(url, params=merged, timeout=timeout)
        resp.raise_for_status()
    except requests.Timeout as exc:
        raise DataSourceError(SOURCE_NAME, f"Request timed out: {url}", exc) from exc
    except requests.HTTPError as exc:
        status = exc.response.status_code if exc.response is not None else "?"
        raise DataSourceError(
            SOURCE_NAME, f"HTTP {status} from {url}", exc
        ) from exc
    except requests.RequestException as exc:
        raise DataSourceError(SOURCE_NAME, f"Request failed: {url}", exc) from exc

    return resp


def _parse_article(article: ET.Element) -> dict[str, Any]:
    """Parse a single PubmedArticle XML element into the unified result dict."""
    citation = article.find("MedlineCitation")
    if citation is None:
        raise DataSourceError(SOURCE_NAME, "Missing MedlineCitation in article XML")

    pmid_el = citation.find("PMID")
    pmid = pmid_el.text.strip() if pmid_el is not None and pmid_el.text else ""

    art = citation.find("Article")
    if art is None:
        raise DataSourceError(SOURCE_NAME, f"Missing Article for PMID {pmid}")

    # Title
    title_el = art.find("ArticleTitle")
    title = title_el.text.strip() if title_el is not None and title_el.text else ""

    # Authors
    authors: list[str] = []
    author_list = art.find("AuthorList")
    if author_list is not None:
        for author in author_list.findall("Author"):
            last = author.find("LastName")
            fore = author.find("ForeName")
            if last is not None and last.text:
                name = last.text.strip()
                if fore is not None and fore.text:
                    name = f"{name} {fore.text.strip()}"
                authors.append(name)
            elif (collective := author.find("CollectiveName")) is not None and collective.text:
                authors.append(collective.text.strip())

    # Abstract
    abstract_parts: list[str] = []
    abstract_el = art.find("Abstract")
    if abstract_el is not None:
        for text_el in abstract_el.findall("AbstractText"):
            label = text_el.get("Label", "")
            content = "".join(text_el.itertext()).strip()
            if label and content:
                abstract_parts.append(f"{label}: {content}")
            elif content:
                abstract_parts.append(content)
    abstract = " ".join(abstract_parts)

    # Journal
    journal_el = art.find("Journal")
    journal = ""
    year = None
    if journal_el is not None:
        title_el = journal_el.find("Title")
        if title_el is not None and title_el.text:
            journal = title_el.text.strip()
        # Year from JournalIssue/PubDate
        issue = journal_el.find("JournalIssue")
        if issue is not None:
            pub_date = issue.find("PubDate")
            if pub_date is not None:
                year_el = pub_date.find("Year")
                if year_el is not None and year_el.text:
                    try:
                        year = int(year_el.text.strip())
                    except ValueError:
                        pass
                if year is None:
                    medline_date = pub_date.find("MedlineDate")
                    if medline_date is not None and medline_date.text:
                        # Extract first 4-digit year from string like "2024 Jan-Feb"
                        import re

                        m = re.search(r"\d{4}", medline_date.text)
                        if m:
                            year = int(m.group())

    # DOI
    doi = ""
    for eloi in art.findall("ELocationID"):
        if eloi.get("EIdType") == "doi" and eloi.text:
            doi = eloi.text.strip()
            break

    return {
        "title": title,
        "authors": authors,
        "year": year,
        "pmid": pmid,
        "doi": doi,
        "journal": journal,
        "abstract": abstract,
        "source": SOURCE_NAME,
    }


class PubMedSource:
    """PubMed data source providing search, fetch, and MeSH lookup."""

    def search(
        self,
        query: str,
        rows: int = 5,
        sort: str = "relevance",
    ) -> dict[str, Any]:
        """Search PubMed and return structured results.

        Args:
            query: PubMed search query string.
            rows: Number of results to return.
            sort: Sort order -- "relevance" (Best Match) or "date".

        Returns:
            Dict with keys: total, query, results (list of unified result dicts).
        """
        if not query or not query.strip():
            raise DataSourceError(SOURCE_NAME, "Empty search query")

        cfg = get_config()
        if not cfg.pubmed_email:
            raise DataSourceError(
                SOURCE_NAME,
                "PubMed email not configured. Set PUBMED_EMAIL env var or [pubmed].email in config.toml",
            )

        rows = min(rows, cfg.max_rows)
        sort_param = "relevance" if sort == "relevance" else "pub_date"

        # Step 1: esearch to get WebEnv + query_key
        search_params: dict[str, Any] = {
            "db": "pubmed",
            "term": query.strip(),
            "retmax": rows,
            "usehistory": "y",
            "retmode": "xml",
            "sort": sort_param,
        }
        resp = _get("esearch.fcgi", search_params)
        root = ET.fromstring(resp.content)

        count_el = root.find("Count")
        total = int(count_el.text) if count_el is not None and count_el.text else 0

        web_env_el = root.find("WebEnv")
        query_key_el = root.find("QueryKey")

        if web_env_el is None or query_key_el is None or not web_env_el.text or not query_key_el.text:
            # No results
            return {"total": 0, "query": query, "results": []}

        web_env = web_env_el.text.strip()
        query_key = query_key_el.text.strip()

        # Step 2: efetch to get article details
        fetch_params: dict[str, Any] = {
            "db": "pubmed",
            "query_key": query_key,
            "WebEnv": web_env,
            "retmax": rows,
            "retmode": "xml",
            "rettype": "abstract",
        }
        resp = _get("efetch.fcgi", fetch_params)
        fetch_root = ET.fromstring(resp.content)

        results: list[dict[str, Any]] = []
        for article in fetch_root.findall("PubmedArticle"):
            try:
                results.append(_parse_article(article))
            except DataSourceError as exc:
                logger.warning("Failed to parse article: %s", exc)
                continue

        return {"total": total, "query": query, "results": results}

    def get_by_pmid(self, pmid: str) -> dict[str, Any]:
        """Fetch a single article by PMID.

        Args:
            pmid: PubMed ID (numeric string).

        Returns:
            Unified result dict for the article.

        Raises:
            DataSourceError: If PMID is invalid or article not found.
        """
        if not pmid or not pmid.strip().isdigit():
            raise DataSourceError(SOURCE_NAME, f"Invalid PMID: {pmid}")

        cfg = get_config()
        if not cfg.pubmed_email:
            raise DataSourceError(
                SOURCE_NAME,
                "PubMed email not configured. Set PUBMED_EMAIL env var or [pubmed].email in config.toml",
            )

        fetch_params: dict[str, Any] = {
            "db": "pubmed",
            "id": pmid.strip(),
            "retmode": "xml",
            "rettype": "abstract",
        }
        resp = _get("efetch.fcgi", fetch_params)
        root = ET.fromstring(resp.content)

        article = root.find("PubmedArticle")
        if article is None:
            raise DataSourceError(SOURCE_NAME, f"PMID {pmid} not found")

        return _parse_article(article)

    def lookup_mesh(self, term: str) -> dict[str, Any]:
        """Look up a MeSH descriptor by term.

        Queries the MeSH database via E-utilities to find matching
        descriptor names and unique IDs.

        Args:
            term: Search term to look up in MeSH.

        Returns:
            Dict with keys: term, results (list of {name, mesh_id, ui}).
        """
        if not term or not term.strip():
            raise DataSourceError(SOURCE_NAME, "Empty MeSH lookup term")

        cfg = get_config()
        if not cfg.pubmed_email:
            raise DataSourceError(
                SOURCE_NAME,
                "PubMed email not configured. Set PUBMED_EMAIL env var or [pubmed].email in config.toml",
            )

        # Use esearch on MeSH database
        search_params: dict[str, Any] = {
            "db": "mesh",
            "term": term.strip(),
            "retmax": 10,
            "retmode": "xml",
        }
        resp = _get("esearch.fcgi", search_params)
        try:
            root = ET.fromstring(resp.content)
        except ET.ParseError as exc:
            raise DataSourceError(
                SOURCE_NAME,
                "Invalid XML response from NCBI MeSH ESearch",
                exc,
            ) from exc

        id_list = root.find("IdList")
        if id_list is None or len(id_list) == 0:
            return {"term": term, "results": []}

        ids = [id_el.text.strip() for id_el in id_list.findall("Id") if id_el.text]

        if not ids:
            return {"term": term, "results": []}

        # MeSH full-record EFetch is text-only, even when retmode=xml is
        # requested. ESummary v2 provides structured descriptor metadata,
        # including the canonical MeSH UI, without parsing the text view.
        summary_params: dict[str, Any] = {
            "db": "mesh",
            "id": ",".join(ids),
            "retmode": "json",
            "version": "2.0",
        }
        resp = _get("esummary.fcgi", summary_params)
        try:
            payload = resp.json()
        except (ValueError, requests.JSONDecodeError) as exc:
            raise DataSourceError(
                SOURCE_NAME,
                "Invalid JSON response from NCBI MeSH ESummary",
                exc,
            ) from exc

        summary = payload.get("result") if isinstance(payload, dict) else None
        if not isinstance(summary, dict):
            raise DataSourceError(
                SOURCE_NAME,
                "Malformed NCBI MeSH ESummary response: missing result object",
            )

        results: list[dict[str, str]] = []
        for entrez_uid in ids:
            record = summary.get(entrez_uid)
            if not isinstance(record, dict):
                raise DataSourceError(
                    SOURCE_NAME,
                    f"Malformed NCBI MeSH ESummary response: missing UID {entrez_uid}",
                )

            mesh_terms = record.get("ds_meshterms")
            name = ""
            if isinstance(mesh_terms, list):
                name = next(
                    (
                        value.strip()
                        for value in mesh_terms
                        if isinstance(value, str) and value.strip()
                    ),
                    "",
                )

            ui_value = record.get("ds_meshui")
            ui = ui_value.strip() if isinstance(ui_value, str) else ""

            if not name:
                raise DataSourceError(
                    SOURCE_NAME,
                    f"Malformed NCBI MeSH ESummary response: missing descriptor name for UID {entrez_uid}",
                )
            if not re.fullmatch(r"[A-Z]\d{6,}", ui):
                raise DataSourceError(
                    SOURCE_NAME,
                    f"Malformed NCBI MeSH ESummary response: invalid MeSH UI for UID {entrez_uid}",
                )

            results.append(
                {
                    "name": name,
                    "mesh_id": ui,
                    "ui": ui,
                    "entrez_uid": entrez_uid,
                }
            )

        return {"term": term, "results": results}
