from __future__ import annotations

import argparse
import importlib.util
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path
import xml.etree.ElementTree as ET


SCRIPT = Path(__file__).parents[1] / "scripts" / "nature_citation.py"
SPEC = importlib.util.spec_from_file_location("nature_citation_under_test", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def candidate(**overrides):
    values = {
        "title": "A complete reference",
        "journal": "Nature Medicine",
        "family": "Nature Portfolio",
        "year": "2024",
        "y1": "2024/01/01",
        "doi": "10.1000/example",
        "url": "",
        "volume": "1",
        "issue": "2",
        "start_page": "10",
        "end_page": "18",
        "issn": "0000-0000",
        "authors": ["Smith, Alfred", "NMSS Validation Group,"],
        "abstract": "",
        "type": "journal-article",
        "score": 0.0,
        "source_query": "test",
    }
    values.update(overrides)
    return MODULE.Candidate(**values)


class AuthorExportTests(unittest.TestCase):
    def test_ris_is_the_default(self):
        self.assertEqual(MODULE.DEFAULT_EXPORT_FORMAT, "ris")
        self.assertEqual(MODULE.infer_export_format(None), "ris")
        self.assertEqual(MODULE.export_filename("ris"), "references.ris")

    def test_crossref_preserves_given_names_suffixes_and_corporate_authors(self):
        item = {
            "title": ["Author metadata test"],
            "container-title": ["Nature Medicine"],
            "published": {"date-parts": [[2024, 2, 3]]},
            "DOI": "10.1000/authors",
            "author": [
                {"family": "Smith", "given": "Alfred", "suffix": "Jr."},
                {"name": "NMSS Validation Group"},
            ],
        }
        result = MODULE.candidate_from_crossref(item, "doi:10.1000/authors")
        self.assertIsNotNone(result)
        self.assertEqual(result.authors, ["Smith, Alfred, Jr.", "NMSS Validation Group,"])
        self.assertEqual(result.author_warnings, [])

    def test_incomplete_personal_author_is_blocked_by_default(self):
        incomplete = candidate(
            authors=["Chaudhuri"],
            author_warnings=["Author 1 lacks a given name or initials in structured metadata."],
        )
        with self.assertRaisesRegex(ValueError, "Author metadata integrity check failed"):
            MODULE.validate_author_integrity([incomplete])
        MODULE.validate_author_integrity([incomplete], allow_incomplete=True)

        unflagged_surname = candidate(authors=["Chaudhuri"], author_warnings=[])
        with self.assertRaisesRegex(ValueError, "complete personal name"):
            MODULE.validate_author_integrity([unflagged_surname])

    def test_ris_has_one_author_per_line_and_traceable_identifiers(self):
        record = MODULE.build_ris_record(candidate(pmid="12345678"))
        self.assertIn("AU  - Smith, Alfred", record)
        self.assertIn("AU  - NMSS Validation Group,", record)
        self.assertEqual(record.count("AU  - "), 2)
        self.assertIn("DO  - 10.1000/example", record)
        self.assertIn("AN  - PMID:12345678", record)

    def test_write_ris_requires_explicit_override_for_incomplete_authors(self):
        incomplete = candidate(authors=["Smith"], author_warnings=["surname only"])
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "references.ris"
            with self.assertRaises(ValueError):
                MODULE.write_ris([incomplete], output)
            MODULE.write_ris([incomplete], output, allow_incomplete_authors=True)
            self.assertIn("Author metadata warning: surname only", output.read_text(encoding="utf-8"))

    def test_pubmed_parser_retains_personal_and_collective_authors(self):
        xml = """
        <PubmedArticle>
          <MedlineCitation>
            <PMID>21264941</PMID>
            <Article>
              <ArticleTitle>Validation of a nonmotor symptoms questionnaire.</ArticleTitle>
              <Abstract><AbstractText>Abstract text.</AbstractText></Abstract>
              <Journal>
                <ISSN>0000-0000</ISSN>
                <JournalIssue>
                  <Volume>26</Volume><Issue>10</Issue>
                  <PubDate><Year>2010</Year><Month>Oct</Month><Day>5</Day></PubDate>
                </JournalIssue>
                <Title>Nature Medicine</Title>
              </Journal>
              <Pagination><MedlinePgn>123-130</MedlinePgn></Pagination>
              <AuthorList>
                <Author><LastName>Chaudhuri</LastName><ForeName>K Ray</ForeName></Author>
                <Author><LastName>Schapira</LastName><ForeName>Anthony H V</ForeName><Suffix>Jr.</Suffix></Author>
                <Author><CollectiveName>NMSS Validation Group</CollectiveName></Author>
              </AuthorList>
              <PublicationTypeList><PublicationType>Journal Article</PublicationType></PublicationTypeList>
            </Article>
          </MedlineCitation>
          <PubmedData><ArticleIdList><ArticleId IdType="doi">10.1000/pubmed</ArticleId></ArticleIdList></PubmedData>
        </PubmedArticle>
        """
        result = MODULE.candidate_from_pubmed(ET.fromstring(xml))
        self.assertIsNotNone(result)
        self.assertEqual(
            result.authors,
            ["Chaudhuri, K Ray", "Schapira, Anthony H V, Jr.", "NMSS Validation Group,"],
        )
        self.assertEqual(result.author_warnings, [])
        self.assertEqual(result.pmid, "21264941")
        self.assertEqual(result.doi, "10.1000/pubmed")
        self.assertEqual(result.y1, "2010/10/05")

    def test_pubmed_candidate_replaces_incomplete_crossref_duplicate(self):
        crossref = candidate(authors=["Smith"], author_warnings=["surname only"])
        pubmed = candidate(
            authors=["Smith, Alfred"],
            author_warnings=[],
            pmid="12345678",
            source_catalog="PubMed",
        )
        result = MODULE.dedupe([crossref, pubmed])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].source_catalog, "PubMed")
        self.assertEqual(result[0].authors, ["Smith, Alfred"])

    def test_read_pmids_normalizes_urls_and_rejects_invalid_values(self):
        args = argparse.Namespace(
            pmid=["PMID: 123", "https://pubmed.ncbi.nlm.nih.gov/456/", "123"],
            pmid_file=None,
        )
        self.assertEqual(MODULE.read_pmids(args), ["123", "456"])
        args.pmid = ["not-a-pmid"]
        with self.assertRaisesRegex(ValueError, "Invalid PMID"):
            MODULE.read_pmids(args)

    def test_failed_explicit_pmid_does_not_write_empty_success_export(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "references.ris"
            with mock.patch.object(
                MODULE,
                "fetch_pubmed_candidates",
                return_value=([], [{"pmid": "123", "error": "network unavailable"}]),
            ):
                code = MODULE.main(["--pmid", "123", "--output-file", str(output), "--sleep", "0"])
            self.assertEqual(code, 4)
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
