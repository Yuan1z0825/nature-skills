"""Unit tests for academic search source modules and ID detection.

All external HTTP calls are mocked -- no network access required.
"""

from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------


def _make_crossref_config():
    """Return a mock Config object for CrossRef."""
    cfg = MagicMock()
    cfg.crossref_mailto = "test@example.com"
    cfg.crossref_timeout = 10
    return cfg


def _make_pubmed_config():
    """Return a mock Config object for PubMed."""
    cfg = MagicMock()
    cfg.pubmed_email = "test@example.com"
    cfg.pubmed_api_key = ""
    cfg.max_rows = 50
    return cfg


def _make_arxiv_config():
    """Return a mock Config object for arXiv."""
    cfg = MagicMock()
    cfg.arxiv_timeout = 10
    return cfg


# ===================================================================
# 1. CrossRef tests
# ===================================================================


class TestCrossRefSearch:
    """Test CrossRef search returns the unified result format."""

    @patch("sources.crossref.get_config")
    @patch("sources.crossref.requests.get")
    def test_search_returns_unified_format(self, mock_get, mock_config):
        mock_config.return_value = _make_crossref_config()

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.raise_for_status = MagicMock()
        mock_resp.json.return_value = {
            "message": {
                "total-results": 42,
                "items": [
                    {
                        "title": ["Deep Learning for NLP"],
                        "author": [
                            {"given": "Alice", "family": "Smith"},
                            {"given": "Bob", "family": "Jones"},
                        ],
                        "published-print": {"date-parts": [[2023, 6, 15]]},
                        "DOI": "10.1234/example.2023",
                        "container-title": ["Journal of AI Research"],
                        "is-referenced-by-count": 17,
                    }
                ],
            }
        }
        mock_get.return_value = mock_resp

        from sources.crossref import CrossRefSource

        source = CrossRefSource()
        result = source.search("deep learning", rows=5)

        assert "total" in result
        assert "results" in result
        assert result["total"] == 42
        assert len(result["results"]) == 1

        item = result["results"][0]
        assert item["title"] == "Deep Learning for NLP"
        assert item["authors"] == ["Alice Smith", "Bob Jones"]
        assert item["year"] == 2023
        assert item["doi"] == "10.1234/example.2023"
        assert item["journal"] == "Journal of AI Research"
        assert item["source"] == "crossref"
        assert item["citation_count"] == 17

    @patch("sources.crossref.get_config")
    @patch("sources.crossref.requests.get")
    def test_search_with_type_filter(self, mock_get, mock_config):
        mock_config.return_value = _make_crossref_config()

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.raise_for_status = MagicMock()
        mock_resp.json.return_value = {"message": {"total-results": 0, "items": []}}
        mock_get.return_value = mock_resp

        from sources.crossref import CrossRefSource

        source = CrossRefSource()
        result = source.search("test", rows=5, filter_type="journal-article")

        called_params = mock_get.call_args[1]["params"]
        assert called_params["filter"] == "type:journal-article"
        assert result["total"] == 0
        assert result["results"] == []

    @patch("sources.crossref.get_config")
    @patch("sources.crossref.requests.get")
    def test_search_empty_items(self, mock_get, mock_config):
        mock_config.return_value = _make_crossref_config()

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.raise_for_status = MagicMock()
        mock_resp.json.return_value = {
            "message": {"total-results": 0, "items": []}
        }
        mock_get.return_value = mock_resp

        from sources.crossref import CrossRefSource

        source = CrossRefSource()
        result = source.search("nonexistent query xyz")

        assert result["total"] == 0
        assert result["results"] == []

    @patch("sources.crossref.get_config")
    @patch("sources.crossref.requests.get")
    def test_get_by_doi(self, mock_get, mock_config):
        mock_config.return_value = _make_crossref_config()

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.raise_for_status = MagicMock()
        mock_resp.json.return_value = {
            "message": {
                "title": ["A Great Paper"],
                "author": [{"given": "Jane", "family": "Doe"}],
                "published-online": {"date-parts": [[2024]]},
                "DOI": "10.1038/nature12373",
                "container-title": ["Nature"],
                "abstract": "<p>We discovered something.</p>",
                "volume": "615",
                "issue": "7951",
                "page": "100-105",
                "publisher": "Springer Nature",
                "type": "journal-article",
                "references-count": 42,
                "URL": "https://doi.org/10.1038/nature12373",
            }
        }
        mock_get.return_value = mock_resp

        from sources.crossref import CrossRefSource

        source = CrossRefSource()
        detail = source.get_by_doi("10.1038/nature12373")

        assert detail["title"] == "A Great Paper"
        assert detail["doi"] == "10.1038/nature12373"
        assert detail["abstract"] == "<p>We discovered something.</p>"
        assert detail["volume"] == "615"
        assert detail["type"] == "journal-article"
        assert detail["source"] == "crossref"

    @patch("sources.crossref.get_config")
    @patch("sources.crossref.requests.get")
    def test_search_http_error(self, mock_get, mock_config):
        import requests as real_requests

        mock_config.return_value = _make_crossref_config()

        mock_resp = MagicMock()
        mock_resp.status_code = 503
        mock_resp.raise_for_status.side_effect = real_requests.HTTPError(
            response=mock_resp
        )
        mock_get.return_value = mock_resp

        from sources.crossref import CrossRefSource
        from utils.errors import DataSourceError

        source = CrossRefSource()
        with pytest.raises(DataSourceError, match="crossref"):
            source.search("test")

    @patch("sources.crossref.get_config")
    @patch("sources.crossref.requests.get")
    def test_get_citation(self, mock_get, mock_config):
        mock_config.return_value = _make_crossref_config()

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.raise_for_status = MagicMock()
        mock_resp.text = "Smith, A. (2023). Deep Learning. Nature."
        mock_get.return_value = mock_resp

        from sources.crossref import CrossRefSource

        source = CrossRefSource()
        citation = source.get_citation("10.1038/nature12373", style="nature")

        assert "Smith" in citation
        assert "2023" in citation


# ===================================================================
# 2. PubMed tests
# ===================================================================


class TestPubMedSearch:
    """Test PubMed esearch + efetch flow with WebEnv/query_key handling."""

    @patch("sources.pubmed.get_config")
    @patch("sources.pubmed._get")
    def test_search_esearch_efetch_flow(self, mock_get, mock_config):
        mock_config.return_value = _make_pubmed_config()

        # esearch response
        esearch_xml = """<?xml version="1.0"?>
        <eSearchResult>
            <Count>1</Count>
            <RetMax>1</RetMax>
            <WebEnv>ABC123_webenv</WebEnv>
            <QueryKey>1</QueryKey>
            <IdList><Id>99999999</Id></IdList>
        </eSearchResult>"""

        # efetch response
        efetch_xml = """<?xml version="1.0"?>
        <PubmedArticleSet>
            <PubmedArticle>
                <MedlineCitation>
                    <PMID>99999999</PMID>
                    <Article>
                        <ArticleTitle>Genomic Analysis of Cancer</ArticleTitle>
                        <AuthorList>
                            <Author>
                                <LastName>Wang</LastName>
                                <ForeName>Li</ForeName>
                            </Author>
                            <Author>
                                <LastName>Zhang</LastName>
                                <ForeName>Wei</ForeName>
                            </Author>
                        </AuthorList>
                        <Abstract>
                            <AbstractText>We performed whole-genome sequencing.</AbstractText>
                        </Abstract>
                        <Journal>
                            <Title>Nature Medicine</Title>
                            <JournalIssue>
                                <PubDate><Year>2024</Year></PubDate>
                            </JournalIssue>
                        </Journal>
                        <ELocationID EIdType="doi">10.1038/s41591-024-00001</ELocationID>
                    </Article>
                </MedlineCitation>
            </PubmedArticle>
        </PubmedArticleSet>"""

        esearch_resp = MagicMock()
        esearch_resp.content = esearch_xml.encode("utf-8")

        efetch_resp = MagicMock()
        efetch_resp.content = efetch_xml.encode("utf-8")

        mock_get.side_effect = [esearch_resp, efetch_resp]

        from sources.pubmed import PubMedSource

        source = PubMedSource()
        result = source.search("cancer genomics", rows=5)

        assert result["total"] == 1
        assert result["query"] == "cancer genomics"
        assert len(result["results"]) == 1

        item = result["results"][0]
        assert item["title"] == "Genomic Analysis of Cancer"
        assert item["authors"] == ["Wang Li", "Zhang Wei"]
        assert item["year"] == 2024
        assert item["pmid"] == "99999999"
        assert item["doi"] == "10.1038/s41591-024-00001"
        assert item["journal"] == "Nature Medicine"
        assert item["source"] == "pubmed"
        assert "whole-genome" in item["abstract"]

        # Verify WebEnv and query_key were passed to efetch
        # _get(endpoint, params) -- params is positional arg index 1
        efetch_call_args = mock_get.call_args_list[1]
        efetch_params = efetch_call_args[0][1]
        assert efetch_params["WebEnv"] == "ABC123_webenv"
        assert efetch_params["query_key"] == "1"

    @patch("sources.pubmed.get_config")
    @patch("sources.pubmed._get")
    def test_search_no_results(self, mock_get, mock_config):
        mock_config.return_value = _make_pubmed_config()

        esearch_xml = """<?xml version="1.0"?>
        <eSearchResult>
            <Count>0</Count>
            <RetMax>0</RetMax>
            <IdList></IdList>
        </eSearchResult>"""

        mock_resp = MagicMock()
        mock_resp.content = esearch_xml.encode("utf-8")
        mock_get.return_value = mock_resp

        from sources.pubmed import PubMedSource

        source = PubMedSource()
        result = source.search("xyznonexistent12345", rows=5)

        assert result["total"] == 0
        assert result["results"] == []

    @patch("sources.pubmed.get_config")
    @patch("sources.pubmed._get")
    def test_get_by_pmid(self, mock_get, mock_config):
        mock_config.return_value = _make_pubmed_config()

        efetch_xml = """<?xml version="1.0"?>
        <PubmedArticleSet>
            <PubmedArticle>
                <MedlineCitation>
                    <PMID>12345678</PMID>
                    <Article>
                        <ArticleTitle>CRISPR Gene Editing Review</ArticleTitle>
                        <AuthorList>
                            <Author>
                                <LastName>Chen</LastName>
                                <ForeName>Xiaoming</ForeName>
                            </Author>
                        </AuthorList>
                        <Abstract>
                            <AbstractText>A comprehensive review of CRISPR.</AbstractText>
                        </Abstract>
                        <Journal>
                            <Title>Cell</Title>
                            <JournalIssue>
                                <PubDate><Year>2023</Year></PubDate>
                            </JournalIssue>
                        </Journal>
                    </Article>
                </MedlineCitation>
            </PubmedArticle>
        </PubmedArticleSet>"""

        mock_resp = MagicMock()
        mock_resp.content = efetch_xml.encode("utf-8")
        mock_get.return_value = mock_resp

        from sources.pubmed import PubMedSource

        source = PubMedSource()
        result = source.get_by_pmid("12345678")

        assert result["title"] == "CRISPR Gene Editing Review"
        assert result["pmid"] == "12345678"
        assert result["journal"] == "Cell"
        assert result["source"] == "pubmed"

    @patch("sources.pubmed.get_config")
    def test_search_empty_query_raises(self, mock_config):
        mock_config.return_value = _make_pubmed_config()

        from sources.pubmed import PubMedSource
        from utils.errors import DataSourceError

        source = PubMedSource()
        with pytest.raises(DataSourceError, match="Empty"):
            source.search("")

    @patch("sources.pubmed.get_config")
    def test_search_no_email_raises(self, mock_config):
        cfg = MagicMock()
        cfg.pubmed_email = ""
        mock_config.return_value = cfg

        from sources.pubmed import PubMedSource
        from utils.errors import DataSourceError

        source = PubMedSource()
        with pytest.raises(DataSourceError, match="email"):
            source.search("test query")

    @patch("sources.pubmed.get_config")
    @patch("sources.pubmed._get")
    def test_search_multiple_articles(self, mock_get, mock_config):
        mock_config.return_value = _make_pubmed_config()

        esearch_xml = """<?xml version="1.0"?>
        <eSearchResult>
            <Count>2</Count>
            <RetMax>2</RetMax>
            <WebEnv>ENV456</WebEnv>
            <QueryKey>2</QueryKey>
            <IdList><Id>111</Id><Id>222</Id></IdList>
        </eSearchResult>"""

        efetch_xml = """<?xml version="1.0"?>
        <PubmedArticleSet>
            <PubmedArticle>
                <MedlineCitation>
                    <PMID>111</PMID>
                    <Article>
                        <ArticleTitle>First Paper</ArticleTitle>
                        <AuthorList>
                            <Author><LastName>A</LastName><ForeName>B</ForeName></Author>
                        </AuthorList>
                        <Journal><Title>J1</Title><JournalIssue><PubDate><Year>2022</Year></PubDate></JournalIssue></Journal>
                    </Article>
                </MedlineCitation>
            </PubmedArticle>
            <PubmedArticle>
                <MedlineCitation>
                    <PMID>222</PMID>
                    <Article>
                        <ArticleTitle>Second Paper</ArticleTitle>
                        <AuthorList>
                            <Author><LastName>C</LastName><ForeName>D</ForeName></Author>
                        </AuthorList>
                        <Journal><Title>J2</Title><JournalIssue><PubDate><Year>2023</Year></PubDate></JournalIssue></Journal>
                    </Article>
                </MedlineCitation>
            </PubmedArticle>
        </PubmedArticleSet>"""

        esearch_resp = MagicMock()
        esearch_resp.content = esearch_xml.encode("utf-8")
        efetch_resp = MagicMock()
        efetch_resp.content = efetch_xml.encode("utf-8")
        mock_get.side_effect = [esearch_resp, efetch_resp]

        from sources.pubmed import PubMedSource

        source = PubMedSource()
        result = source.search("multi test", rows=2)

        assert result["total"] == 2
        assert len(result["results"]) == 2
        assert result["results"][0]["pmid"] == "111"
        assert result["results"][1]["pmid"] == "222"


# ===================================================================
# 3. arXiv tests
# ===================================================================


_ARXIV_ATOM_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom"
      xmlns:arxiv="http://arxiv.org/schemas/atom">
  <title>ArXiv Query: search_query={query}</title>
  {entries}
</feed>"""

_ARXIV_ENTRY_TEMPLATE = """<entry>
    <id>http://arxiv.org/abs/{arxiv_id}v1</id>
    <title>{title}</title>
    <summary>{summary}</summary>
    {author_elements}
    <published>{published}</published>
    <arxiv:primary_category term="{category}" xmlns:arxiv="http://arxiv.org/schemas/atom"/>
    <link rel="alternate" type="text/html" href="http://arxiv.org/abs/{arxiv_id}v1"/>
    <link title="pdf" rel="related" type="application/pdf" href="http://arxiv.org/pdf/{arxiv_id}v1"/>
</entry>"""


def _build_arxiv_xml(query: str, entries_data: list[dict]) -> str:
    """Build a minimal arXiv Atom XML response."""
    entries_xml = []
    for e in entries_data:
        author_elements = "".join(
            f"<author><name>{a}</name></author>" for a in e.get("authors", [])
        )
        entries_xml.append(
            _ARXIV_ENTRY_TEMPLATE.format(
                arxiv_id=e.get("arxiv_id", "2401.00001"),
                title=e.get("title", "Untitled"),
                summary=e.get("summary", ""),
                author_elements=author_elements,
                published=e.get("published", "2024-01-01T00:00:00Z"),
                category=e.get("category", "cs.AI"),
            )
        )
    return _ARXIV_ATOM_TEMPLATE.format(
        query=query, entries="\n".join(entries_xml)
    )


class TestArxivSearch:
    """Test arXiv search with date filtering and ID normalization."""

    @patch("sources.arxiv.get_config")
    @patch.object(
        __import__("sources.arxiv", fromlist=["ArxivSource"]).ArxivSource,
        "_request",
    )
    def test_search_returns_unified_format(self, mock_request, mock_config):
        mock_config.return_value = _make_arxiv_config()

        xml = _build_arxiv_xml("transformer", [
            {
                "arxiv_id": "2401.12345",
                "title": "Attention Is All You Need Again",
                "summary": "We revisit the transformer architecture.",
                "authors": ["Alice Smith", "Bob Jones"],
                "published": "2024-01-22T00:00:00Z",
                "category": "cs.CL",
            }
        ])
        mock_request.return_value = xml

        from sources.arxiv import ArxivSource

        source = ArxivSource()
        result = source.search("transformer", rows=5)

        assert "total" in result
        assert "results" in result
        assert result["total"] == 1
        assert result["source"] == "arxiv"

        item = result["results"][0]
        assert item["title"] == "Attention Is All You Need Again"
        assert item["authors"] == ["Alice Smith", "Bob Jones"]
        assert item["year"] == 2024
        assert item["arxiv_id"] == "2401.12345"
        assert item["categories"] == ["cs.CL"]
        assert item["source"] == "arxiv"

    @patch("sources.arxiv.get_config")
    @patch.object(
        __import__("sources.arxiv", fromlist=["ArxivSource"]).ArxivSource,
        "_request",
    )
    def test_search_with_date_filter(self, mock_request, mock_config):
        mock_config.return_value = _make_arxiv_config()

        xml = _build_arxiv_xml("LLM", [])
        mock_request.return_value = xml

        from sources.arxiv import ArxivSource

        source = ArxivSource()
        source.search("LLM", rows=5, date_from="2024-01-01", date_to="2024-06-30")

        called_params = mock_request.call_args[0][0]
        search_query = called_params["search_query"]
        assert "submittedDate:[" in search_query
        assert "202401010000+TO+202406302359" in search_query

    @patch("sources.arxiv.get_config")
    @patch.object(
        __import__("sources.arxiv", fromlist=["ArxivSource"]).ArxivSource,
        "_request",
    )
    def test_search_with_categories(self, mock_request, mock_config):
        mock_config.return_value = _make_arxiv_config()

        xml = _build_arxiv_xml("robotics", [])
        mock_request.return_value = xml

        from sources.arxiv import ArxivSource

        source = ArxivSource()
        source.search("robotics", rows=5, categories=["cs.RO", "cs.AI"])

        called_params = mock_request.call_args[0][0]
        search_query = called_params["search_query"]
        assert "cat:cs.RO" in search_query
        assert "cat:cs.AI" in search_query

    @patch("sources.arxiv.get_config")
    @patch.object(
        __import__("sources.arxiv", fromlist=["ArxivSource"]).ArxivSource,
        "_request",
    )
    def test_get_by_id(self, mock_request, mock_config):
        mock_config.return_value = _make_arxiv_config()

        xml = _build_arxiv_xml("id", [
            {
                "arxiv_id": "2301.00001",
                "title": "Foundational LLM Paper",
                "summary": "We introduce a new LLM.",
                "authors": ["Researcher One"],
                "published": "2023-01-01T00:00:00Z",
                "category": "cs.AI",
            }
        ])
        mock_request.return_value = xml

        from sources.arxiv import ArxivSource

        source = ArxivSource()
        result = source.get_by_id("2301.00001")

        assert result["title"] == "Foundational LLM Paper"
        assert result["arxiv_id"] == "2301.00001"
        assert result["source"] == "arxiv"

    @patch("sources.arxiv.get_config")
    @patch.object(
        __import__("sources.arxiv", fromlist=["ArxivSource"]).ArxivSource,
        "_request",
    )
    def test_get_by_id_not_found(self, mock_request, mock_config):
        mock_config.return_value = _make_arxiv_config()

        # Empty feed = no results
        xml = _build_arxiv_xml("id", [])
        mock_request.return_value = xml

        from sources.arxiv import ArxivSource
        from utils.errors import DataSourceError

        source = ArxivSource()
        with pytest.raises(DataSourceError, match="not found"):
            source.get_by_id("9999.99999")

    def test_normalize_id_strips_url_prefix_and_version(self):
        from sources.arxiv import ArxivSource

        source = ArxivSource.__new__(ArxivSource)

        assert source._normalize_id("http://arxiv.org/abs/2401.12345v1") == "2401.12345"
        assert source._normalize_id("https://arxiv.org/abs/2401.12345v2") == "2401.12345"
        assert source._normalize_id("2401.12345") == "2401.12345"
        assert source._normalize_id("2401.12345v3") == "2401.12345"

    def test_build_date_filter_syntax(self):
        from sources.arxiv import ArxivSource

        result = ArxivSource._build_date_filter("2024-01-01", "2024-12-31")
        assert result == "submittedDate:[202401010000+TO+202412312359]"

    def test_build_date_filter_only_from(self):
        from sources.arxiv import ArxivSource

        result = ArxivSource._build_date_filter("2024-06-01", None)
        assert "submittedDate:[" in result
        assert "202406010000" in result
        assert "999912312359" in result

    def test_build_date_filter_empty(self):
        from sources.arxiv import ArxivSource

        assert ArxivSource._build_date_filter(None, None) == ""

    def test_build_date_filter_only_to(self):
        from sources.arxiv import ArxivSource

        result = ArxivSource._build_date_filter(None, "2024-12-31")
        assert result == "submittedDate:[000000000000+TO+202412312359]"


# ===================================================================
# 4. ID auto-detection tests
# ===================================================================


class TestDetectIdType:
    """Test _detect_id_type auto-identification logic."""

    def test_detect_doi(self):
        from academic_search_server import _detect_id_type

        assert _detect_id_type("10.1038/nature12373") == "doi"
        assert _detect_id_type("10.1126/science.abc1234") == "doi"
        assert _detect_id_type("10.1016/j.cell.2023.01.001") == "doi"

    def test_detect_pmid(self):
        from academic_search_server import _detect_id_type

        assert _detect_id_type("12345678") == "pmid"
        assert _detect_id_type("1234567") == "pmid"

    def test_detect_arxiv(self):
        from academic_search_server import _detect_id_type

        assert _detect_id_type("2401.12345") == "arxiv"
        assert _detect_id_type("2301.00001") == "arxiv"
        assert _detect_id_type("2401.12345v1") == "arxiv"

    def test_detect_doi_with_whitespace(self):
        from academic_search_server import _detect_id_type

        assert _detect_id_type("  10.1038/nature12373  ") == "doi"

    def test_detect_unknown_raises(self):
        from academic_search_server import _detect_id_type

        with pytest.raises(ValueError, match="Cannot detect"):
            _detect_id_type("abc123")

    def test_detect_short_number_raises(self):
        """6-digit number is too short for PMID (needs 7-8)."""
        from academic_search_server import _detect_id_type

        with pytest.raises(ValueError, match="Cannot detect"):
            _detect_id_type("123456")

    def test_detect_long_number_raises(self):
        """9-digit number is too long for PMID (needs 7-8)."""
        from academic_search_server import _detect_id_type

        with pytest.raises(ValueError, match="Cannot detect"):
            _detect_id_type("123456789")

    def test_detect_arxiv_with_whitespace(self):
        from academic_search_server import _detect_id_type

        assert _detect_id_type("  2401.12345  ") == "arxiv"


class TestResolveIdType:
    """Test _resolve_id_type explicit and auto modes."""

    def test_explicit_doi(self):
        from academic_search_server import _resolve_id_type

        assert _resolve_id_type("10.1038/test", "doi") == "doi"

    def test_explicit_pmid(self):
        from academic_search_server import _resolve_id_type

        assert _resolve_id_type("12345678", "pmid") == "pmid"

    def test_auto_delegates(self):
        from academic_search_server import _resolve_id_type

        assert _resolve_id_type("10.1038/test", "auto") == "doi"
        assert _resolve_id_type("12345678", "auto") == "pmid"
        assert _resolve_id_type("2401.12345", "auto") == "arxiv"

    def test_invalid_type_raises(self):
        from academic_search_server import _resolve_id_type

        with pytest.raises(ValueError, match="Unsupported"):
            _resolve_id_type("anything", "invalid_type")

    def test_explicit_case_insensitive(self):
        from academic_search_server import _resolve_id_type

        assert _resolve_id_type("10.1038/test", "DOI") == "doi"
        assert _resolve_id_type("12345678", "PMID") == "pmid"
        assert _resolve_id_type("2401.12345", "ARXIV") == "arxiv"

    def test_explicit_whitespace_stripped(self):
        from academic_search_server import _resolve_id_type

        assert _resolve_id_type("10.1038/test", "  doi  ") == "doi"
        assert _resolve_id_type("12345678", " pmid ") == "pmid"
