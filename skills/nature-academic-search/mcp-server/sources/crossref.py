"""CrossRef data source for academic search."""

import re
from urllib.parse import quote

import requests

from utils.config import get_config
from utils.errors import DataSourceError

CROSSREF_API = "https://api.crossref.org"


class CrossRefSource:
    """CrossRef API wrapper with unified result format."""

    SOURCE_NAME = "crossref"

    def __init__(self):
        config = get_config()
        mailto = config.crossref_mailto or "user@example.com"
        self._headers = {
            "User-Agent": f"ClaudeCode-MCP-Crossref/1.0 (mailto:{mailto})",
        }
        self._timeout = config.crossref_timeout

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def search(
        self, query: str, rows: int = 5, filter_type: str | None = None
    ) -> dict:
        """Search CrossRef works.

        Args:
            query: Keywords, author name, title, DOI prefix, etc.
            rows: Number of results (max 50).
            filter_type: Optional work type filter, e.g. "journal-article".

        Returns:
            {"total": int, "results": [unified_result, ...]}
        """
        params: dict = {"query": query, "rows": min(rows, 50)}
        if filter_type:
            params["filter"] = f"type:{filter_type}"

        data = self._request("/works", params=params)
        items = data.get("items", [])
        total = data.get("total-results", 0)

        results = [self._normalize_search_item(item) for item in items]
        return {"total": total, "results": results}

    def get_by_doi(self, doi: str) -> dict:
        """Get detailed metadata for a single work by DOI.

        Args:
            doi: Digital Object Identifier (e.g. "10.1038/nature12373").

        Returns:
            Unified result dict with extra fields (abstract, volume, etc.).
        """
        data = self._request(f"/works/{quote(doi, safe='/')}")
        return self._normalize_detail_item(data)

    def get_citation(self, doi: str, style: str = "apa") -> str:
        """Return a formatted citation string via CrossRef content negotiation.

        Args:
            doi: Digital Object Identifier.
            style: Citation style (apa, nature, vancouver, ieee, etc.).

        Returns:
            Formatted citation string.
        """
        url = f"{CROSSREF_API}/works/{quote(doi, safe='/')}/transform"
        headers = {
            **self._headers,
            "Accept": f"text/x-bibliography; style={style}",
        }
        try:
            resp = requests.get(url, headers=headers, timeout=self._timeout)
        except requests.RequestException as exc:
            raise DataSourceError(
                self.SOURCE_NAME,
                f"Network error fetching citation for {doi}: {exc}",
                original_error=exc,
            ) from exc

        if resp.status_code == 404:
            raise DataSourceError(
                self.SOURCE_NAME,
                f"No citation found for DOI {doi}",
            )
        if resp.status_code == 406:
            raise DataSourceError(
                self.SOURCE_NAME,
                f"Unsupported citation style: {style}",
            )

        try:
            resp.raise_for_status()
        except requests.HTTPError as exc:
            raise DataSourceError(
                self.SOURCE_NAME,
                f"HTTP {resp.status_code} fetching citation for {doi}",
                original_error=exc,
            ) from exc

        return resp.text.strip()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _request(self, path: str, params: dict | None = None) -> dict:
        """Issue GET to CrossRef API and return the ``message`` payload."""
        url = f"{CROSSREF_API}{path}"
        try:
            resp = requests.get(
                url, params=params, headers=self._headers, timeout=self._timeout
            )
            resp.raise_for_status()
        except requests.HTTPError as exc:
            status = exc.response.status_code if exc.response is not None else "?"
            raise DataSourceError(
                self.SOURCE_NAME,
                f"HTTP {status} from {url}",
                original_error=exc,
            ) from exc
        except requests.RequestException as exc:
            raise DataSourceError(
                self.SOURCE_NAME,
                f"Network error calling {url}: {exc}",
                original_error=exc,
            ) from exc

        return resp.json().get("message", {})

    # ------------------------------------------------------------------
    # Normalization
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_authors(author_list: list[dict], limit: int = 0) -> list[str]:
        """Convert CrossRef author entries to ``["Given Family", ...]`` list.

        Args:
            author_list: Raw ``author`` array from CrossRef.
            limit: Max authors to include; 0 = all.
        """
        subset = author_list[:limit] if limit else author_list
        names = [
            f"{a.get('given', '')} {a.get('family', '')}".strip()
            for a in subset
        ]
        if limit and len(author_list) > limit:
            names.append("et al.")
        return names

    @staticmethod
    def _extract_year(item: dict) -> int | None:
        """Best-effort publication year extraction."""
        for key in ("published-print", "published-online", "created"):
            parts = item.get(key, {}).get("date-parts", [[None]])
            year = parts[0][0] if parts and parts[0] else None
            if year is not None:
                return year
        return None

    @staticmethod
    def _extract_preprint_of_dois(item: dict) -> list[str]:
        """Retain explicit Crossref version relations, not inferred identities.

        Targets may be accepted manuscripts or versions of record. They still
        require resolution before use; this field does not replace a citation.
        """
        relation = item.get("relation")
        entries = relation.get("is-preprint-of", []) if isinstance(relation, dict) else []
        result: list[str] = []
        seen: set[str] = set()
        for entry in entries if isinstance(entries, list) else []:
            if not isinstance(entry, dict) or entry.get("id-type") != "doi":
                continue
            value = entry.get("id")
            if not isinstance(value, str):
                continue
            doi = value.strip()
            if re.fullmatch(r"10\.\d{4,9}/[^\s<>\x00-\x1f\x7f]+", doi) and doi.casefold() not in seen:
                result.append(doi)
                seen.add(doi.casefold())
        return result

    def _normalize_search_item(self, item: dict) -> dict:
        """Map a CrossRef work item to the unified search result format."""
        return {
            "title": (item.get("title") or [""])[0],
            "authors": self._extract_authors(item.get("author", []), limit=5),
            "year": self._extract_year(item),
            "doi": item.get("DOI"),
            "journal": (item.get("container-title") or [""])[0],
            "source": self.SOURCE_NAME,
            "citation_count": item.get("is-referenced-by-count", 0),
            "preprint_of_dois": self._extract_preprint_of_dois(item),
        }

    def _normalize_detail_item(self, item: dict) -> dict:
        """Map a CrossRef work item to the unified detail result format."""
        base = self._normalize_search_item(item)
        base.update({
            "authors": self._extract_authors(item.get("author", [])),
            "abstract": item.get("abstract", ""),
            "volume": item.get("volume", ""),
            "issue": item.get("issue", ""),
            "pages": item.get("page", ""),
            "publisher": item.get("publisher", ""),
            "type": item.get("type"),
            "references_count": item.get("references-count", 0),
            "url": item.get("URL"),
        })
        return base
