import json
from pathlib import Path
import subprocess
import sys

import pymupdf

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "pages.py"


def test_prepare_and_status_emit_only_json(tmp_path):
    source, work = tmp_path / "source.pdf", tmp_path / "job"
    with pymupdf.open() as pdf:
        pdf.new_page(width=80, height=100)
        pdf.save(source)
    for command in (["prepare", "--pdf", str(source), "--pages", "all", "--dpi", "72"], ["status"]):
        result = subprocess.run([sys.executable, str(SCRIPT), *command, "--work-dir", str(work)],
                                capture_output=True, text=True, timeout=30)
        assert result.returncode == 0, result.stderr
        assert isinstance(json.loads(result.stdout), dict)
        assert result.stderr == ""


def test_error_channel_remains_json_without_import_warnings(tmp_path):
    result = subprocess.run([sys.executable, str(SCRIPT), "prepare", "--pdf", str(tmp_path / "missing.pdf"),
                             "--pages", "all", "--work-dir", str(tmp_path / "job")],
                            capture_output=True, text=True, timeout=30)
    assert result.returncode != 0
    assert result.stdout == ""
    assert "error" in json.loads(result.stderr)
