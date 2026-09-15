"""arXiv data source via REST API (Atom XML feed)."""

import re
import time
import urllib.parse
from datetime import datetime

import defusedxml.ElementTree as ET
import requests

from utils.config import get_config
from utils.errors import DataSourceError
from utils.logging import setup_logging

ARXIV_API_URL = "https://export.arxiv.org/api/query"

ARXIV_NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "arxiv": "http://arxiv.org/schemas/atom",
}

_MIN_REQUEST_INTERVAL = 3.0  # seconds between requests
_SOURCE_NAME = "arxiv"

logger = setup_logging("INFO")


class ArxivSource:
    """arXiv search and retrieval via the Atom API."""

    def __init__(self):
        self._last_request_time: float = 0.0
        self._timeout: int | None = None

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def search(
        self,
        query: str,
        rows: int = 5,
        categories: list[str] | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> dict:
        """Search arXiv.

        Parameters
        ----------
        query : str
            Free-text search query.
        rows : int
            Max number of results to return.
        categories : list[str] | None
            arXiv categories to restrict to (e.g. ["cs.AI", "cs.LG"]).
        date_from : str | None
            Start date in YYYY-MM-DD format.
        date_to : str | None
            End date in YYYY-MM-DD format.

        Returns
        -------
        dict
            {"results": [...], "total": int, "source": "arxiv"}
        """
        search_query = self._build_query(query, categories)
        date_filter = self._build_date_filter(date_from, date_to)

        params = {
            "search_query": search_query,
            "start": 0,
            "max_results": rows,
            "sortBy": "relevance",
            "sortOrder": "descending",
        }
        if date_filter:
            params["search_query"] = f"{search_query}+AND+{date_filter}"

        raw = self._request(params)
        results = self._parse_feed(raw)
        return {
            "results": results,
            "total": len(results),
            "source": _SOURCE_NAME,
        }

    def get_by_id(self, arxiv_id: str) -> dict:
        """Retrieve a single paper by arXiv ID.

        Parameters
        ----------
        arxiv_id : str
            arXiv identifier, e.g. "2401.12345" or "2401.12345v1".

        Returns
        -------
        dict
            Paper record in unified format.
        """
        clean_id = self._normalize_id(arxiv_id)
        params = {
            "id_list": clean_id,
            "max_results": 1,
        }
        raw = self._request(params)
        results = self._parse_feed(raw)
        if not results:
            raise DataSourceError(
                _SOURCE_NAME,
                f"Paper not found: {arxiv_id}",
            )
        return results[0]

    # ------------------------------------------------------------------
    # Query construction
    # ------------------------------------------------------------------

    @staticmethod
    def _build_query(user_query: str, categories: list[str] | None = None) -> str:
        """Build the search_query parameter.

        Combines user query with optional category restrictions.
        Returns a string with +AND+/+OR+ connectors (URL-ready).
        """
        parts: list[str] = []
        parts.append(f"({user_query})")
        if categories:
            cat_expr = " OR ".join(f"cat:{cat}" for cat in categories)
            parts.append(f"({cat_expr})")
        combined = " AND ".join(parts)
        # Replace connectors and spaces for URL embedding
        combined = (
            combined.replace(" AND ", "+AND+")
            .replace(" OR ", "+OR+")
            .replace(" ", "+")
        )
        return combined

    @staticmethod
    def _build_date_filter(
        date_from: str | None, date_to: str | None
    ) -> str:
        """Build submittedDate filter expression.

        The arXiv API requires the literal +TO+ syntax and 14-digit
        timestamps in the format YYYYMMDDHHMM.

        Returns empty string when no date bounds are given.
        """
        if not date_from and not date_to:
            return ""

        # Default boundaries
        start_ts = "000000000000"
        end_ts = "999912312359"

        if date_from:
            start_ts = _date_to_ts(date_from)
        if date_to:
            end_ts = _date_to_ts(date_to, end_of_day=True)

        return f"submittedDate:[{start_ts}+TO+{end_ts}]"

    # ------------------------------------------------------------------
    # HTTP
    # ------------------------------------------------------------------

    def _request(self, params: dict) -> str:
        """Execute an HTTP GET to the arXiv API with rate limiting."""
        self._enforce_rate_limit()
        url = f"{ARXIV_API_URL}?{urllib.parse.urlencode(params)}"
        timeout = self._get_timeout()
        logger.debug("arXiv request: %s", url)

        try:
            resp = requests.get(
                url,
                headers={"User-Agent": "academic-search/1.0"},
                timeout=timeout,
            )
            resp.raise_for_status()
            return resp.text
        except requests.exceptions.HTTPError as exc:
            code = exc.response.status_code if exc.response is not None else 0
            if code in (429, 503):
                raise DataSourceError(
                    _SOURCE_NAME,
                    f"Rate limited or unavailable (HTTP {code})",
                    original_error=exc,
                ) from exc
            raise DataSourceError(
                _SOURCE_NAME,
                f"HTTP error {code}: {exc}",
                original_error=exc,
            ) from exc
        except requests.exceptions.Timeout as exc:
            raise DataSourceError(
                _SOURCE_NAME,
                f"Request timed out after {timeout}s",
                original_error=exc,
            ) from exc
        except requests.exceptions.RequestException as exc:
            raise DataSourceError(
                _SOURCE_NAME,
                f"Network error: {exc}",
                original_error=exc,
            ) from exc

    def _enforce_rate_limit(self) -> None:
        elapsed = time.monotonic() - self._last_request_time
        if elapsed < _MIN_REQUEST_INTERVAL:
            time.sleep(_MIN_REQUEST_INTERVAL - elapsed)
        self._last_request_time = time.monotonic()

    def _get_timeout(self) -> int:
        if self._timeout is None:
            self._timeout = get_config().arxiv_timeout
        return self._timeout

    # ------------------------------------------------------------------
    # XML parsing
    # ------------------------------------------------------------------

    def _parse_feed(self, xml_text: str) -> list[dict]:
        """Parse arXiv Atom XML into a list of unified result dicts."""
        try:
            root = ET.fromstring(xml_text)
        except ET.ParseError as exc:
            raise DataSourceError(
                _SOURCE_NAME,
                f"Malformed XML response: {exc}",
                original_error=exc,
            ) from exc

        entries: list[dict] = []
        for entry in root.findall("atom:entry", ARXIV_NS):
            parsed = self._parse_entry(entry)
            if parsed:
                entries.append(parsed)
        return entries

    def _parse_entry(self, entry: ET.Element) -> dict | None:
        """Extract a single paper record from an Atom <entry>."""
        arxiv_id_raw = _text(entry, "atom:id", ARXIV_NS)
        if not arxiv_id_raw:
            return None

        title = _text(entry, "atom:title", ARXIV_NS) or ""
        title = re.sub(r"\s+", " ", title).strip()

        summary = _text(entry, "atom:summary", ARXIV_NS) or ""
        summary = re.sub(r"\s+", " ", summary).strip()

        authors = [
            name
            for name in (
                _text(author, "atom:name", ARXIV_NS)
                for author in entry.findall("atom:author", ARXIV_NS)
            )
            if name
        ]

        primary_cat = entry.find("arxiv:primary_category", ARXIV_NS)
        categories = []
        if primary_cat is not None:
            term = primary_cat.get("term")
            if term:
                categories.append(term)
        # Also collect secondary categories from atom:category elements
        for cat in entry.findall("atom:category", ARXIV_NS):
            scheme = cat.get("scheme", "")
            term = cat.get("term", "")
            if term and "arxiv" in scheme.lower() and term not in categories:
                categories.append(term)

        published = _text(entry, "atom:published", ARXIV_NS) or ""
        year = _extract_year(published)

        pdf_url = ""
        for link in entry.findall("atom:link", ARXIV_NS):
            if link.get("title") == "pdf":
                pdf_url = link.get("href", "")
                break

        arxiv_id = self._normalize_id(arxiv_id_raw)

        return {
            "title": title,
            "authors": authors,
            "year": year,
            "arxiv_id": arxiv_id,
            "categories": categories,
            "abstract": summary,
            "pdf_url": pdf_url,
            "source": _SOURCE_NAME,
        }

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _normalize_id(raw: str) -> str:
        """Strip URL prefix and version suffix from an arXiv ID.

        http://arxiv.org/abs/2401.12345v1 -> 2401.12345
        """
        arxiv_id = raw.strip()
        # Remove URL prefix
        match = re.search(r"(\d{4}\.\d{4,5})(v\d+)?$", arxiv_id)
        if match:
            return match.group(1)
        # Fallback: strip known prefixes
        for prefix in ("https://arxiv.org/abs/", "http://arxiv.org/abs/"):
            if arxiv_id.startswith(prefix):
                arxiv_id = arxiv_id[len(prefix):]
                break
        # Strip version
        arxiv_id = re.sub(r"v\d+$", "", arxiv_id)
        return arxiv_id


# ------------------------------------------------------------------
# Module-level helpers
# ------------------------------------------------------------------


def _text(parent: ET.Element, xpath: str, ns: dict) -> str | None:
    """Return stripped text of a sub-element, or None."""
    el = parent.find(xpath, ns)
    if el is not None and el.text:
        return el.text.strip()
    return None


def _date_to_ts(date_str: str, end_of_day: bool = False) -> str:
    """Convert YYYY-MM-DD to YYYYMMDDHHMM (14-digit timestamp).

    Parameters
    ----------
    date_str : str
        Date in YYYY-MM-DD format.
    end_of_day : bool
        If True, use 2359 as HHMM; otherwise 0000.
    """
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    suffix = "2359" if end_of_day else "0000"
    return dt.strftime("%Y%m%d") + suffix


def _extract_year(published: str) -> int | None:
    """Extract year from ISO datetime string (e.g. 2024-01-15T...)."""
    try:
        return int(published[:4])
    except (ValueError, IndexError):
        return None
