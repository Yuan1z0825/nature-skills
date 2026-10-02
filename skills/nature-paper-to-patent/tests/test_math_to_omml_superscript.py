from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path
from xml.etree import ElementTree


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "math_to_omml.py"
SPEC = importlib.util.spec_from_file_location("math_to_omml", SCRIPT)
MATH = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MATH)


class SuperscriptOmmlTests(unittest.TestCase):
    def test_msup_uses_superscript_child(self) -> None:
        mathml = ElementTree.fromstring(
            '<msup xmlns="http://www.w3.org/1998/Math/MathML">'
            "<mi>x</mi><mn>2</mn></msup>"
        )
        target = MATH._element("oMath")

        MATH._append_mathml(target, mathml)

        superscript = target[0]
        self.assertTrue(superscript.tag.endswith("}sSup"))
        self.assertTrue(superscript[1].tag.endswith("}sup"))
        self.assertEqual("".join(superscript[1].itertext()), "2")

    def test_script_variants_keep_operands_in_the_correct_slots(self) -> None:
        cases = (
            ("msub", "sSub", ("e", "sub"), ("x", "i")),
            ("msup", "sSup", ("e", "sup"), ("x", "2")),
            ("msubsup", "sSubSup", ("e", "sub", "sup"), ("x", "i", "2")),
            ("munder", "sSub", ("e", "sub"), ("x", "i")),
            ("mover", "sSup", ("e", "sup"), ("x", "2")),
            ("munderover", "sSubSup", ("e", "sub", "sup"), ("x", "i", "2")),
        )
        for tag, expected_tag, slots, values in cases:
            with self.subTest(tag=tag):
                children = "".join(f"<mi>{value}</mi>" for value in values)
                mathml = ElementTree.fromstring(
                    f'<{tag} xmlns="http://www.w3.org/1998/Math/MathML">'
                    f"{children}</{tag}>"
                )
                target = MATH._element("oMath")
                MATH._append_mathml(target, mathml)
                script = target[0]
                self.assertEqual(script.tag, MATH.qn(f"m:{expected_tag}"))
                self.assertEqual([child.tag for child in script], [MATH.qn(f"m:{s}") for s in slots])
                self.assertEqual(tuple("".join(child.itertext()) for child in script), values)


if __name__ == "__main__":
    unittest.main()
