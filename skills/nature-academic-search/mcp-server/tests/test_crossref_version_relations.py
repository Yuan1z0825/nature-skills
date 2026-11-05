"""Crossref explicit version-link handoff; no HTTP calls."""
import unittest
from sources.crossref import CrossRefSource

class CrossRefVersionRelationTests(unittest.TestCase):
    def setUp(self):
        # Normalization is independent of config/network initialization.
        self.source = object.__new__(CrossRefSource)
        self.item = {"DOI": "10.1234/preprint.1", "title": ["Study"],
                     "relation": {"is-preprint-of": [
                         {"id-type": "doi", "id": "10.1234/manuscript.1",
                          "asserted-by": "subject"}]}}

    def test_search_and_detail_preserve_explicit_relation_and_source_doi(self):
        for normalize in (self.source._normalize_search_item,
                          self.source._normalize_detail_item):
            with self.subTest(normalizer=normalize.__name__):
                result = normalize(self.item)
                self.assertEqual(result["preprint_of_dois"], ["10.1234/manuscript.1"])
                self.assertEqual(result["doi"], "10.1234/preprint.1")

    def test_missing_or_malformed_relation_returns_empty(self):
        for value in (None, {}, [], "is-preprint-of", {"is-preprint-of": None},
                      {"is-preprint-of": {}}, {"is-preprint-of": "10.1234/x"}):
            with self.subTest(value=value):
                self.assertEqual(self.source._extract_preprint_of_dois(
                    {"relation": value}), [])

    def test_other_relationships_are_not_version_relations(self):
        entry = [{"id-type": "doi", "id": "10.1234/parent"}]
        for kind in ("has-preprint", "is-component-of", "is-review-of",
                     "is-referenced-by", "is-identical-to"):
            with self.subTest(kind=kind):
                self.assertEqual(self.source._extract_preprint_of_dois(
                    {"relation": {kind: entry}}), [])

    def test_non_doi_and_malformed_ids_are_ignored(self):
        invalid = [None, {}, 42, "", "10.1234/", "10.123/a", "10.1234567890/a",
                   "https://doi.org/10.1234/a", "10.1234/a b", "10.1234/<a>",
                   "10.1234/a\x00b", "10.1234/a\x7fb"]
        entries = [{"id-type": "doi", "id": value} for value in invalid]
        entries += [None, "10.1234/a", {"id-type": "url", "id": "10.1234/a"}]
        self.assertEqual(self.source._extract_preprint_of_dois(
            {"relation": {"is-preprint-of": entries}}), [])

    def test_multiple_targets_preserve_first_spelling_and_order(self):
        entries = [{"id-type": "doi", "id": doi} for doi in
                   [" 10.1234/A  ", "10.1234/a", "10.1234/B"]]
        self.assertEqual(self.source._extract_preprint_of_dois(
            {"relation": {"is-preprint-of": entries}}), ["10.1234/A", "10.1234/B"])

    def test_relation_and_input_are_not_mutated(self):
        import copy
        before = copy.deepcopy(self.item)
        self.source._normalize_search_item(self.item)
        self.source._normalize_detail_item(self.item)
        self.assertEqual(self.item, before)

    def test_search_legacy_fields_keep_order(self):
        keys = list(self.source._normalize_search_item(self.item))
        self.assertEqual(keys, ["title", "authors", "year", "doi", "journal",
                                "source", "citation_count", "preprint_of_dois"])

if __name__ == "__main__":
    unittest.main()

