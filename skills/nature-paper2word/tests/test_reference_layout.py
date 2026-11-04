"""Regression cases for formatting extracted from actual reference paragraphs."""
from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

from docx import Document
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml import OxmlElement
from docx.shared import Pt

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "reference_layout.py"
spec = importlib.util.spec_from_file_location("reference_layout", SCRIPT)
reference_layout = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reference_layout)


class ReferenceLayoutTests(unittest.TestCase):
    def setUp(self):
        self.doc = Document()
        self.doc.styles["Normal"].font.name = "Times New Roman"
        self.doc.styles["Normal"].font.size = Pt(11)
        self.parent = self.doc.styles.add_style("CustomParent", WD_STYLE_TYPE.PARAGRAPH)
        self.parent.base_style = self.doc.styles["Normal"]
        self.child = self.doc.styles.add_style("CustomChild", WD_STYLE_TYPE.PARAGRAPH)
        self.child.base_style = self.parent
        self.paragraph = self.doc.add_paragraph("Reference body sample.", self.child)
        self.run = self.paragraph.runs[0]

    def extract_body(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "reference.docx"
            self.doc.save(path)
            draft = reference_layout.build_reference(
                path, {"Body Text": {"paragraph": 0, "run": 0}}
            )
        return next(line.split("：", 1)[1] for line in draft.splitlines()
                    if line.startswith("正文："))

    def assert_emphasis(self, bold, italic):
        clauses = self.extract_body().split()
        self.assertIn("加粗" if bold else "不加粗", clauses)
        self.assertIn("倾斜" if italic else "不倾斜", clauses)

    def test_parent_child_style_toggles(self):
        self.parent.font.bold = self.parent.font.italic = True
        for child_value, expected in [(True, False), (False, True), (None, True)]:
            with self.subTest(child_value=child_value):
                self.child.font.bold = self.child.font.italic = child_value
                self.assert_emphasis(expected, expected)

    def test_paragraph_plus_character_style_toggles(self):
        self.parent.font.bold = self.parent.font.italic = True
        char_parent = self.doc.styles.add_style("CharacterParent", WD_STYLE_TYPE.CHARACTER)
        char_parent.font.bold = True
        char_parent.font.italic = False
        char_child = self.doc.styles.add_style("CharacterChild", WD_STYLE_TYPE.CHARACTER)
        char_child.base_style = char_parent
        char_child.font.bold = False
        char_child.font.italic = True
        self.run.style = char_child
        self.assert_emphasis(False, False)

    def test_direct_run_overrides_are_absolute(self):
        self.parent.font.bold = self.parent.font.italic = True
        for child_value, direct_value in [(True, True), (False, False)]:
            with self.subTest(child_value=child_value, direct_value=direct_value):
                self.child.font.bold = self.child.font.italic = child_value
                self.run.bold = self.run.italic = direct_value
                self.assert_emphasis(direct_value, direct_value)
        for value in ["true", "on", "false", "off"]:
            with self.subTest(direct_xml=value):
                for tag in ["b", "i"]:
                    self.run._r.rPr.find(reference_layout.q(tag)).set(reference_layout.q("val"), value)
                self.assert_emphasis(value in {"true", "on"}, value in {"true", "on"})

    def test_document_defaults_initialize_toggle_state(self):
        defaults = self.doc.styles.element.find(reference_layout.q("docDefaults"))
        rpr = defaults.find(reference_layout.q("rPrDefault")).find(reference_layout.q("rPr"))
        rpr.append(OxmlElement("w:b"))
        self.assert_emphasis(True, False)
        self.parent.font.bold = self.parent.font.italic = True
        self.assert_emphasis(False, True)

    def test_partial_property_inheritance(self):
        self.parent.font.bold = True
        self.parent.font.size = Pt(14)
        self.parent.paragraph_format.line_spacing = 1.5
        self.parent.paragraph_format.space_before = Pt(2)
        self.parent.paragraph_format.space_after = Pt(7)
        self.child.font.name = "Arial"
        self.child.font.bold = False  # A style-level false retains inherited bold.
        self.child.font.italic = True
        self.child.paragraph_format.space_after = Pt(3)
        character = self.doc.styles.add_style("CharacterToggle", WD_STYLE_TYPE.CHARACTER)
        character.font.italic = True
        self.run.style = character
        self.run.font.size = Pt(10.5)
        clauses = self.extract_body().split()
        for value in ["Arial", "10.5pt", "加粗", "不倾斜", "行距1.5倍", "段前2磅", "段后3磅"]:
            self.assertIn(value, clauses)


if __name__ == "__main__":
    unittest.main()
