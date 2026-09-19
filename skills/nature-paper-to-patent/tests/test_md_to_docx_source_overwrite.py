from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "disclosure" / "md_to_docx.py"
SPEC = importlib.util.spec_from_file_location("md_to_docx", SCRIPT)
CONVERTER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CONVERTER)


class MarkdownSourceOverwriteTests(unittest.TestCase):
    def test_output_cannot_reuse_markdown_input_path(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "disclosure.md"
            original = "# 技术交底书\n\n原始内容。\n"
            source.write_text(original, encoding="utf-8")

            with mock.patch.object(
                CONVERTER,
                "convert_md_to_docx",
                side_effect=AssertionError("conversion should not start"),
            ):
                result = CONVERTER.main(
                    [
                        "--input",
                        str(source),
                        "--output",
                        str(source),
                        "--no-math-render",
                    ]
                )

            self.assertEqual(result, 1)
            self.assertEqual(source.read_text(encoding="utf-8"), original)


if __name__ == "__main__":
    unittest.main()
