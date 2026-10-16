import importlib.util
from pathlib import Path
import sys

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "nature_citation.py"
spec = importlib.util.spec_from_file_location("journal_scope", SCRIPT)
citation = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = citation
spec.loader.exec_module(citation)


@pytest.mark.parametrize("journal", ["Nature and Science of Sleep", "Nature Imaginary Journal", "npj Invented Journal"])
def test_brand_prefix_does_not_establish_membership(journal):
    assert citation.journal_family(journal) is None
    assert not citation.in_scope(journal, "nature")
    assert not citation.in_scope(journal, "cns")


@pytest.mark.parametrize("journal", ["Nature", "Nature Materials", "Nature Aging", "Scientific Reports", "npj Digital Medicine", "npj Computational Materials"])
def test_known_nature_titles_remain_in_scope(journal):
    assert citation.journal_family(journal) == "Nature Portfolio"
    assert citation.in_scope(journal, "nature")
    assert citation.in_scope(journal, "cns")


def test_whitespace_and_other_families_keep_their_existing_behavior():
    assert citation.in_scope("  Nature   Materials ", "nature")
    assert citation.in_scope("Science Advances", "science")
    assert citation.in_scope("Cell Reports", "cell")
    assert not citation.in_scope("Nature Materials", "flagship")
    assert citation.in_scope("Nature", "flagship")
