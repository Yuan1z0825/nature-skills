from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "check_consistency.py"
SPEC = importlib.util.spec_from_file_location("check_consistency", SCRIPT)
assert SPEC and SPEC.loader
CHECKER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = CHECKER
SPEC.loader.exec_module(CHECKER)


class ConsistencyCheckerTests(unittest.TestCase):
    def run_text(
        self,
        text: str,
        groups: dict[str, tuple[str, ...]] | None = None,
    ) -> list[object]:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "manuscript.tex"
            path.write_text(text, encoding="utf-8")
            return CHECKER.run_checks([path], groups)

    def test_clean_text_has_no_findings(self) -> None:
        findings = self.run_text(
            "This study used a 35 mm specimen and obtained values of 8.26 and 9.14.",
            CHECKER.DEFAULT_TERM_GROUPS,
        )
        self.assertEqual([], findings)

    def test_term_variants_are_reported(self) -> None:
        findings = self.run_text(
            "This study defines the task. Later, this work reports the results.",
            CHECKER.DEFAULT_TERM_GROUPS,
        )
        self.assertIn("TERM_VARIANTS_PRESENT", {item.code for item in findings})

    def test_numeric_precision_variants_are_reported(self) -> None:
        findings = self.run_text("The score was 8.26 in Table 1 and 8.260 in the abstract.")
        self.assertIn("NUMERIC_PRECISION_VARIANT", {item.code for item in findings})

    def test_equivalent_length_units_are_reported(self) -> None:
        findings = self.run_text("The cover was 35 mm in Methods and 3.5 cm in the caption.")
        self.assertIn(
            "EQUIVALENT_LENGTH_UNIT_VARIANT",
            {item.code for item in findings},
        )

    def test_custom_term_group_is_supported(self) -> None:
        findings = self.run_text(
            "The test specimen was loaded. Each sample was then measured.",
            {"test-object": ("specimen", "sample")},
        )
        self.assertIn("TERM_VARIANTS_PRESENT", {item.code for item in findings})


if __name__ == "__main__":
    unittest.main()
