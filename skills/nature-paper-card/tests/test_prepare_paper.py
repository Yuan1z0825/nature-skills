#!/usr/bin/env python3
"""Regression tests for source-map page-locator normalization."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


sys.dont_write_bytecode = True
SCRIPT_PATH = Path(__file__).parents[1] / "scripts" / "prepare_paper.py"
SPEC = importlib.util.spec_from_file_location("nature_paper_card_prepare", SCRIPT_PATH)
assert SPEC and SPEC.loader
PREPARE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PREPARE)

LONG_TEXT = (
    "This source block is deliberately longer than fifty characters so bundle "
    "validation accepts it."
)


class SourceMapLocatorTests(unittest.TestCase):
    def prepare(self, blocks: list[dict]) -> dict:
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source-map.json"
            source.write_text(
                json.dumps({"metadata": {"title": "Test paper"}, "blocks": blocks}),
                encoding="utf-8",
            )
            bundle = PREPARE.prepare_source_map(source)
            bundle["validation"] = PREPARE.validate_bundle(bundle)
            return bundle

    def test_verified_page_one_remains_page_one(self) -> None:
        bundle = self.prepare([{"id": "S001", "page": 1, "text": LONG_TEXT}])

        self.assertEqual([page["pdf_page"] for page in bundle["pages"]], [1])
        self.assertEqual(bundle["unlocated_blocks"], [])
        self.assertEqual(bundle["locator_summary"]["verified_page_blocks"], 1)

    def test_missing_locator_does_not_become_page_one(self) -> None:
        bundle = self.prepare([{"id": "S001", "text": LONG_TEXT}])

        self.assertEqual(bundle["pages"], [])
        self.assertEqual(bundle["page_count"], 0)
        self.assertEqual(bundle["unlocated_blocks"][0]["locator_status"], "missing")
        self.assertEqual(bundle["validation"]["recommended_locator_mode"], "structure-grounded")
        self.assertEqual(bundle["validation"]["status"], "valid_with_warnings")
        self.assertTrue(
            any("no page locator" in warning for warning in bundle["validation"]["warnings"])
        )

    def test_non_numeric_locator_is_preserved_as_invalid(self) -> None:
        bundle = self.prepare(
            [{"id": "S001", "page": "not-a-page", "text": LONG_TEXT}]
        )

        block = bundle["unlocated_blocks"][0]
        self.assertEqual(bundle["pages"], [])
        self.assertEqual(block["locator_status"], "invalid")
        self.assertEqual(block["locator_field"], "page")
        self.assertEqual(block["locator_value"], "not-a-page")

    def test_zero_locator_is_preserved_as_invalid(self) -> None:
        bundle = self.prepare([{"id": "S001", "page": 0, "text": LONG_TEXT}])

        block = bundle["unlocated_blocks"][0]
        self.assertEqual(bundle["pages"], [])
        self.assertEqual(block["locator_status"], "invalid")
        self.assertEqual(block["locator_value"], 0)

    def test_unknown_location_text_remains_available_for_structure_analysis(self) -> None:
        equation_text = (
            "Methods\nThe model minimizes the following objective while retaining "
            "all structural evidence from the supplied source map. (2)"
        )
        bundle = self.prepare([{"id": "S009", "text": equation_text}])

        self.assertEqual(bundle["unlocated_blocks"][0]["text"], equation_text)
        self.assertEqual(bundle["sections"][0]["title"], "Methods")
        self.assertIsNone(bundle["sections"][0]["pdf_page"])
        self.assertEqual(bundle["evidence_inventory"]["equations"][0]["id"], "Equation 2")
        self.assertIsNone(bundle["evidence_inventory"]["equations"][0]["pdf_page"])

    def test_mixed_locators_never_merge_unknown_text_into_page_one(self) -> None:
        bundle = self.prepare(
            [
                {"id": "S001", "page": 1, "text": LONG_TEXT},
                {"id": "S002", "text": "Unlocated " + LONG_TEXT},
                {"id": "S003", "page": "bad", "text": "Invalid " + LONG_TEXT},
            ]
        )

        self.assertEqual(len(bundle["pages"]), 1)
        self.assertEqual(bundle["pages"][0]["text"], LONG_TEXT)
        self.assertEqual(len(bundle["unlocated_blocks"]), 2)
        self.assertEqual(
            bundle["locator_summary"],
            {
                "verified_page_blocks": 1,
                "missing_page_locator_blocks": 1,
                "invalid_page_locator_blocks": 1,
                "page_locator_reliability": "mixed",
            },
        )

    def test_cli_preserves_an_invalid_locator_as_unknown(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source-map.json"
            output = root / "source-bundle.json"
            source.write_text(
                json.dumps(
                    {
                        "metadata": {"title": "CLI test"},
                        "blocks": [{"page": "not-a-page", "text": LONG_TEXT}],
                    }
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                [sys.executable, str(SCRIPT_PATH), str(source), "--output", str(output)],
                check=False,
                capture_output=True,
                text=True,
            )
            bundle = json.loads(output.read_text(encoding="utf-8"))

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(bundle["pages"], [])
        self.assertEqual(bundle["unlocated_blocks"][0]["locator_status"], "invalid")
        self.assertIn("invalid page locators", "\n".join(bundle["validation"]["warnings"]))


if __name__ == "__main__":
    unittest.main()
