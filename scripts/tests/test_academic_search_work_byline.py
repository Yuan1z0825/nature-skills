from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path
from unittest import mock

SCRIPT = Path(__file__).resolve().parents[2] / "skills/nature-academic-search/scripts/academic_search.py"
SPEC = importlib.util.spec_from_file_location("academic_search_byline_test", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def search_saved(records, **kwargs):
    with mock.patch.object(MODULE, "_get_json", return_value={"results": records}) as transport:
        result = MODULE.search("shared pathways", **kwargs)
    transport.assert_called_once()
    return result, transport.call_args.args[0]


class OpenAlexWorkBylineTests(unittest.TestCase):
    def test_published_work_bylines_instead_of_entity_variants(self):
        # Published bylines: PMID 32971526 / DOI 10.1038/s41586-020-2797-4
        # and PMID 32535955 / DOI 10.1111/all.14449.
        records = [
            {"doi": "https://doi.org/10.1038/s41586-020-2797-4", "authorships": [
                {"raw_author_name": "Carlos Talavera-López",
                 "author": {"display_name": "Carlos N. Talavera-López"}}]},
            {"doi": "https://doi.org/10.1111/all.14449", "authorships": [
                {"raw_author_name": "Ioana Agache",
                 "author": {"display_name": "Ioana Octavia Agache"}}]},
        ]
        papers, _ = search_saved(records, limit=2)
        self.assertEqual(papers[0]["authors"], ["Carlos Talavera-López"])
        self.assertEqual(papers[1]["authors"], ["Ioana Agache"])

    def test_missing_blank_null_and_nonstring_raw_names_keep_entity_fallback(self):
        authorships = [
            {"author": {"display_name": "Missing Raw"}},
            {"raw_author_name": "", "author": {"display_name": "Empty Raw"}},
            {"raw_author_name": " \t\n", "author": {"display_name": "Blank Raw"}},
            {"raw_author_name": None, "author": {"display_name": "Null Raw"}},
            {"raw_author_name": 42, "author": {"display_name": "Nonstring Raw"}},
        ]
        papers, _ = search_saved([{"authorships": authorships}])
        self.assertEqual(papers[0]["authors"], ["Missing Raw", "Empty Raw", "Blank Raw", "Null Raw", "Nonstring Raw"])

    def test_raw_name_survives_missing_or_null_resolved_author(self):
        papers, _ = search_saved([{"authorships": [
            {"raw_author_name": "Work Byline", "author": None},
            {"raw_author_name": "Second Byline"},
            {"raw_author_name": None, "author": None},
        ]}])
        self.assertEqual(papers[0]["authors"], ["Work Byline", "Second Byline", ""])

    def test_preserves_authorship_order_and_five_author_limit(self):
        papers, _ = search_saved([{"authorships": [
            {"raw_author_name": f"Byline {number}", "author": {"display_name": f"Entity {number}"}}
            for number in range(7)
        ]}])
        self.assertEqual(papers[0]["authors"], ["Byline 0", "Byline 1", "Byline 2", "Byline 3", "Byline 4"])

    def test_query_filters_and_relevance_reranking_still_apply(self):
        records = [
            {"doi": "10.1234/relevant", "relevance_score": 1.0, "cited_by_count": 10},
            {"doi": "10.1234/relevant-cited", "relevance_score": 0.8, "cited_by_count": 20},
            {"doi": "10.1234/weak", "relevance_score": 0.1, "cited_by_count": 9999},
        ]
        papers, url = search_saved(records, limit=1, year_from=2020,
                                    sort="cited_by_count", author_id="A123")
        self.assertEqual([paper["doi"] for paper in papers], ["10.1234/relevant-cited"])
        self.assertIn("per_page=5", url)
        self.assertIn("from_publication_date%3A2020-01-01", url)
        self.assertIn("author.id%3AA123", url)
        self.assertNotIn("sort=", url)


if __name__ == "__main__":
    unittest.main()
