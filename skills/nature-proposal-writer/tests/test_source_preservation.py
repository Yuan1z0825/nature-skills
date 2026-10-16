import os
from pathlib import Path
import subprocess
import sys

from docx import Document
import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "build_proposal_docx.py"


def run(source, *output):
    return subprocess.run([sys.executable, str(SCRIPT), str(source), *map(str, output)],
                          capture_output=True, text=True, encoding="utf-8",
                          env={**os.environ, "PYTHONIOENCODING": "utf-8"})


@pytest.mark.parametrize("name", ["proposal.md", "proposal.MD", "proposal.Markdown", "proposal"])
def test_default_output_preserves_source(tmp_path, name):
    parent = tmp_path / "source.md.folder"
    parent.mkdir()
    source = parent / name
    original = b"# Research proposal\n\nSource must survive.\n"
    source.write_bytes(original)
    result = run(source)
    assert result.returncode == 0, result.stderr
    assert source.read_bytes() == original
    output = source.with_suffix(".docx")
    assert output.is_file()
    assert any("Source must survive" in p.text for p in Document(output).paragraphs)


def test_explicit_source_output_is_rejected(tmp_path):
    source = tmp_path / "proposal.MD"
    source.write_text("# Source", encoding="utf-8")
    result = run(source, source.parent / "." / source.name)
    assert result.returncode != 0
    assert "must not overwrite" in result.stderr
    assert source.read_text(encoding="utf-8") == "# Source"


def test_hardlink_alias_cannot_overwrite_source(tmp_path):
    source = tmp_path / "proposal.md"
    source.write_text("# Source", encoding="utf-8")
    alias = tmp_path / "alias.docx"
    try:
        os.link(source, alias)
    except OSError as error:
        pytest.skip(str(error))
    result = run(source, alias)
    assert result.returncode != 0
    assert source.read_text(encoding="utf-8") == "# Source"
