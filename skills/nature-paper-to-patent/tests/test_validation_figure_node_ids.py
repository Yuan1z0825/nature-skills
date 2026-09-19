from __future__ import annotations

import unittest

from test_validation import VALIDATOR, valid_draft


class FigureNodeIdValidationTests(unittest.TestCase):
    def test_duplicate_figure_node_id_fails(self) -> None:
        draft = valid_draft()
        draft["figures"][0]["nodes"][2]["id"] = "S2"

        findings = VALIDATOR.validate(draft)

        messages = [
            item.message
            for item in findings
            if item.code == "DUPLICATE_FIGURE_NODE_ID"
        ]
        self.assertEqual(["图1的节点ID重复：'S2'。"], messages)


if __name__ == "__main__":
    unittest.main()
