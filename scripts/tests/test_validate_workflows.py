from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "validate-workflows.py"
SPEC = importlib.util.spec_from_file_location("validate_workflows", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class WorkflowActionPinTests(unittest.TestCase):
    def validate(self, action: str) -> list[str]:
        workflow = f"""
name: test
on: workflow_dispatch
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: {action}
"""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "test.yml"
            path.write_text(workflow, encoding="utf-8")
            original_root = MODULE.ROOT
            MODULE.ROOT = Path(tmp)
            try:
                return MODULE.validate_workflow(path)
            finally:
                MODULE.ROOT = original_root

    def test_mutable_version_tag_is_rejected(self) -> None:
        errors = self.validate("actions/checkout@v7")
        self.assertTrue(any("full 40-character commit SHA" in item for item in errors))

    def test_full_commit_sha_is_accepted(self) -> None:
        errors = self.validate(
            "actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1"
        )
        self.assertEqual(errors, [])

    def test_local_action_is_accepted(self) -> None:
        self.assertEqual(self.validate("./.github/actions/local"), [])


if __name__ == "__main__":
    unittest.main()
