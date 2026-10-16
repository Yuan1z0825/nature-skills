import os
from pathlib import Path
import subprocess
import sys

from docx import Document
import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "build_proposal_docx.py"


def export(tmp_path, markdown):
    source, output = tmp_path / "source.md", tmp_path / "proposal.docx"
    source.write_text(markdown, encoding="utf-8")
    result = subprocess.run([sys.executable, str(SCRIPT), str(source), str(output)],
                            capture_output=True, text=True, encoding="utf-8",
                            env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    assert result.returncode == 0, result.stderr
    assert source.read_text(encoding="utf-8") == markdown
    return [[cell.text for cell in row.cells] for row in Document(output).tables[0].rows]


@pytest.mark.parametrize("separator", ["|---|---|", "| --- | --- |", "| :--- | ---: |", "| :---: | :----: |"])
def test_delimiter_row_is_not_exported(tmp_path, separator):
    rows = export(tmp_path, f"# Proposal\n\n| Item | Value |\n{separator}\n| sample | 42 |\n")
    assert rows == [["Item", "Value"], ["sample", "42"]]


def test_dash_text_in_body_is_preserved(tmp_path):
    rows = export(tmp_path, "| Item | Value |\n| --- | --- |\n| --- | retained |\n")
    assert rows == [["Item", "Value"], ["---", "retained"]]


def test_header_only_table_is_preserved(tmp_path):
    assert export(tmp_path, "| Item | Value |\n| --- | --- |\n") == [["Item", "Value"]]
