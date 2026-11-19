"""PubMed article parsing edge cases (no network access)."""

from __future__ import annotations

import defusedxml.ElementTree as ET

from sources.pubmed import _parse_article


def _article(title_xml: str) -> object:
    return ET.fromstring(
        f"""<PubmedArticle><MedlineCitation><PMID>1</PMID><Article>
        <ArticleTitle>{title_xml}</ArticleTitle>
        <Journal><Title>J Test</Title><JournalIssue><PubDate><Year>2020</Year></PubDate></JournalIssue></Journal>
        </Article></MedlineCitation></PubmedArticle>"""
    )


def test_title_with_inline_markup_is_not_truncated():
    parsed = _parse_article(_article("Role of <i>Escherichia coli</i> in disease."))
    assert parsed["title"] == "Role of Escherichia coli in disease."


def test_plain_title_is_unchanged():
    assert _parse_article(_article("Genomic Analysis of Cancer"))["title"] == "Genomic Analysis of Cancer"


def _with_article_ids(*entries):
    article = _article("A <i>complete</i> title")
    ids = ET.SubElement(ET.SubElement(article, "PubmedData"), "ArticleIdList")
    for kind, value in entries:
        element = ET.SubElement(ids, "ArticleId")
        if kind is not None:
            element.set("IdType", kind)
        element.text = value
    return article


def test_pmcid_and_canonical_url_are_preserved():
    parsed = _parse_article(_with_article_ids(("pmc", "PMC12345")))
    assert parsed["pmcid"] == "PMC12345"
    assert parsed["pmc_url"] == "https://pmc.ncbi.nlm.nih.gov/articles/PMC12345/"


def test_pmcid_normalizes_outer_whitespace_and_lowercase_prefix():
    parsed = _parse_article(_with_article_ids(("pmc", " \tpmc12345\n ")))
    assert parsed["pmcid"] == "PMC12345"
    assert parsed["pmc_url"] == "https://pmc.ncbi.nlm.nih.gov/articles/PMC12345/"


def test_absent_pmcid_does_not_create_a_link():
    for article in (_article("Plain title"), _with_article_ids()):
        parsed = _parse_article(article)
        assert parsed["pmcid"] == ""
        assert parsed["pmc_url"] == ""


def test_invalid_pmcids_do_not_create_links():
    for value in (
        None, "", "12345", "PMC", "PMC0", "PMC0123", "PMC-1",
        "PMC12/other", "PMC12?x=1", "PMC1.0", "PMC１２３", "PMC1\n2",
        "https://pmc.ncbi.nlm.nih.gov/articles/PMC12345/",
    ):
        parsed = _parse_article(_with_article_ids(("pmc", value)))
        assert parsed["pmcid"] == "", value
        assert parsed["pmc_url"] == "", value


def test_only_this_articles_typed_pmc_identifier_is_used():
    article = _with_article_ids(
        ("pubmed", "PMC111"), ("doi", "PMC222"), (None, "PMC333"),
        ("PMC", "PMC444"),
    )
    references = ET.SubElement(article.find("PubmedData"), "ReferenceList")
    ref_ids = ET.SubElement(ET.SubElement(references, "Reference"), "ArticleIdList")
    ET.SubElement(ref_ids, "ArticleId", IdType="pmc").text = "PMC555"
    parsed = _parse_article(article)
    assert parsed["pmcid"] == ""
    assert parsed["pmc_url"] == ""


def test_duplicate_equivalent_pmcids_are_one_identity():
    parsed = _parse_article(
        _with_article_ids(("pmc", "PMC123"), ("pmc", " pmc123 "))
    )
    assert parsed["pmcid"] == "PMC123"


def test_conflicting_valid_pmcids_do_not_choose_an_arbitrary_identity():
    parsed = _parse_article(
        _with_article_ids(("pmc", "PMC123"), ("pmc", "PMC456"))
    )
    assert parsed["pmcid"] == ""
    assert parsed["pmc_url"] == ""


def test_malformed_id_does_not_hide_one_valid_pmcid():
    parsed = _parse_article(
        _with_article_ids(("pmc", "not-a-pmcid"), ("pmc", "PMC123"))
    )
    assert parsed["pmcid"] == "PMC123"


def test_existing_doi_behavior_is_unchanged():
    article = _with_article_ids(("doi", "10.9999/other"), ("pmc", "PMC123"))
    art = article.find("MedlineCitation/Article")
    ET.SubElement(art, "ELocationID", EIdType="doi").text = "10.9999/original"
    assert _parse_article(article)["doi"] == "10.9999/original"
    only_article_id_doi = _with_article_ids(("doi", "10.9999/other"))
    assert _parse_article(only_article_id_doi)["doi"] == ""


def test_original_eight_fields_remain_unchanged():
    parsed = _parse_article(_with_article_ids(("pmc", "PMC123")))
    expected = {
        "title": "A complete title", "authors": [], "year": 2020,
        "pmid": "1", "doi": "", "journal": "J Test", "abstract": "",
        "source": "pubmed",
    }
    assert {key: parsed[key] for key in expected} == expected
    assert set(parsed) == set(expected) | {"pmcid", "pmc_url"}
