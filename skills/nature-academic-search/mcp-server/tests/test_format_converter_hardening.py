"""Hardening regression tests for format-converter.py (no network access)."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"


def _load(name: str, filename: str):
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / filename)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


format_converter = _load("nature_search_format_converter", "format-converter.py")


METADATA_HOST = "http://169.254.169.254/latest/meta-data/"


def test_is_allowed_url_accepts_known_api_hosts_and_rejects_others():
    assert format_converter._is_allowed_url("https://api.crossref.org/works/10.1/x")
    assert format_converter._is_allowed_url("https://eutils.ncbi.nlm.nih.gov/esearch.fcgi?x=1")
    assert not format_converter._is_allowed_url(METADATA_HOST)
    assert not format_converter._is_allowed_url("https://evil.example.com/works")
    assert not format_converter._is_allowed_url("not a url")


def test_efetch_medline_skips_network_when_host_not_allowlisted(monkeypatch):
    monkeypatch.setattr(format_converter, "EUTILS_BASE", "http://169.254.169.254")
    with patch.object(format_converter, "urlopen", side_effect=AssertionError("must not fetch")) as opened:
        assert format_converter.efetch_medline("1") is None
    opened.assert_not_called()


def test_download_crossref_skips_network_when_host_not_allowlisted(monkeypatch):
    monkeypatch.setattr(format_converter, "CROSSREF_BASE", "http://169.254.169.254/works")
    with patch.object(format_converter, "urlopen", side_effect=AssertionError("must not fetch")) as opened:
        ok, message = format_converter.download_crossref("10.1/x", "/tmp", "ris")
    assert ok is False and "not in allowlist" in message
    opened.assert_not_called()


def test_download_arxiv_skips_network_when_host_not_allowlisted(monkeypatch):
    monkeypatch.setattr(format_converter, "ARXIV_BASE", "http://169.254.169.254/query")
    with patch.object(format_converter, "urlopen", side_effect=AssertionError("must not fetch")) as opened:
        ok, message = format_converter.download_arxiv("1706.03762", "/tmp", "ris")
    assert ok is False and "not in allowlist" in message
    opened.assert_not_called()


def test_download_pubmed_keeps_output_inside_output_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(format_converter, "efetch_medline", lambda _pmid, retries=1: "PMID- 1\nTI  - t\n")
    monkeypatch.setattr(format_converter, "convert_from_medline", lambda _text, _fmt: "content")
    monkeypatch.setattr(format_converter, "time", MagicMock())

    ok, filename = format_converter.download_pubmed("x/../../evil", str(tmp_path), "ris")

    assert ok is True
    assert "/" not in filename and ".." not in Path(filename).parts
    written = tmp_path / filename
    assert written.is_file() and written.read_text(encoding="utf-8") == "content"
    assert not (tmp_path.parent / "evil.ris").exists()


def test_download_crossref_and_arxiv_filenames_stay_sanitized(tmp_path, monkeypatch):
    monkeypatch.setattr(format_converter, "convert_from_crossref", lambda _data, _fmt: "content")
    monkeypatch.setattr(format_converter, "convert_from_arxiv", lambda _root, _fmt: "content")
    monkeypatch.setattr(format_converter, "time", MagicMock())

    def _response(payload: bytes) -> MagicMock:
        response = MagicMock()
        response.__enter__.return_value.read.return_value = payload
        return response

    with patch.object(format_converter, "urlopen", side_effect=[_response(b"{}"), _response(b'<feed xmlns="http://www.w3.org/2005/Atom"/>')]):
        ok_crossref, name_crossref = format_converter.download_crossref("10.1/../../evil", str(tmp_path), "ris")
        ok_arxiv, name_arxiv = format_converter.download_arxiv("../../evil", str(tmp_path), "ris")
    assert ok_crossref and ok_arxiv
    for name in (name_crossref, name_arxiv):
        assert "/" not in name and ".." not in Path(name).parts
        assert (tmp_path / name).is_file()
