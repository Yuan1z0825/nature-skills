#!/usr/bin/env python3
"""
Segment manuscript text, search strict Nature/CNS-family citation candidates, and export a
reference-manager file. By default the script writes one inspectable `.ris` file.

Optional review artifacts can still be generated, but they are opt-in.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen
import defusedxml.ElementTree as ET
xml_escape = lambda data: data.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
quoteattr = lambda data: '"%s"' % xml_escape(data).replace('"', "&quot;")


CROSSREF_API = "https://api.crossref.org/works"
PUBMED_EFETCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
USER_AGENT = "codex-nature-citation/1.0 (mailto:unknown@example.com)"
EXPORT_FORMAT_CHOICES = ("enw", "ris", "zotero-rdf", "rdf")
DEFAULT_EXPORT_FORMAT = "ris"
ZOTERO_RDF_NS = {
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "z": "http://www.zotero.org/namespaces/export#",
    "dcterms": "http://purl.org/dc/terms/",
    "bib": "http://purl.org/net/biblio#",
    "foaf": "http://xmlns.com/foaf/0.1/",
    "dc": "http://purl.org/dc/elements/1.1/",
    "prism": "http://prismstandard.org/namespaces/1.2/basic/",
}


NATURE_EXACT = {
    "Nature",
    "Nature Biotechnology",
    "Nature Cancer",
    "Nature Cardiovascular Research",
    "Nature Cell Biology",
    "Nature Chemical Biology",
    "Nature Chemistry",
    "Nature Climate Change",
    "Nature Communications",
    "Nature Computational Science",
    "Nature Ecology & Evolution",
    "Nature Electronics",
    "Nature Energy",
    "Nature Food",
    "Nature Genetics",
    "Nature Geoscience",
    "Nature Human Behaviour",
    "Nature Immunology",
    "Nature Machine Intelligence",
    "Nature Materials",
    "Nature Medicine",
    "Nature Metabolism",
    "Nature Methods",
    "Nature Microbiology",
    "Nature Nanotechnology",
    "Nature Neuroscience",
    "Nature Photonics",
    "Nature Physics",
    "Nature Plants",
    "Nature Protocols",
    "Nature Reviews Cancer",
    "Nature Reviews Cardiology",
    "Nature Reviews Chemistry",
    "Nature Reviews Clinical Oncology",
    "Nature Reviews Drug Discovery",
    "Nature Reviews Earth & Environment",
    "Nature Reviews Endocrinology",
    "Nature Reviews Gastroenterology & Hepatology",
    "Nature Reviews Genetics",
    "Nature Reviews Immunology",
    "Nature Reviews Materials",
    "Nature Reviews Microbiology",
    "Nature Reviews Molecular Cell Biology",
    "Nature Reviews Nephrology",
    "Nature Reviews Neurology",
    "Nature Reviews Neuroscience",
    "Nature Reviews Physics",
    "Nature Reviews Psychology",
    "Nature Reviews Rheumatology",
    "Nature Structural & Molecular Biology",
    "Scientific Reports",
}


SCIENCE_EXACT = {
    "Science",
    "Science Advances",
    "Science Immunology",
    "Science Robotics",
    "Science Signaling",
    "Science Translational Medicine",
}


CELL_EXACT = {
    "Cell",
    "Cancer Cell",
    "Cell Chemical Biology",
    "Cell Genomics",
    "Cell Host & Microbe",
    "Cell Metabolism",
    "Cell Reports",
    "Cell Reports Medicine",
    "Cell Reports Methods",
    "Cell Reports Physical Science",
    "Cell Stem Cell",
    "Cell Systems",
    "Chem",
    "Current Biology",
    "Developmental Cell",
    "Immunity",
    "Joule",
    "Med",
    "Molecular Cell",
    "Neuron",
    "One Earth",
    "Patterns",
    "Structure",
    "The Innovation",
}


CELL_TRENDS_EXACT = {
    "Trends in Biochemical Sciences",
    "Trends in Biotechnology",
    "Trends in Cancer",
    "Trends in Cell Biology",
    "Trends in Chemistry",
    "Trends in Cognitive Sciences",
    "Trends in Ecology & Evolution",
    "Trends in Endocrinology & Metabolism",
    "Trends in Genetics",
    "Trends in Immunology",
    "Trends in Microbiology",
    "Trends in Molecular Medicine",
    "Trends in Neurosciences",
    "Trends in Parasitology",
    "Trends in Pharmacological Sciences",
    "Trends in Plant Science",
}


FLAGSHIP = {"Nature", "Science", "Cell"}


@dataclass
class Segment:
    id: str
    text: str
    search_query: str
    order: int

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "order": self.order,
            "text": self.text,
            "search_query": self.search_query,
        }


@dataclass
class Candidate:
    title: str
    journal: str
    family: str
    year: str
    y1: str
    doi: str
    url: str
    volume: str
    issue: str
    start_page: str
    end_page: str
    issn: str
    authors: list[str]
    abstract: str
    type: str
    score: float
    source_query: str
    pmid: str = ""
    source_catalog: str = "Crossref"
    author_warnings: list[str] = field(default_factory=list)

    @property
    def doi_url(self) -> str:
        return f"https://doi.org/{self.doi}" if self.doi else self.url

    @property
    def key(self) -> str:
        if self.doi:
            return self.doi.lower()
        return f"{self.title.lower()}|{self.journal.lower()}"

    @property
    def first_author(self) -> str:
        if not self.authors:
            return "Unknown author"
        return self.authors[0].split(",", 1)[0]

    @property
    def citation_marker(self) -> str:
        if self.year:
            return f"({self.first_author} et al., {self.year})"
        return f"({self.first_author} et al.)"

    @property
    def page_range(self) -> str:
        if self.start_page and self.end_page:
            return f"{self.start_page}-{self.end_page}"
        return self.start_page

    @property
    def identifier_url(self) -> str:
        return self.doi_url or self.url

    @property
    def article_resource(self) -> str:
        if self.identifier_url:
            return self.identifier_url
        return f"urn:candidate:{stable_hash(self.key or self.title or 'candidate')}"

    @property
    def journal_resource(self) -> str:
        return build_journal_resource(self)

    @property
    def zotero_citation_key(self) -> str:
        return build_zotero_citation_key(self)

    def as_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "journal": self.journal,
            "family": self.family,
            "year": self.year,
            "doi": self.doi,
            "pmid": self.pmid,
            "url": self.url,
            "doi_url": self.doi_url,
            "volume": self.volume,
            "issue": self.issue,
            "start_page": self.start_page,
            "end_page": self.end_page,
            "issn": self.issn,
            "authors": self.authors,
            "abstract": self.abstract,
            "type": self.type,
            "score": self.score,
            "source_query": self.source_query,
            "source_catalog": self.source_catalog,
            "author_metadata_status": "complete" if not self.author_warnings else "incomplete",
            "author_warnings": self.author_warnings,
            "citation_marker": self.citation_marker,
            "support_grade": "metadata-only candidate",
            "screening_note": "Inspect abstract/publisher page before citing this paper as support.",
            "enw_record": build_enw_record(self),
            "ris_record": build_ris_record(self),
            "journal_resource": self.journal_resource,
            "zotero_rdf_article": build_zotero_rdf_article(self),
            "zotero_rdf_journal": build_zotero_rdf_journal(self),
        }


def normalize_title(title: str) -> str:
    return re.sub(r"\s+", " ", title or "").strip()


def stable_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:12]


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", (value or "").lower()).strip("-")
    return slug or "item"


def normalize_export_format(value: str | None) -> str:
    if not value:
        return DEFAULT_EXPORT_FORMAT
    if value == "rdf":
        return "zotero-rdf"
    return value


def infer_export_format(output_path: Path | None) -> str:
    if output_path is None:
        return DEFAULT_EXPORT_FORMAT
    suffix = output_path.suffix.lower()
    if suffix == ".ris":
        return "ris"
    if suffix == ".rdf":
        return "zotero-rdf"
    if suffix == ".enw":
        return "enw"
    return DEFAULT_EXPORT_FORMAT


def export_filename(export_format: str, base: str = "references") -> str:
    if export_format == "ris":
        return f"{base}.ris"
    if export_format == "zotero-rdf":
        return f"{base}.rdf"
    return f"{base}.enw"


def slug_from_text(text: str, max_words: int = 6) -> str:
    """Derive a filename slug from the first meaningful words of manuscript text."""
    text = clean_text(text)
    text = re.sub(r"\[[^\]]+\]|\([A-Za-z]+ et al\.,? \d{4}\)", " ", text)
    words = re.findall(r"[A-Za-z0-9]+|[一-鿿]+", text)
    stopwords = {
        "the", "a", "an", "and", "or", "of", "to", "in", "for", "by", "with", "on", "at",
        "from", "is", "are", "was", "were", "be", "been", "being", "that", "this", "these",
        "those", "it", "its", "can", "may", "could", "not", "but", "as", "if", "into",
    }
    content = [w for w in words if w.lower() not in stopwords]
    slug = "-".join(w.lower() for w in content[:max_words])
    return slug or "references"


def export_label(export_format: str) -> str:
    if export_format == "ris":
        return "RIS"
    if export_format == "zotero-rdf":
        return "Zotero RDF"
    return "ENW"


def make_partial_path(path: Path) -> Path:
    return path.with_name(f"{path.stem}.partial{path.suffix}")


def retry_with_backoff(action: Callable[[], Any], max_retries: int, base_delay: float = 0.5) -> Any:
    last_error: Exception | None = None
    retries = max(0, max_retries)
    for attempt in range(retries + 1):
        try:
            return action()
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            if attempt >= retries:
                break
            time.sleep(base_delay * (2 ** attempt))
    if last_error is not None:
        raise last_error
    raise RuntimeError("retry_with_backoff() exited without returning or raising")


def resolve_batch_size(segment_count: int, args: argparse.Namespace) -> int:
    if getattr(args, "batch_size", 0) and args.batch_size > 0:
        return max(1, args.batch_size)
    if segment_count > 10:
        return 10
    return 0


def chunk_segments(segments: list[Segment], batch_size: int) -> list[list[Segment]]:
    if not segments:
        return []
    if batch_size <= 0 or batch_size >= len(segments):
        return [segments]
    return [segments[idx : idx + batch_size] for idx in range(0, len(segments), batch_size)]


def limit_segments(segments: list[Segment], max_segments: int) -> tuple[list[Segment], int]:
    if max_segments and max_segments > 0 and len(segments) > max_segments:
        return segments[:max_segments], len(segments) - max_segments
    return segments, 0


def zotero_date_value(item: Candidate) -> str:
    if item.y1:
        return item.y1.replace("/", "-")
    return item.year


def split_author_parts(name: str) -> tuple[str, str]:
    if name.endswith(","):
        return name[:-1].replace(",,", ",").strip(), ""
    if "," in name:
        family, given = name.split(",", 1)
        return family.strip(), given.strip()
    parts = [part for part in name.split() if part]
    if not parts:
        return "", ""
    if len(parts) == 1:
        return parts[0], ""
    return parts[-1], " ".join(parts[:-1])


def build_journal_resource(item: Candidate) -> str:
    parts: list[str] = []
    if item.issn:
        parts.append(f"issn:{slugify(item.issn)}")
    elif item.journal:
        parts.append(f"title:{slugify(item.journal)}")
    else:
        parts.append(f"record:{stable_hash(item.key or item.title or 'journal')}")
    if item.volume:
        parts.append(f"vol:{slugify(item.volume)}")
    if item.issue:
        parts.append(f"issue:{slugify(item.issue)}")
    return "urn:" + ":".join(parts)


def build_zotero_citation_key(item: Candidate) -> str:
    first_author = slugify(item.first_author)
    title_words = re.findall(r"[A-Za-z0-9]+", item.title)[:3]
    title_part = "".join(word.capitalize() for word in title_words) or "Item"
    year = item.year or "n.d."
    return f"{first_author}{title_part}{year}"


def journal_family(journal: str) -> str | None:
    journal = normalize_title(journal)
    if not journal:
        return None
    if journal in NATURE_EXACT or journal.startswith("Nature ") or journal.startswith("npj "):
        return "Nature Portfolio"
    if journal in SCIENCE_EXACT:
        return "Science family"
    if journal in CELL_EXACT or journal in CELL_TRENDS_EXACT:
        return "Cell Press"
    return None


def in_scope(journal: str, scope: str) -> bool:
    journal = normalize_title(journal)
    if not journal:
        return False
    if scope == "flagship":
        return journal in FLAGSHIP
    family = journal_family(journal)
    if scope == "nature":
        return family == "Nature Portfolio"
    if scope == "science":
        return family == "Science family"
    if scope == "cell":
        return family == "Cell Press"
    return family in {"Nature Portfolio", "Science family", "Cell Press"}


def first(values: list[Any] | None, default: str = "") -> str:
    if not values:
        return default
    value = values[0]
    if isinstance(value, str):
        return value
    return default


def date_parts(item: dict[str, Any]) -> list[int]:
    for key in ("published-print", "published-online", "published", "issued"):
        parts = item.get(key, {}).get("date-parts")
        if parts and parts[0]:
            return parts[0]
    return []


def year_from_item(item: dict[str, Any]) -> str:
    parts = date_parts(item)
    return str(parts[0]) if parts else ""


def y1_from_item(item: dict[str, Any]) -> str:
    parts = date_parts(item)
    if not parts:
        return ""
    year = f"{parts[0]:04d}"
    month = f"{parts[1]:02d}" if len(parts) > 1 else "01"
    day = f"{parts[2]:02d}" if len(parts) > 2 else "01"
    return f"{year}/{month}/{day}"


def endnote_corporate_author(name: str) -> str:
    """Return an EndNote-safe corporate author name.

    EndNote requires a trailing comma to prevent a corporate name from being
    inverted. Embedded commas are doubled so they remain part of the name.
    """
    normalized = clean_text(name).rstrip(",").strip()
    if not normalized:
        return ""
    return f"{normalized.replace(',', ',,')},"


def author_name(author: dict[str, Any]) -> str:
    family = clean_text(str(author.get("family") or ""))
    given = clean_text(str(author.get("given") or ""))
    suffix = clean_text(str(author.get("suffix") or ""))
    literal = clean_text(str(author.get("name") or ""))
    if literal and not family and not given:
        return endnote_corporate_author(literal)
    if family and given:
        parts = [family, given]
        if suffix:
            parts.append(suffix)
        return ", ".join(parts)
    return family or given or literal


def crossref_author_warnings(raw_authors: list[dict[str, Any]], authors: list[str]) -> list[str]:
    warnings: list[str] = []
    if not raw_authors or not authors:
        return ["No structured author list was supplied by the metadata source."]
    for index, author in enumerate(raw_authors, 1):
        family = clean_text(str(author.get("family") or ""))
        given = clean_text(str(author.get("given") or ""))
        literal = clean_text(str(author.get("name") or ""))
        if literal and not family and not given:
            continue
        if not family or not given:
            warnings.append(
                f"Author {index} lacks a {'family name' if not family else 'given name or initials'} in structured metadata."
            )
    return warnings


def pages(item: dict[str, Any]) -> tuple[str, str]:
    page = item.get("page", "") or item.get("article-number", "")
    if not page:
        return "", ""
    if "-" in page:
        start, end = page.split("-", 1)
        return start.strip(), end.strip()
    return page.strip(), ""


def clean_text(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text or "")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def ris_escape(text: str) -> str:
    return clean_text(text).replace("\n", " ").replace("\r", " ")


def split_sentences(text: str) -> list[str]:
    text = re.sub(r"\s+", " ", text.strip())
    if not text:
        return []
    pattern = r"(?<=[.!?。！？])\s+|(?<=[。！？])"
    return [part.strip() for part in re.split(pattern, text) if part.strip()]


def looks_like_heading(text: str) -> bool:
    stripped = text.strip()
    if len(stripped) > 90:
        return False
    if stripped.endswith((".", "。", "!", "！", "?", "？")):
        return False
    words = stripped.split()
    if 0 < len(words) <= 8 and not any(char in stripped for char in ",;，；"):
        return True
    return False


def query_from_segment(text: str, max_words: int = 26) -> str:
    text = clean_text(text)
    text = re.sub(r"\[[^\]]+\]|\([A-Za-z]+ et al\.,? \d{4}\)", " ", text)
    words = re.findall(r"[A-Za-z0-9α-ωΑ-Ωβγδκλμνπρστυφχψω\-]+|[\u4e00-\u9fff]+", text)
    if not words:
        return text[:240]
    return " ".join(words[:max_words])


def fallback_queries_from_segment(text: str) -> list[str]:
    words = re.findall(r"[A-Za-z0-9α-ωΑ-Ωβγδκλμνπρστυφχψω\-]+|[\u4e00-\u9fff]+", clean_text(text))
    if not words:
        return []
    stopwords = {
        "the", "a", "an", "and", "or", "of", "to", "in", "for", "by", "with", "on", "at", "from",
        "reveals", "reveal", "revealed", "promote", "promotes", "promoted", "promoting",
        "suppress", "suppresses", "suppressing", "show", "shows", "showed", "indicate", "indicates",
        "indicated", "identify", "identifies", "identified", "can", "may", "could", "is", "are",
        "was", "were", "be", "been", "being", "that", "this", "these", "those",
    }
    content = [word for word in words if word.lower() not in stopwords]
    candidates: list[str] = []
    if len(content) >= 3:
        candidates.append(" ".join(content[:12]))
    if len(content) >= 5:
        candidates.append(" ".join(content[:8]))
    deduped: list[str] = []
    seen: set[str] = set()
    for candidate in candidates:
        normalized = candidate.lower().strip()
        if normalized and normalized not in seen:
            seen.add(normalized)
            deduped.append(candidate)
    return deduped


def segment_text(text: str, max_chars: int = 700) -> list[Segment]:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n").strip()
    if not normalized:
        return []
    paragraphs = [part.strip() for part in re.split(r"\n\s*\n+", normalized) if part.strip()]
    raw_segments: list[str] = []
    for paragraph in paragraphs:
        if looks_like_heading(paragraph):
            continue
        sentences = split_sentences(paragraph)
        if len(sentences) > 1:
            raw_segments.extend(sentences)
        elif len(paragraph) <= max_chars:
            raw_segments.append(re.sub(r"\s+", " ", paragraph))
        else:
            raw_segments.extend(sentences)
    segments: list[Segment] = []
    for idx, segment in enumerate(raw_segments, 1):
        cleaned = clean_text(segment)
        if len(cleaned) < 10:
            continue
        segments.append(
            Segment(
                id=f"S{len(segments) + 1:03d}",
                text=cleaned,
                search_query=query_from_segment(cleaned),
                order=len(segments) + 1,
            )
        )
    return segments


def candidate_from_crossref(item: dict[str, Any], source_query: str) -> Candidate | None:
    journal = first(item.get("container-title"))
    if not journal:
        return None
    family = journal_family(journal) or ""
    start, end = pages(item)
    raw_authors = item.get("author", [])
    authors = [author_name(author) for author in raw_authors]
    authors = [author for author in authors if author]
    return Candidate(
        title=clean_text(first(item.get("title"))),
        journal=normalize_title(journal),
        family=family,
        year=year_from_item(item),
        y1=y1_from_item(item),
        doi=item.get("DOI", ""),
        url=item.get("URL", ""),
        volume=item.get("volume", ""),
        issue=item.get("issue", ""),
        start_page=start,
        end_page=end,
        issn=first(item.get("ISSN")),
        authors=authors,
        abstract=clean_text(item.get("abstract", "")),
        type=item.get("type", ""),
        score=float(item.get("score", 0.0) or 0.0),
        source_query=source_query,
        source_catalog="Crossref",
        author_warnings=crossref_author_warnings(raw_authors, authors),
    )


def crossref_headers(mailto: str | None = None) -> dict[str, str]:
    return {"User-Agent": USER_AGENT if not mailto else f"codex-nature-citation/1.0 (mailto:{mailto})"}


def fetch_crossref(query: str, rows: int, mailto: str | None = None, from_year: int | None = None, to_year: int | None = None, retries: int = 2) -> list[dict[str, Any]]:
    filters = ["type:journal-article"]
    if from_year is not None:
        filters.append(f"from-pub-date:{from_year}-01-01")
    if to_year is not None:
        filters.append(f"until-pub-date:{to_year}-12-31")
    params = {
        "query.bibliographic": query,
        "rows": str(rows),
        "select": "DOI,title,container-title,published,published-print,published-online,issued,author,volume,issue,page,article-number,ISSN,URL,abstract,type,score",
        "filter": ",".join(filters),
        "sort": "relevance",
        "order": "desc",
    }
    if mailto:
        params["mailto"] = mailto
    url = f"{CROSSREF_API}?{urlencode(params)}"
    req = Request(url, headers=crossref_headers(mailto))
    last_exc: Exception | None = None
    for attempt in range(1, retries + 2):
        try:
            with urlopen(req, timeout=30) as response:
                payload = json.loads(response.read().decode("utf-8"))
            return payload.get("message", {}).get("items", [])
        except Exception as exc:  # noqa: BLE001
            last_exc = exc
            if attempt <= retries:
                time.sleep(min(2 ** attempt, 8))
    raise last_exc  # type: ignore[misc]


def fetch_crossref_doi(doi: str, mailto: str | None = None) -> dict[str, Any]:
    url = f"{CROSSREF_API}/{quote(doi.strip(), safe='')}"
    if mailto:
        url = f"{url}?{urlencode({'mailto': mailto})}"
    req = Request(url, headers=crossref_headers(mailto))
    with urlopen(req, timeout=30) as response:
        payload = json.loads(response.read().decode("utf-8"))
    return payload.get("message", {})


MONTHS = {
    "jan": 1,
    "feb": 2,
    "mar": 3,
    "apr": 4,
    "may": 5,
    "jun": 6,
    "jul": 7,
    "aug": 8,
    "sep": 9,
    "oct": 10,
    "nov": 11,
    "dec": 12,
}


def xml_text(element: ET.Element | None) -> str:
    if element is None:
        return ""
    return clean_text("".join(element.itertext()))


def pubmed_date(article: ET.Element) -> tuple[str, str]:
    date_node = article.find("MedlineCitation/Article/Journal/JournalIssue/PubDate")
    if date_node is None:
        date_node = article.find("MedlineCitation/Article/ArticleDate")
    year = xml_text(date_node.find("Year")) if date_node is not None else ""
    if not year and date_node is not None:
        match = re.search(r"\b(18|19|20|21)\d{2}\b", xml_text(date_node.find("MedlineDate")))
        year = match.group(0) if match else ""
    if not year:
        return "", ""
    month_text = xml_text(date_node.find("Month")) if date_node is not None else ""
    if month_text.isdigit():
        month = max(1, min(12, int(month_text)))
    else:
        month = MONTHS.get(month_text[:3].lower(), 1)
    day_text = xml_text(date_node.find("Day")) if date_node is not None else ""
    day = max(1, min(31, int(day_text))) if day_text.isdigit() else 1
    return year, f"{int(year):04d}/{month:02d}/{day:02d}"


def split_page_text(page: str) -> tuple[str, str]:
    page = clean_text(page)
    if not page:
        return "", ""
    if "-" in page:
        start, end = page.split("-", 1)
        return start.strip(), end.strip()
    return page, ""


def pubmed_authors(article: ET.Element) -> tuple[list[str], list[str]]:
    authors: list[str] = []
    warnings: list[str] = []
    author_nodes = article.findall("MedlineCitation/Article/AuthorList/Author")
    if not author_nodes:
        return [], ["No structured author list was supplied by PubMed."]
    for index, author in enumerate(author_nodes, 1):
        collective = xml_text(author.find("CollectiveName"))
        if collective:
            authors.append(endnote_corporate_author(collective))
            continue
        family = xml_text(author.find("LastName"))
        given = xml_text(author.find("ForeName")) or xml_text(author.find("Initials"))
        suffix = xml_text(author.find("Suffix"))
        if family and given:
            name_parts = [family, given]
            if suffix:
                name_parts.append(suffix)
            authors.append(", ".join(name_parts))
            continue
        incomplete = family or given
        if incomplete:
            authors.append(incomplete)
        warnings.append(
            f"Author {index} lacks a {'family name' if not family else 'given name or initials'} in PubMed metadata."
        )
    if not authors and not warnings:
        warnings.append("No usable authors were found in PubMed metadata.")
    return authors, warnings


def candidate_from_pubmed(article: ET.Element) -> Candidate | None:
    article_node = article.find("MedlineCitation/Article")
    if article_node is None:
        return None
    pmid = xml_text(article.find("MedlineCitation/PMID"))
    journal = xml_text(article_node.find("Journal/Title")) or xml_text(
        article.find("MedlineCitation/MedlineJournalInfo/MedlineTA")
    )
    title = xml_text(article_node.find("ArticleTitle"))
    if not title or not journal:
        return None
    year, y1 = pubmed_date(article)
    start_page, end_page = split_page_text(xml_text(article_node.find("Pagination/MedlinePgn")))
    doi = ""
    for identifier in article.findall("PubmedData/ArticleIdList/ArticleId"):
        if identifier.attrib.get("IdType", "").lower() == "doi":
            doi = xml_text(identifier)
            break
    if not doi:
        for identifier in article_node.findall("ELocationID"):
            if identifier.attrib.get("EIdType", "").lower() == "doi":
                doi = xml_text(identifier)
                break
    authors, warnings = pubmed_authors(article)
    abstract = " ".join(
        xml_text(node) for node in article_node.findall("Abstract/AbstractText") if xml_text(node)
    )
    return Candidate(
        title=title,
        journal=normalize_title(journal),
        family=journal_family(journal) or "",
        year=year,
        y1=y1,
        doi=doi,
        url=f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else "",
        volume=xml_text(article_node.find("Journal/JournalIssue/Volume")),
        issue=xml_text(article_node.find("Journal/JournalIssue/Issue")),
        start_page=start_page,
        end_page=end_page,
        issn=xml_text(article_node.find("Journal/ISSN")),
        authors=authors,
        abstract=abstract,
        type=xml_text(article_node.find("PublicationTypeList/PublicationType")) or "journal-article",
        score=0.0,
        source_query=f"pmid:{pmid}",
        pmid=pmid,
        source_catalog="PubMed",
        author_warnings=warnings,
    )


def fetch_pubmed(pmids: list[str], email: str | None = None) -> list[ET.Element]:
    params = {
        "db": "pubmed",
        "id": ",".join(pmids),
        "retmode": "xml",
        "tool": "nature-citation",
    }
    if email:
        params["email"] = email
    request = Request(
        f"{PUBMED_EFETCH}?{urlencode(params)}",
        headers={"User-Agent": USER_AGENT if not email else f"codex-nature-citation/1.0 (mailto:{email})"},
    )
    with urlopen(request, timeout=45) as response:
        root = ET.fromstring(response.read())
    return list(root.findall("PubmedArticle"))


def dedupe(candidates: list[Candidate]) -> list[Candidate]:
    output: list[Candidate] = []
    positions: dict[str, int] = {}
    for candidate in candidates:
        if not candidate.key:
            continue
        if candidate.key not in positions:
            positions[candidate.key] = len(output)
            output.append(candidate)
            continue
        existing_index = positions[candidate.key]
        existing = output[existing_index]
        existing_quality = (not existing.author_warnings, len(existing.authors), bool(existing.doi))
        candidate_quality = (not candidate.author_warnings, len(candidate.authors), bool(candidate.doi))
        if candidate_quality > existing_quality:
            output[existing_index] = candidate
    return output


def author_integrity_issues(candidates: list[Candidate]) -> list[str]:
    issues: list[str] = []
    for candidate in candidates:
        identifier = candidate.doi or (f"PMID {candidate.pmid}" if candidate.pmid else candidate.title)
        candidate_issues = list(candidate.author_warnings)
        if not candidate.authors and not candidate_issues:
            candidate_issues.append("No authors are present.")
        for index, author in enumerate(candidate.authors, 1):
            if "," not in author and not any(issue.startswith(f"Author {index} ") for issue in candidate_issues):
                candidate_issues.append(
                    f"Author {index} is not encoded as a complete personal name or an EndNote corporate author."
                )
        for issue in candidate_issues:
            issues.append(f"{identifier}: {issue}")
    return issues


def validate_author_integrity(candidates: list[Candidate], allow_incomplete: bool = False) -> None:
    issues = author_integrity_issues(candidates)
    if not issues or allow_incomplete:
        return
    preview = "\n".join(f"  - {issue}" for issue in issues[:12])
    remainder = f"\n  - ... and {len(issues) - 12} more issue(s)" if len(issues) > 12 else ""
    raise ValueError(
        "Author metadata integrity check failed. Export was stopped so surname-only, missing, or "
        "otherwise incomplete author data is not presented as EndNote-ready. Refetch the affected "
        "records with --pmid/--pmid-file or verify them against the publisher record. Use "
        "--allow-incomplete-authors only when the limitation is intentional.\n"
        f"{preview}{remainder}"
    )


def build_ris_record(item: Candidate) -> str:
    lines: list[str] = []
    lines.append("TY  - JOUR")
    if item.title:
        lines.append(f"TI  - {ris_escape(item.title)}")
    for author in item.authors:
        lines.append(f"AU  - {ris_escape(author)}")
    if item.journal:
        lines.append(f"T2  - {ris_escape(item.journal)}")
        lines.append(f"JO  - {ris_escape(item.journal)}")
    if item.year:
        lines.append(f"PY  - {ris_escape(item.year)}")
    if item.y1:
        lines.append(f"Y1  - {ris_escape(item.y1)}")
    if item.volume:
        lines.append(f"VL  - {ris_escape(item.volume)}")
    if item.issue:
        lines.append(f"IS  - {ris_escape(item.issue)}")
    if item.start_page:
        lines.append(f"SP  - {ris_escape(item.start_page)}")
    if item.end_page:
        lines.append(f"EP  - {ris_escape(item.end_page)}")
    if item.doi:
        lines.append(f"DO  - {ris_escape(item.doi)}")
    if item.pmid:
        lines.append(f"AN  - PMID:{ris_escape(item.pmid)}")
    if item.doi_url:
        lines.append(f"UR  - {ris_escape(item.doi_url)}")
    if item.issn:
        lines.append(f"SN  - {ris_escape(item.issn)}")
    for warning in item.author_warnings:
        lines.append(f"N1  - Author metadata warning: {ris_escape(warning)}")
    lines.append("N1  - Metadata-only candidate. Inspect abstract or publisher page before citing as support.")
    lines.append("ER  -")
    return "\n".join(lines)


def write_ris(candidates: list[Candidate], path: Path, allow_incomplete_authors: bool = False) -> None:
    validate_author_integrity(candidates, allow_incomplete=allow_incomplete_authors)
    lines: list[str] = []
    for item in candidates:
        lines.append(build_ris_record(item))
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def build_enw_record(item: Candidate) -> str:
    lines: list[str] = []
    lines.append("%0 Journal Article")
    if item.title:
        lines.append(f"%T {ris_escape(item.title)}")
    for author in item.authors:
        lines.append(f"%A {ris_escape(author)}")
    if item.journal:
        lines.append(f"%J {ris_escape(item.journal)}")
    if item.volume:
        lines.append(f"%V {ris_escape(item.volume)}")
    if item.issue:
        lines.append(f"%N {ris_escape(item.issue)}")
    if item.start_page and item.end_page:
        lines.append(f"%P {ris_escape(item.start_page)}-{ris_escape(item.end_page)}")
    elif item.start_page:
        lines.append(f"%P {ris_escape(item.start_page)}")
    if item.year:
        lines.append(f"%D {ris_escape(item.year)}")
    if item.issn:
        lines.append(f"%@ {ris_escape(item.issn)}")
    if item.doi:
        lines.append(f"%R {ris_escape(item.doi)}")
    if item.pmid:
        lines.append(f"%M PMID:{ris_escape(item.pmid)}")
    if item.doi_url:
        lines.append(f"%U {ris_escape(item.doi_url)}")
    return "\n".join(lines)


def write_enw(candidates: list[Candidate], path: Path, allow_incomplete_authors: bool = False) -> None:
    validate_author_integrity(candidates, allow_incomplete=allow_incomplete_authors)
    lines: list[str] = []
    for item in candidates:
        lines.append(build_enw_record(item))
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def build_zotero_rdf_article(item: Candidate) -> str:
    lines: list[str] = [f'    <bib:Article rdf:about={quoteattr(item.article_resource)}>']
    lines.append("        <z:itemType>journalArticle</z:itemType>")
    if item.journal:
        lines.append(f'        <dcterms:isPartOf rdf:resource={quoteattr(item.journal_resource)}/>')
    if item.authors:
        lines.append("        <bib:authors>")
        lines.append("            <rdf:Seq>")
        for author in item.authors:
            family, given = split_author_parts(author)
            lines.append("                <rdf:li>")
            lines.append("                    <foaf:Person>")
            if family:
                lines.append(f"                        <foaf:surname>{xml_escape(family)}</foaf:surname>")
            if given:
                lines.append(f"                        <foaf:givenName>{xml_escape(given)}</foaf:givenName>")
            lines.append("                    </foaf:Person>")
            lines.append("                </rdf:li>")
        lines.append("            </rdf:Seq>")
        lines.append("        </bib:authors>")
    if item.title:
        lines.append(f"        <dc:title>{xml_escape(item.title)}</dc:title>")
    date_value = zotero_date_value(item)
    if date_value:
        lines.append(f"        <dc:date>{xml_escape(date_value)}</dc:date>")
    lines.append(f"        <z:libraryCatalog>{xml_escape(item.source_catalog)}</z:libraryCatalog>")
    if item.identifier_url:
        lines.append("        <dc:identifier>")
        lines.append("            <dcterms:URI>")
        lines.append(f"                <rdf:value>{xml_escape(item.identifier_url)}</rdf:value>")
        lines.append("            </dcterms:URI>")
        lines.append("        </dc:identifier>")
    if item.doi:
        lines.append(f"        <dc:identifier>{xml_escape(f'DOI {item.doi}')}</dc:identifier>")
    if item.page_range:
        lines.append(f"        <bib:pages>{xml_escape(item.page_range)}</bib:pages>")
    lines.append(f"        <z:citationKey>{xml_escape(item.zotero_citation_key)}</z:citationKey>")
    lines.append("    </bib:Article>")
    return "\n".join(lines)


def build_zotero_rdf_journal(item: Candidate) -> str:
    lines: list[str] = [f'    <bib:Journal rdf:about={quoteattr(item.journal_resource)}>']
    if item.volume:
        lines.append(f"        <prism:volume>{xml_escape(item.volume)}</prism:volume>")
    if item.journal:
        lines.append(f"        <dc:title>{xml_escape(item.journal)}</dc:title>")
    if item.issue:
        lines.append(f"        <prism:number>{xml_escape(item.issue)}</prism:number>")
    if item.issn:
        lines.append(f"        <dc:identifier>{xml_escape(f'ISSN {item.issn}')}</dc:identifier>")
    lines.append("    </bib:Journal>")
    return "\n".join(lines)


def build_zotero_rdf_document(candidates: list[Candidate]) -> str:
    root_open = [
        "<rdf:RDF",
        *(f' xmlns:{prefix}="{uri}"' for prefix, uri in ZOTERO_RDF_NS.items()),
        ">",
    ]
    journal_map: dict[str, str] = {}
    article_blocks: list[str] = []
    for item in candidates:
        article_blocks.append(build_zotero_rdf_article(item))
        if item.journal and item.journal_resource not in journal_map:
            journal_map[item.journal_resource] = build_zotero_rdf_journal(item)
    sections = ["".join(root_open), *article_blocks, *journal_map.values(), "</rdf:RDF>"]
    return "\n".join(section for section in sections if section)


def write_zotero_rdf(candidates: list[Candidate], path: Path, allow_incomplete_authors: bool = False) -> None:
    validate_author_integrity(candidates, allow_incomplete=allow_incomplete_authors)
    path.write_text(build_zotero_rdf_document(candidates), encoding="utf-8")


def read_text_inputs(args: argparse.Namespace) -> str:
    parts: list[str] = []
    if args.text:
        parts.extend(args.text)
    if args.text_file:
        parts.append(Path(args.text_file).read_text(encoding="utf-8"))
    return "\n\n".join(part for part in parts if part.strip())


def read_claims(args: argparse.Namespace) -> list[str]:
    claims: list[str] = []
    if args.claim:
        claims.extend(args.claim)
    if args.claim_file:
        for line in Path(args.claim_file).read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                claims.append(line)
    return claims


def read_dois(args: argparse.Namespace) -> list[str]:
    dois: list[str] = []
    if args.doi:
        dois.extend(args.doi)
    if args.doi_file:
        for line in Path(args.doi_file).read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                dois.append(line)
    cleaned = []
    for doi in dois:
        doi = doi.strip()
        doi = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", doi, flags=re.IGNORECASE)
        if doi:
            cleaned.append(doi)
    return cleaned


def read_pmids(args: argparse.Namespace) -> list[str]:
    raw_pmids: list[str] = []
    if args.pmid:
        raw_pmids.extend(args.pmid)
    if args.pmid_file:
        for line in Path(args.pmid_file).read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                raw_pmids.append(line)
    pmids: list[str] = []
    seen: set[str] = set()
    for value in raw_pmids:
        normalized = re.sub(r"^PMID\s*:\s*", "", value.strip(), flags=re.IGNORECASE)
        normalized = re.sub(r"^https?://pubmed\.ncbi\.nlm\.nih\.gov/", "", normalized, flags=re.IGNORECASE)
        normalized = normalized.strip("/ ")
        if not re.fullmatch(r"\d+", normalized):
            raise ValueError(f"Invalid PMID: {value}")
        if normalized not in seen:
            seen.add(normalized)
            pmids.append(normalized)
    return pmids


def build_segments(args: argparse.Namespace) -> list[Segment]:
    text = read_text_inputs(args)
    segments = segment_text(text, max_chars=args.segment_chars) if text else []
    claims = read_claims(args)
    for claim in claims:
        cleaned = clean_text(claim)
        if cleaned:
            segments.append(
                Segment(
                    id=f"S{len(segments) + 1:03d}",
                    text=cleaned,
                    search_query=query_from_segment(cleaned),
                    order=len(segments) + 1,
                )
            )
    return segments


def search_segment(segment: Segment, args: argparse.Namespace) -> tuple[list[Candidate], list[dict[str, str]]]:
    errors: list[dict[str, str]] = []
    candidates: list[Candidate] = []
    queries = [segment.search_query, *fallback_queries_from_segment(segment.text)]
    seen_queries: set[str] = set()
    for query in queries:
        normalized_query = query.strip().lower()
        if not normalized_query or normalized_query in seen_queries:
            continue
        seen_queries.add(normalized_query)
        try:
            items = retry_with_backoff(
                lambda: fetch_crossref(
                    query,
                    rows=args.rows,
                    mailto=args.mailto,
                    from_year=args.from_year,
                    to_year=args.to_year,
                ),
                max_retries=args.max_retries,
            )
        except Exception as exc:  # noqa: BLE001
            errors.append({"segment_id": segment.id, "query": query, "error": str(exc)})
            continue
        for item in items:
            candidate = candidate_from_crossref(item, source_query=query)
            if candidate and in_scope(candidate.journal, args.scope):
                candidates.append(candidate)
        if dedupe(candidates):
            break
    return dedupe(candidates)[: args.per_segment], errors


def build_mapping(segments: list[Segment], args: argparse.Namespace) -> tuple[list[dict[str, Any]], list[Candidate], list[dict[str, str]]]:
    mapping: list[dict[str, Any]] = []
    all_candidates: list[Candidate] = []
    errors: list[dict[str, str]] = []
    for segment in segments:
        candidates, segment_errors = search_segment(segment, args)
        errors.extend(segment_errors)
        all_candidates.extend(candidates)
        mapping.append(
            {
                "segment": segment,
                "references": candidates,
                "suggested_insert_text": " ".join(candidate.citation_marker for candidate in candidates[: args.citations_per_segment]),
            }
        )
        if args.sleep:
            time.sleep(args.sleep)
    return mapping, dedupe(all_candidates), errors


def summarize_mapping(mapping: list[dict[str, Any]], references: list[Candidate], errors: list[dict[str, str]]) -> str:
    return (
        f"segments={len(mapping)} "
        f"references={len(references)} "
        f"errors={len(errors)}"
    )


def write_export_checkpoint(
    outdir: Path,
    base_path: Path,
    export_format: str,
    references: list[Candidate],
    allow_incomplete_authors: bool = False,
) -> Path:
    partial_output = make_partial_path(base_path)
    if export_format == "enw":
        write_enw(references, partial_output, allow_incomplete_authors=allow_incomplete_authors)
    elif export_format == "ris":
        write_ris(references, partial_output, allow_incomplete_authors=allow_incomplete_authors)
    else:
        write_zotero_rdf(references, partial_output, allow_incomplete_authors=allow_incomplete_authors)
    return partial_output


def write_final_artifacts(
    mapping: list[dict[str, Any]],
    references: list[Candidate],
    outdir: Path,
    output_path: Path,
    args: argparse.Namespace,
    errors: list[dict[str, str]],
    skipped_segments: int = 0,
) -> tuple[Path, Path, Path, Path]:
    artifact_base = outdir / (output_path.stem if output_path.stem else "citation")
    json_payload = mapping_to_json(mapping, references, args, errors)
    if skipped_segments:
        json_payload["notes"].append(f"Skipped {skipped_segments} segment(s) because --max-segments was set.")
    json_path = artifact_base.with_suffix(".json")
    tsv_path = artifact_base.with_suffix(".tsv")
    report_path = artifact_base.with_suffix(".md")
    html_path = artifact_base.with_suffix(".html")
    json_path.write_text(json.dumps(json_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    write_mapping_tsv(mapping, tsv_path)
    write_report(mapping, report_path, args.scope, len(references), args.format, output_path.name)
    write_html(mapping, references, outdir, html_path, output_path, args.format)
    return json_path, tsv_path, report_path, html_path


def process_segment_batches(
    segments: list[Segment],
    args: argparse.Namespace,
    outdir: Path,
    base_path: Path,
) -> tuple[list[dict[str, Any]], list[Candidate], list[dict[str, str]]]:
    batch_size = resolve_batch_size(len(segments), args)
    batches = chunk_segments(segments, batch_size)
    mapping: list[dict[str, Any]] = []
    references: list[Candidate] = []
    errors: list[dict[str, str]] = []
    if not batches:
        return mapping, references, errors

    for batch_index, batch in enumerate(batches, 1):
        print(
            f"Processing batch {batch_index}/{len(batches)}: segments {batch[0].order}-{batch[-1].order} ({len(batch)} segments)..."
        )
        batch_mapping, batch_references, batch_errors = build_mapping(batch, args)
        mapping.extend(batch_mapping)
        references = dedupe([*references, *batch_references])
        errors.extend(batch_errors)
        try:
            partial_output = write_export_checkpoint(
                outdir,
                base_path,
                args.format,
                references,
                allow_incomplete_authors=args.allow_incomplete_authors,
            )
        except ValueError as exc:
            partial_output = None
            print(f"  Checkpoint not written: {str(exc).splitlines()[0]}", file=sys.stderr)
        print(
            f"  Batch {batch_index} done: {sum(len(entry['references']) for entry in batch_mapping)} candidates, "
            f"cumulative {len(references)} unique refs."
        )
        if partial_output:
            print(f"  Checkpoint saved: {partial_output}")
    return mapping, references, errors


def fetch_doi_candidates(dois: list[str], args: argparse.Namespace) -> tuple[list[Candidate], list[dict[str, str]]]:
    candidates: list[Candidate] = []
    errors: list[dict[str, str]] = []
    for doi in dois:
        try:
            item = retry_with_backoff(
                lambda: fetch_crossref_doi(doi, mailto=args.mailto),
                max_retries=args.max_retries,
            )
        except Exception as exc:  # noqa: BLE001
            errors.append({"doi": doi, "error": str(exc)})
            continue
        candidate = candidate_from_crossref(item, source_query=f"doi:{doi}")
        if candidate:
            candidates.append(candidate)
        if args.sleep:
            time.sleep(args.sleep)
    return dedupe(candidates), errors


def fetch_pubmed_candidates(pmids: list[str], args: argparse.Namespace) -> tuple[list[Candidate], list[dict[str, str]]]:
    candidates: list[Candidate] = []
    errors: list[dict[str, str]] = []
    for offset in range(0, len(pmids), 100):
        batch = pmids[offset : offset + 100]
        try:
            articles = retry_with_backoff(
                lambda: fetch_pubmed(batch, email=args.ncbi_email or args.mailto),
                max_retries=args.max_retries,
            )
        except Exception as exc:  # noqa: BLE001
            errors.append({"pmids": ",".join(batch), "error": str(exc)})
            continue
        returned: set[str] = set()
        for article in articles:
            candidate = candidate_from_pubmed(article)
            if candidate:
                candidates.append(candidate)
                if candidate.pmid:
                    returned.add(candidate.pmid)
        for missing in set(batch) - returned:
            errors.append({"pmid": missing, "error": "PubMed returned no usable journal-article metadata."})
        if args.sleep and offset + 100 < len(pmids):
            time.sleep(args.sleep)
    return dedupe(candidates), errors


def mapping_to_json(mapping: list[dict[str, Any]], references: list[Candidate], args: argparse.Namespace, errors: list[dict[str, str]]) -> dict[str, Any]:
    return {
        "scope": args.scope,
        "from_year": args.from_year,
        "to_year": args.to_year,
        "export_format": args.format,
        "segment_count": len(mapping),
        "reference_count": len(references),
        "segments": [
            {
                **entry["segment"].as_dict(),
                "suggested_insert_text": entry["suggested_insert_text"],
                "references": [candidate.as_dict() for candidate in entry["references"]],
            }
            for entry in mapping
        ],
        "references": [candidate.as_dict() for candidate in references],
        "errors": errors,
        "notes": [
            "Candidates are retrieved from Crossref and/or PubMed metadata and require abstract/full-text screening before citation.",
            "Author metadata passes a strict integrity gate unless --allow-incomplete-authors is explicitly set.",
            "Supported reference-manager exports: ENW, RIS, and Zotero RDF.",
        ],
    }


def write_mapping_tsv(mapping: list[dict[str, Any]], path: Path) -> None:
    fields = [
        "segment_id",
        "segment_order",
        "segment_text",
        "search_query",
        "suggested_insert_text",
        "citation_marker",
        "support_grade",
        "title",
        "journal",
        "family",
        "year",
        "doi",
        "pmid",
        "doi_url",
        "authors",
        "score",
        "screening_note",
    ]
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, delimiter="\t")
        writer.writeheader()
        for entry in mapping:
            segment: Segment = entry["segment"]
            if not entry["references"]:
                writer.writerow(
                    {
                        "segment_id": segment.id,
                        "segment_order": segment.order,
                        "segment_text": segment.text,
                        "search_query": segment.search_query,
                        "suggested_insert_text": "",
                        "support_grade": "no candidate",
                        "screening_note": "No in-scope candidate found in Crossref metadata search.",
                    }
                )
            for candidate in entry["references"]:
                writer.writerow(
                    {
                        "segment_id": segment.id,
                        "segment_order": segment.order,
                        "segment_text": segment.text,
                        "search_query": segment.search_query,
                        "suggested_insert_text": entry["suggested_insert_text"],
                        "citation_marker": candidate.citation_marker,
                        "support_grade": "metadata-only candidate",
                        "title": candidate.title,
                        "journal": candidate.journal,
                        "family": candidate.family,
                        "year": candidate.year,
                        "doi": candidate.doi,
                        "pmid": candidate.pmid,
                        "doi_url": candidate.doi_url,
                        "authors": "; ".join(candidate.authors[:10]),
                        "score": candidate.score,
                        "screening_note": "Inspect abstract/publisher page before citing this paper as support.",
                    }
                )


def write_report(
    mapping: list[dict[str, Any]],
    path: Path,
    scope: str,
    reference_count: int,
    export_format: str,
    output_name: str,
) -> None:
    lines = [
        "# Nature Citation Report",
        "",
        "## Search Scope",
        "",
        f"- Scope: `{scope}`",
        f"- Segments: {len(mapping)}",
        f"- Unique references exported: {reference_count}",
        "- Sources: Crossref metadata search and optional PubMed PMID retrieval",
        "- Author integrity: incomplete or surname-only structured names are blocked by default.",
        "- Support grade: all rows are `metadata-only candidate` until abstract/full text is checked.",
        "",
        "## Segment-to-Reference Map",
        "",
    ]
    for entry in mapping:
        segment: Segment = entry["segment"]
        lines.extend([f"### {segment.id}", "", segment.text, ""])
        if entry["suggested_insert_text"]:
            lines.append(f"Suggested insert text: `{entry['suggested_insert_text']}`")
            lines.append("")
        if not entry["references"]:
            lines.extend(["- No in-scope candidate found.", ""])
            continue
        for candidate in entry["references"]:
            lines.extend(
                [
                    f"- {candidate.citation_marker} {candidate.title}. *{candidate.journal}* ({candidate.year}). {candidate.doi_url}",
                    f"  - Family: {candidate.family or 'Unclassified'}",
                    "  - Support grade: metadata-only candidate",
                ]
            )
        lines.append("")
    lines.extend(
        [
            "## Export",
            "",
            f"- Output file: `{output_name}`",
            f"- Format: `{export_format}` ({export_label(export_format)})",
            "- RIS is the default inspectable exchange format and imports into EndNote with Reference Manager (RIS).",
            "- ENW is suitable for EndNote tagged import when explicitly selected.",
            "- Zotero RDF is suitable for direct Zotero import.",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def rel_link(path: Path, outdir: Path) -> str:
    try:
        return html.escape(path.relative_to(outdir).as_posix())
    except ValueError:
        return html.escape(path.as_posix())


def write_html(
    mapping: list[dict[str, Any]],
    references: list[Candidate],
    outdir: Path,
    path: Path,
    export_path: Path,
    export_format: str,
) -> None:
    payload = {
        "segmentCount": len(mapping),
        "referenceCount": len(references),
        "defaultExportFormat": export_format,
        "defaultExportName": export_path.name,
        "references": [candidate.as_dict() for candidate in references],
        "segments": [
            {
                "id": entry["segment"].id,
                "order": entry["segment"].order,
                "text": entry["segment"].text,
                "query": entry["segment"].search_query,
                "suggestedInsertText": entry["suggested_insert_text"],
                "references": [candidate.as_dict() for candidate in entry["references"]],
            }
            for entry in mapping
        ],
    }
    payload_json = json.dumps(payload, ensure_ascii=False).replace("</script>", "<\\/script>")
    cards: list[str] = []
    for entry in mapping:
        segment: Segment = entry["segment"]
        refs = entry["references"]
        ref_items = []
        if refs:
            for idx, candidate in enumerate(refs, 1):
                record_json = html.escape(json.dumps(candidate.as_dict(), ensure_ascii=False))
                ref_items.append(
                    f"""
                    <article
                      class="reference"
                      data-key="{html.escape(candidate.key)}"
                      data-title="{html.escape(candidate.title)}"
                      data-journal="{html.escape(candidate.journal)}"
                      data-doi="{html.escape(candidate.doi)}"
                      data-year="{html.escape(candidate.year)}"
                      data-authors="{html.escape('; '.join(candidate.authors[:10]))}"
                      data-segment="{html.escape(segment.text)}"
                      data-record="{record_json}"
                    >
                      <div class="ref-controls">
                        <label class="check-row"><input type="checkbox"> Select</label>
                        <span class="marker">{html.escape(candidate.citation_marker)}</span>
                      </div>
                      <div class="ref-topline">
                        <span class="grade">metadata-only</span>
                        <span>{idx} / {len(refs)}</span>
                      </div>
                      <h3>{html.escape(candidate.title)}</h3>
                      <p class="meta">{html.escape(candidate.journal)} · {html.escape(candidate.family or "Unclassified")} · {html.escape(candidate.year or "n.d.")}</p>
                      <p class="authors">{html.escape("; ".join(candidate.authors[:6]))}</p>
                      <p class="abstract">{html.escape(candidate.abstract[:380] + ('...' if len(candidate.abstract) > 380 else '')) if candidate.abstract else 'No abstract snippet available from Crossref metadata.'}</p>
                      <a href="{html.escape(candidate.doi_url)}" target="_blank" rel="noreferrer">{html.escape(candidate.doi_url)}</a>
                    </article>
                    """
                )
        else:
            ref_items.append('<p class="empty">No in-scope candidate was found for this segment.</p>')
        cards.append(
            f"""
            <section class="segment-card" id="{html.escape(segment.id)}">
              <div class="segment-head">
                <span class="segment-id">{html.escape(segment.id)} · Sentence {segment.order}</span>
                <span class="query">Query: {html.escape(segment.search_query)}</span>
              </div>
              <p class="segment-text">{html.escape(segment.text)}</p>
              <div class="insert-row">
                <span>Suggested insert</span>
                <code>{html.escape(entry["suggested_insert_text"] or "No candidate")}</code>
              </div>
              <div class="references-grid">
                {"".join(ref_items)}
              </div>
            </section>
            """
        )

    export_link = rel_link(export_path, outdir)
    export_label_text = html.escape(export_label(export_format))
    export_file_label = html.escape(export_path.name)
    doc = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Nature Citation Browser</title>
  <style>
    :root {{
      --ink: #1f1f1f;
      --muted: #5f6368;
      --paper: #f8f9fa;
      --panel: #ffffff;
      --line: #dadce0;
      --accent: #1a73e8;
      --accent-2: #d93025;
      --soft: #e8f0fe;
      --soft-2: #f1f3f4;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      color: var(--ink);
      background: var(--paper);
      font-family: Arial, Helvetica, sans-serif;
      line-height: 1.45;
    }}
    header {{
      padding: 26px clamp(16px, 4vw, 40px) 16px;
      border-bottom: 1px solid var(--line);
      background: var(--panel);
    }}
    h1 {{
      margin: 0 0 8px;
      font-size: clamp(28px, 3vw, 42px);
      font-weight: 500;
      letter-spacing: 0;
    }}
    .subhead {{
      max-width: 980px;
      margin: 0;
      color: var(--muted);
      font-size: 15px;
    }}
    .toolbar {{
      display: grid;
      grid-template-columns: 260px minmax(0, 1fr) auto;
      gap: 14px;
      align-items: start;
      padding: 16px clamp(16px, 4vw, 40px);
      background: var(--panel);
      border-bottom: 1px solid var(--line);
      position: sticky;
      top: 0;
      z-index: 8;
    }}
    .toolbar a, .toolbar button, .toolbar input, .toolbar select {{
      appearance: none;
      border: 1px solid var(--line);
      background: var(--panel);
      color: var(--ink);
      border-radius: 20px;
      padding: 10px 14px;
      font: 500 14px Arial, Helvetica, sans-serif;
      text-decoration: none;
    }}
    .toolbar button, .toolbar a {{
      cursor: pointer;
    }}
    .toolbar button.primary, .toolbar a.primary {{
      background: var(--accent);
      border-color: var(--accent);
      color: white;
    }}
    .filters {{
      display: grid;
      gap: 10px;
    }}
    .filter-group {{
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
      align-items: center;
    }}
    .search-input {{
      width: 100%;
    }}
    .summary-strip {{
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
      align-items: center;
      justify-content: center;
    }}
    .pill {{
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 9px 12px;
      background: var(--soft-2);
      font-size: 13px;
    }}
    .layout {{
      display: grid;
      grid-template-columns: minmax(0, 1fr) 320px;
      gap: 18px;
      padding: 22px clamp(16px, 4vw, 40px) 48px;
    }}
    main {{
      display: grid;
      gap: 14px;
      align-content: start;
    }}
    aside {{
      position: sticky;
      top: 124px;
      align-self: start;
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 12px;
      padding: 16px;
      box-shadow: 0 2px 8px rgba(60, 64, 67, 0.12);
    }}
    .segment-card {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 12px;
      padding: 18px 20px;
      box-shadow: 0 1px 4px rgba(60, 64, 67, 0.12);
    }}
    .segment-head {{
      display: flex;
      gap: 12px;
      align-items: start;
      justify-content: space-between;
      flex-wrap: wrap;
      margin-bottom: 10px;
    }}
    .segment-id {{
      background: var(--soft);
      color: var(--accent);
      border-radius: 999px;
      padding: 5px 10px;
      font-size: 12px;
      font-weight: 700;
    }}
    .query {{
      color: var(--muted);
      font-size: 12px;
      max-width: 780px;
    }}
    .segment-text {{
      margin: 0 0 14px;
      font-size: 18px;
    }}
    .insert-row {{
      display: grid;
      gap: 6px;
      margin: 12px 0 16px;
      padding: 12px;
      background: var(--soft);
      border-radius: 10px;
    }}
    .insert-row span {{
      color: var(--muted);
      font-size: 12px;
      font-weight: 700;
    }}
    code {{
      white-space: normal;
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      font-size: 14px;
    }}
    .references-grid {{
      display: grid;
      gap: 12px;
    }}
    .reference {{
      border: 1px solid var(--line);
      border-radius: 12px;
      padding: 14px 16px;
      background: #fff;
    }}
    .ref-topline {{
      display: flex;
      justify-content: space-between;
      gap: 10px;
      margin-bottom: 8px;
      font-size: 12px;
    }}
    .marker {{
      color: var(--accent);
      font-weight: 800;
    }}
    .grade {{
      color: var(--accent-2);
      font-weight: 800;
    }}
    .ref-controls {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 12px;
      margin-bottom: 10px;
    }}
    .check-row {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      font-size: 13px;
      color: var(--muted);
    }}
    h3 {{
      margin: 0 0 8px;
      font-size: 19px;
      line-height: 1.35;
      font-weight: 500;
    }}
    .meta, .authors, .empty {{
      margin: 0 0 8px;
      color: var(--muted);
      font-size: 14px;
    }}
    .reference a {{
      color: var(--accent);
      overflow-wrap: anywhere;
      font-size: 14px;
      font-weight: 500;
    }}
    .abstract {{
      margin: 8px 0 0;
      color: #3c4043;
      font-size: 14px;
    }}
    .hidden {{
      display: none !important;
    }}
    .modal-overlay {{
      position: fixed;
      inset: 0;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 14px;
      background: rgba(20, 33, 31, 0.42);
      backdrop-filter: blur(3px);
      z-index: 20;
    }}
    .modal-overlay.is-hidden {{
      display: none;
    }}
    .modal-panel {{
      border: 1px solid var(--ink);
      border-radius: 8px;
      width: min(680px, calc(100vw - 28px));
      box-shadow: 0 16px 40px rgba(60, 64, 67, 0.28);
      background: var(--panel);
      color: var(--ink);
    }}
    .modal-inner {{
      padding: 24px;
    }}
    .modal-inner h2 {{
      margin: 0 0 10px;
      font-size: 28px;
    }}
    .stats {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 10px;
      margin: 18px 0;
    }}
    .stat {{
      border: 1px solid var(--line);
      border-radius: 10px;
      padding: 14px;
      background: var(--soft-2);
    }}
    .stat b {{
      display: block;
      font-size: 30px;
      line-height: 1;
    }}
    .modal-actions {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-top: 16px;
    }}
    .modal-actions a, .modal-actions button {{
      border: 1px solid var(--accent);
      background: var(--accent);
      color: #fffdf8;
      border-radius: 20px;
      padding: 10px 12px;
      font: 700 14px Arial, Helvetica, sans-serif;
      text-decoration: none;
      cursor: pointer;
    }}
    .modal-actions button {{
      background: var(--panel);
      color: var(--accent);
    }}
    .selection-title {{
      margin: 0 0 10px;
      font-size: 16px;
      font-weight: 700;
    }}
    .selection-meta {{
      margin: 0 0 14px;
      color: var(--muted);
      font-size: 13px;
    }}
    .selection-list {{
      display: grid;
      gap: 10px;
      margin-bottom: 14px;
      max-height: 48vh;
      overflow: auto;
    }}
    .selection-item {{
      border: 1px solid var(--line);
      border-radius: 10px;
      padding: 10px;
      background: var(--soft-2);
    }}
    .selection-item h4 {{
      margin: 0 0 6px;
      font-size: 14px;
      font-weight: 600;
    }}
    .selection-item p {{
      margin: 0;
      color: var(--muted);
      font-size: 12px;
    }}
    .empty-state {{
      color: var(--muted);
      font-size: 14px;
      padding: 12px;
      border: 1px dashed var(--line);
      border-radius: 10px;
      background: var(--soft-2);
    }}
    @media (max-width: 680px) {{
      .stats {{ grid-template-columns: 1fr; }}
      .segment-head {{ align-items: flex-start; }}
    }}
    @media (max-width: 1040px) {{
      .toolbar {{
        grid-template-columns: 1fr;
      }}
      .summary-strip {{
        justify-content: flex-start;
      }}
      .layout {{
        grid-template-columns: 1fr;
      }}
      aside {{
        position: static;
      }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>Nature Citation Browser</h1>
    <p class="subhead">Scholar-style browsing for strict Nature/CNS-family candidates. Filter by year, compare related hits, choose the references you actually want, then download them as RIS, ENW, or Zotero RDF.</p>
  </header>
  <nav class="toolbar">
    <div class="filters">
      <input id="queryFilter" class="search-input" type="text" placeholder="Filter by title, journal, DOI, author, or segment text">
      <div class="filter-group">
        <label for="yearFrom">From year</label>
        <input id="yearFrom" type="number" min="1900" max="2100" placeholder="2019">
        <label for="yearTo">To year</label>
        <input id="yearTo" type="number" min="1900" max="2100" placeholder="2026">
        <button id="applyFilters" type="button">Apply filters</button>
        <button id="clearFilters" type="button">Clear</button>
      </div>
      <div class="filter-group">
        <label class="check-row"><input id="selectedOnly" type="checkbox"> Show selected only</label>
      </div>
    </div>
    <div class="summary-strip">
      <span class="pill"><strong id="visibleCount">0</strong> visible</span>
      <span class="pill"><strong id="selectedCount">0</strong> selected</span>
      <span class="pill"><strong>{payload["segmentCount"]}</strong> segments</span>
    </div>
    <div class="summary-strip">
      <button id="openSummary" type="button">Guide</button>
      <label for="downloadFormat">Format</label>
      <select id="downloadFormat">
        <option value="ris">RIS</option>
        <option value="enw">ENW</option>
        <option value="zotero-rdf">Zotero RDF</option>
      </select>
      <a class="primary" id="downloadSelected" href="{export_link}" download="{export_file_label}">Download selected / all</a>
    </div>
  </nav>
  <div class="layout">
    <main id="results">
      {"".join(cards)}
    </main>
    <aside>
      <h2 class="selection-title">Selected references</h2>
      <p class="selection-meta">Tick the references you want. The download button exports the selection in the chosen format. If nothing is selected, it exports all references.</p>
      <div id="selectionList" class="selection-list"></div>
      <div id="selectionEmpty" class="empty-state">No references selected yet.</div>
    </aside>
  </div>
  <div class="modal-overlay" id="summaryModal" aria-hidden="false">
    <div class="modal-panel" role="dialog" aria-modal="true" aria-labelledby="summaryTitle">
      <div class="modal-inner">
        <h2 id="summaryTitle">Ready to review citations</h2>
        <p>This page behaves more like a compact Scholar browser: filter by year, browse related results, select the citations you trust, and download them as ENW, RIS, or Zotero RDF.</p>
        <div class="stats">
          <div class="stat"><b>{payload["segmentCount"]}</b><span>segments</span></div>
          <div class="stat"><b>{payload["referenceCount"]}</b><span>unique references</span></div>
        </div>
        <p class="meta">Important: these are still metadata-level candidates. Selection is your decision, not an automatic validity guarantee.</p>
        <div class="modal-actions">
          <a href="{export_link}" download>Download original {export_label_text} file</a>
          <button id="closeSummary" type="button" onclick="document.getElementById('summaryModal').classList.add('is-hidden'); document.getElementById('summaryModal').setAttribute('aria-hidden', 'true');">Start browsing</button>
        </div>
      </div>
    </div>
  </div>
  <script id="citationData" type="application/json">{payload_json}</script>
  <script>
    const data = JSON.parse(document.getElementById('citationData').textContent);
    const modal = document.getElementById('summaryModal');
    const closeSummary = document.getElementById('closeSummary');
    const openSummary = document.getElementById('openSummary');
    const yearFromInput = document.getElementById('yearFrom');
    const yearToInput = document.getElementById('yearTo');
    const queryFilterInput = document.getElementById('queryFilter');
    const selectedOnlyInput = document.getElementById('selectedOnly');
    const applyFiltersButton = document.getElementById('applyFilters');
    const clearFiltersButton = document.getElementById('clearFilters');
    const visibleCount = document.getElementById('visibleCount');
    const selectedCount = document.getElementById('selectedCount');
    const selectionList = document.getElementById('selectionList');
    const selectionEmpty = document.getElementById('selectionEmpty');
    const downloadSelected = document.getElementById('downloadSelected');
    const downloadFormat = document.getElementById('downloadFormat');
    const selectedMap = new Map();
    let currentDownloadUrl = null;

    downloadFormat.value = data.defaultExportFormat || 'ris';

    function showModal() {{
      if (modal) {{
        modal.classList.remove('is-hidden');
        modal.setAttribute('aria-hidden', 'false');
      }}
    }}
    function hideModal() {{
      if (modal) {{
        modal.classList.add('is-hidden');
        modal.setAttribute('aria-hidden', 'true');
      }}
    }}
    window.addEventListener('DOMContentLoaded', showModal);
    openSummary.addEventListener('click', showModal);
    closeSummary.addEventListener('click', hideModal);
    modal.addEventListener('click', (event) => {{
      if (event.target === modal) {{
        hideModal();
      }}
    }});

    function revokeDownloadUrl() {{
      if (currentDownloadUrl) {{
        URL.revokeObjectURL(currentDownloadUrl);
        currentDownloadUrl = null;
      }}
    }}

    function selectedItems() {{
      return Array.from(selectedMap.values());
    }}

    function exportItems() {{
      const items = selectedItems();
      return items.length ? items : (data.references || []);
    }}

    function buildEnw(items) {{
      return items.map((item) => item.enw_record).join('\\n\\n');
    }}

    function buildRis(items) {{
      return items.map((item) => item.ris_record).join('\\n\\n');
    }}

    function buildZoteroRdf(items) {{
      const journals = new Map();
      const articles = [];
      for (const item of items) {{
        if (item.zotero_rdf_article) {{
          articles.push(item.zotero_rdf_article);
        }}
        if (item.journal_resource && item.zotero_rdf_journal && !journals.has(item.journal_resource)) {{
          journals.set(item.journal_resource, item.zotero_rdf_journal);
        }}
      }}
      const header = [
        '<rdf:RDF',
        ' xmlns:rdf="{ZOTERO_RDF_NS["rdf"]}"',
        ' xmlns:z="{ZOTERO_RDF_NS["z"]}"',
        ' xmlns:dcterms="{ZOTERO_RDF_NS["dcterms"]}"',
        ' xmlns:bib="{ZOTERO_RDF_NS["bib"]}"',
        ' xmlns:foaf="{ZOTERO_RDF_NS["foaf"]}"',
        ' xmlns:dc="{ZOTERO_RDF_NS["dc"]}"',
        ' xmlns:prism="{ZOTERO_RDF_NS["prism"]}"',
        '>',
      ].join('');
      return [header, ...articles, ...journals.values(), '</rdf:RDF>'].join('\\n');
    }}

    function exportFileName(format, hasSelection) {{
      const base = hasSelection ? 'selected-references' : 'all-references';
      if (format === 'ris') return `${{base}}.ris`;
      if (format === 'zotero-rdf') return `${{base}}.rdf`;
      return `${{base}}.enw`;
    }}

    function updateDownloadLink() {{
      const items = exportItems();
      const format = downloadFormat.value || 'enw';
      const hasSelection = selectedItems().length > 0;
      let content = '';
      if (format === 'ris') {{
        content = buildRis(items);
      }} else if (format === 'zotero-rdf') {{
        content = buildZoteroRdf(items);
      }} else {{
        content = buildEnw(items);
      }}
      revokeDownloadUrl();
      currentDownloadUrl = URL.createObjectURL(new Blob([content], {{ type: 'text/plain;charset=utf-8' }}));
      downloadSelected.href = currentDownloadUrl;
      downloadSelected.download = exportFileName(format, hasSelection);
    }}

    function updateSelectedPanel() {{
      selectionList.innerHTML = '';
      const items = selectedItems();
      selectedCount.textContent = String(items.length);
      if (!items.length) {{
        selectionEmpty.classList.remove('hidden');
      }} else {{
        selectionEmpty.classList.add('hidden');
      }}
      for (const item of items) {{
        const wrapper = document.createElement('div');
        wrapper.className = 'selection-item';
        wrapper.innerHTML = `<h4>${{item.title}}</h4><p>${{item.journal}} · ${{item.year || 'n.d.'}}</p>`;
        selectionList.appendChild(wrapper);
      }}
      updateDownloadLink();
    }}

    function yearPass(year) {{
      const fromYear = Number(yearFromInput.value || 0);
      const toYear = Number(yearToInput.value || 0);
      const y = Number(year || 0);
      if (fromYear && (!y || y < fromYear)) return false;
      if (toYear && (!y || y > toYear)) return false;
      return true;
    }}

    function queryPass(text) {{
      const needle = queryFilterInput.value.trim().toLowerCase();
      if (!needle) return true;
      return text.toLowerCase().includes(needle);
    }}

    function applyFilters() {{
      let totalVisible = 0;
      document.querySelectorAll('.segment-card').forEach((card) => {{
        let visibleRefs = 0;
        card.querySelectorAll('.reference').forEach((ref) => {{
          const title = ref.dataset.title || '';
          const journal = ref.dataset.journal || '';
          const doi = ref.dataset.doi || '';
          const authors = ref.dataset.authors || '';
          const segmentText = ref.dataset.segment || '';
          const year = ref.dataset.year || '';
          const key = ref.dataset.key || '';
          const searchText = `${{title}} ${{journal}} ${{doi}} ${{authors}} ${{segmentText}}`;
          const matches = yearPass(year) && queryPass(searchText) && (!selectedOnlyInput.checked || selectedMap.has(key));
          ref.classList.toggle('hidden', !matches);
          if (matches) visibleRefs += 1;
        }});
        const noRefsMessage = card.querySelector('.empty');
        if (noRefsMessage) {{
          const matches = !selectedOnlyInput.checked && queryPass(card.dataset.segment || '');
          noRefsMessage.classList.toggle('hidden', !matches);
          card.classList.toggle('hidden', !matches);
          if (matches) totalVisible += 1;
          return;
        }}
        card.classList.toggle('hidden', visibleRefs === 0);
        totalVisible += visibleRefs;
      }});
      visibleCount.textContent = String(totalVisible);
    }}

    document.querySelectorAll('.reference').forEach((ref) => {{
      const checkbox = ref.querySelector('input[type="checkbox"]');
      checkbox.addEventListener('change', () => {{
        const key = ref.dataset.key;
        const record = JSON.parse(ref.dataset.record);
        if (checkbox.checked) {{
          selectedMap.set(key, record);
        }} else {{
          selectedMap.delete(key);
        }}
        updateSelectedPanel();
        applyFilters();
      }});
    }});

    applyFiltersButton.addEventListener('click', applyFilters);
    downloadFormat.addEventListener('change', updateDownloadLink);
    clearFiltersButton.addEventListener('click', () => {{
      yearFromInput.value = '';
      yearToInput.value = '';
      queryFilterInput.value = '';
      selectedOnlyInput.checked = false;
      applyFilters();
    }});
    queryFilterInput.addEventListener('input', applyFilters);
    selectedOnlyInput.addEventListener('change', applyFilters);
    yearFromInput.addEventListener('change', applyFilters);
    yearToInput.addEventListener('change', applyFilters);
    updateSelectedPanel();
    applyFilters();
  </script>
</body>
</html>
"""
    path.write_text(doc, encoding="utf-8")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Segment text and export strict Nature/CNS-family citations for EndNote or Zotero.")
    parser.add_argument("--text", action="append", help="Manuscript text to segment and cite. Can be repeated.")
    parser.add_argument("--text-file", help="UTF-8 manuscript text file.")
    parser.add_argument("--claim", action="append", help="Single claim to treat as one segment. Can be repeated.")
    parser.add_argument("--claim-file", help="UTF-8 text file with one claim per line.")
    parser.add_argument("--doi", action="append", help="Known DOI to fetch and export. Can be repeated.")
    parser.add_argument("--doi-file", help="UTF-8 text file with one DOI per line.")
    parser.add_argument("--pmid", action="append", help="Known PubMed PMID to fetch and export. Can be repeated.")
    parser.add_argument("--pmid-file", help="UTF-8 text file with one PMID per line.")
    parser.add_argument("--scope", choices=["cns", "nature", "science", "cell", "flagship"], default="cns")
    parser.add_argument("--output-file", help="Reference output file path, typically ending in .enw, .ris, or .rdf.")
    parser.add_argument("--outdir", help="Optional directory for outputs. If omitted, uses the output file parent or current directory.")
    parser.add_argument("--format", choices=EXPORT_FORMAT_CHOICES, help="Reference export format: enw, ris, or zotero-rdf. Inferred from --output-file when omitted.")
    parser.add_argument("--with-artifacts", action="store_true", help="Also generate JSON/TSV/report/HTML review artifacts.")
    parser.add_argument("--rows", type=int, default=30, help="Crossref rows per segment before journal-scope filtering.")
    parser.add_argument("--per-segment", type=int, default=3, help="Maximum candidates to keep per segment.")
    parser.add_argument("--citations-per-segment", type=int, default=2, help="Markers to include in suggested insert text.")
    parser.add_argument("--segment-chars", type=int, default=700, help="Split paragraphs longer than this many characters.")
    parser.add_argument("--max-candidates", type=int, default=80, help="Maximum deduplicated references to export.")
    parser.add_argument("--max-segments", type=int, help="Limit the number of segments processed in a single run.")
    parser.add_argument("--batch-size", type=int, help="Process segments in batches of this size.")
    parser.add_argument("--max-retries", type=int, default=2, help="Maximum retry count for Crossref requests.")
    parser.add_argument("--from-year", type=int, help="Earliest publication year.")
    parser.add_argument("--to-year", type=int, help="Latest publication year.")
    parser.add_argument("--mailto", help="Email for Crossref polite pool.")
    parser.add_argument("--ncbi-email", help="Contact email sent to NCBI E-utilities for PMID requests.")
    parser.add_argument(
        "--allow-incomplete-authors",
        action="store_true",
        help="Export despite missing/surname-only author metadata. Disabled by default to protect EndNote imports.",
    )
    parser.add_argument("--sleep", type=float, default=0.3, help="Seconds between Crossref requests.")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    segments = build_segments(args)
    dois = read_dois(args)
    try:
        pmids = read_pmids(args)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    if not segments and not dois and not pmids:
        print(
            "Provide --text, --text-file, --claim, --claim-file, --doi, --doi-file, --pmid, or --pmid-file.",
            file=sys.stderr,
        )
        return 2

    output_path = Path(args.output_file).expanduser().resolve() if args.output_file else None
    if args.outdir:
        outdir = Path(args.outdir).expanduser().resolve()
    elif output_path:
        outdir = output_path.parent
    else:
        outdir = Path.cwd().resolve()
    outdir.mkdir(parents=True, exist_ok=True)
    args.format = normalize_export_format(args.format) if args.format else infer_export_format(output_path)

    # Derive a meaningful base name from input text when no explicit output file was given
    raw_text = read_text_inputs(args)
    name_base = slug_from_text(raw_text) if not args.output_file else None

    if output_path is None:
        output_path = outdir / export_filename(args.format, base=name_base or "references")

    segments, skipped_segments = limit_segments(segments, args.max_segments or 0)
    mapping, references, errors = process_segment_batches(segments, args, outdir, output_path)
    doi_candidates, doi_errors = fetch_doi_candidates(dois, args)
    errors.extend(doi_errors)
    pubmed_candidates, pubmed_errors = fetch_pubmed_candidates(pmids, args)
    errors.extend(pubmed_errors)
    references = dedupe([*references, *doi_candidates, *pubmed_candidates])[: args.max_candidates]

    if (dois or pmids) and not references:
        print("No requested DOI/PMID records could be retrieved; no export was written.", file=sys.stderr)
        for error in errors[:5]:
            print(f"  - {error}", file=sys.stderr)
        return 4

    try:
        if args.format == "enw":
            write_enw(references, output_path, allow_incomplete_authors=args.allow_incomplete_authors)
        elif args.format == "ris":
            write_ris(references, output_path, allow_incomplete_authors=args.allow_incomplete_authors)
        else:
            write_zotero_rdf(references, output_path, allow_incomplete_authors=args.allow_incomplete_authors)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 3

    if args.with_artifacts:
        artifact_base = outdir / name_base if name_base else outdir / "citation"
        json_path, tsv_path, report_path, html_path = write_final_artifacts(
            mapping,
            references,
            outdir,
            output_path,
            args,
            errors,
            skipped_segments=skipped_segments,
        )
        print(f"Artifacts: {html_path}, {tsv_path}, {json_path}, {report_path}")

    print(f"Reference output: {output_path}")
    print(f"Export format: {args.format} ({export_label(args.format)})")
    print(f"Unique references exported: {len(references)}")
    if skipped_segments:
        print(f"Segments skipped: {skipped_segments}")
    if errors:
        detail = "; see the JSON artifact for details" if args.with_artifacts else ""
        print(f"Encountered {len(errors)} retrieval error(s){detail}.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
