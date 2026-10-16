import contextlib
import importlib.util
import io
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "pages.py"


def setup_job(tmp_path, monkeypatch, review=None):
    spec = importlib.util.spec_from_file_location("review_gate", SCRIPT)
    pages = importlib.util.module_from_spec(spec)
    with contextlib.redirect_stdout(io.StringIO()):
        spec.loader.exec_module(pages)
    attempt = {"attempt_id": "image-1", "state": "recorded", "prompt": "prompt.md", "output": "page.png",
               "output_sha256": "hash", "output_dimensions": [32, 48], "review": review}
    page = {"attempts": 1, "attempt_records": [attempt], "selected_attempt_id": "image-1",
            "selection_confirmed": True, "source_page_size": [80, 100]}
    task = {"task_id": "task", "source": {"path": str(tmp_path / "source.pdf")}, "selected_pages": [1],
            "pages": {"1": page}}
    monkeypatch.setattr(pages, "composition", lambda *_: contextlib.nullcontext((task, [])))
    publish = Mock(return_value=False)
    monkeypatch.setattr(pages, "publish_pdf", publish)
    args = SimpleNamespace(output=str(tmp_path / "output.pdf"), allow_partial=False, pdf_only=True, a4=False)
    return pages, args, publish


def test_pdf_only_export_cannot_bypass_review(tmp_path, monkeypatch):
    pages, args, publish = setup_job(tmp_path, monkeypatch)
    with pytest.raises(pages.TaskError, match="Review the selected image"):
        pages.assemble(args, tmp_path)
    publish.assert_not_called()


@pytest.mark.parametrize("status", ["pass", "issue", "unknown"])
def test_export_preserves_honest_review_status_without_sidecar(tmp_path, monkeypatch, status):
    review = {"status": status, "observations": ["Compared source and selected generated image"]}
    pages, args, publish = setup_job(tmp_path, monkeypatch, review)
    result = pages.assemble(args, tmp_path)
    publish.assert_called_once()
    assert result["review_summary"][status] == [1]
    assert "report" not in result
    assert publish.call_args.args[3]["page_sources"][0]["review"] == review
