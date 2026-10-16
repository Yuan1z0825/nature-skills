import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "audit_paper_card.py"
spec = importlib.util.spec_from_file_location("page_ranges", SCRIPT)
auditor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(auditor)


def card(pointer):
    return "\n".join(["# Card", "> locator-mode: page-grounded"] + ["> field: supplied"] * 6 +
                     sum(([f"## {i:02d} Section", f"[Paper: {pointer}]"] for i in range(1, 17)), []) +
                     ["Innovation status: hypothesis; validation: test; failure mode: confounding."])


@pytest.mark.parametrize("pointer", ["PDF p. 99999", "PDF p. 0", "PDF p. -1", "PDF pp. 2-1", "PDF pp. 1–99999", "PDF p. 1.5", "PDF pp. 1, 99999", "PDF p. xyz", "PDF p. 1, -2", "PDF pp. 1 - x"])
def test_nonexistent_or_invalid_pages_block_audit(pointer):
    bundle = {"page_count": 1, "pages": [{"pdf_page": 1}], "evidence_inventory": {}}
    result = auditor.audit(card(pointer), bundle, "page-grounded")
    assert result["summary"]["status"] == "fail"
    assert any(f["code"] == "page_pointer_range" and f["level"] == "error" for f in result["findings"])


@pytest.mark.parametrize("pointer", ["PDF p. 1 (printed p. 24959), Fig. 2", "PDF pp. 1–3", "PDF pp. 1, 3", "PDF p. 3"])
def test_valid_pages_ranges_and_printed_labels_pass(pointer):
    bundle = {"page_count": 3, "pages": [{"pdf_page": n} for n in (1, 2, 3)], "evidence_inventory": {}}
    assert auditor.audit(card(pointer), bundle, "page-grounded")["summary"]["status"] == "pass"


def test_sparse_source_map_uses_verified_indices_not_record_count():
    bundle = {"source_type": "source_map", "page_count": 2, "pages": [{"pdf_page": 1}, {"pdf_page": 10}], "evidence_inventory": {}}
    assert auditor.audit(card("PDF p. 10"), bundle, "page-grounded")["summary"]["status"] == "pass"
    assert auditor.audit(card("PDF p. 2"), bundle, "page-grounded")["summary"]["status"] == "fail"
    assert auditor.audit(card("PDF pp. 1-10"), bundle, "page-grounded")["summary"]["status"] == "fail"


def test_cli_fails_for_nonexistent_source_page(tmp_path):
    source, text = tmp_path / "bundle.json", tmp_path / "card.md"
    source.write_text(json.dumps({"page_count": 1, "pages": [{"pdf_page": 1}]}), encoding="utf-8")
    text.write_text(card("PDF p. 99999"), encoding="utf-8")
    result = subprocess.run([sys.executable, str(SCRIPT), "--card", str(text), "--bundle", str(source),
                             "--locator-mode", "page-grounded"], capture_output=True, text=True)
    assert result.returncode == 1
    assert "page_pointer_range" in result.stdout
