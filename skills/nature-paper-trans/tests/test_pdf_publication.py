import contextlib
import importlib.util
import io
from pathlib import Path

import pymupdf
from PIL import Image
import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "pages.py"


@pytest.mark.parametrize("sizes", [[(80, 100)], [(80, 100), (150, 90)]])
def test_assembled_pdf_syncs_writable_descriptor_and_reopens(tmp_path, monkeypatch, sizes):
    spec = importlib.util.spec_from_file_location("pdf_publication", SCRIPT)
    pages = importlib.util.module_from_spec(spec)
    with contextlib.redirect_stdout(io.StringIO()):
        spec.loader.exec_module(pages)
    Image.new("RGB", (32, 48), "red").save(tmp_path / "page.png")
    output = tmp_path / "assembly.pdf"
    rows = [{"attempt_id": str(i), "dimensions": [32, 48], "page_size": size,
             "work_dir": str(tmp_path), "output": "page.png"} for i, size in enumerate(sizes)]
    sync_modes = []
    original_open = open

    def track_open(file, mode="r", *args, **kwargs):
        if Path(file) == output:
            sync_modes.append(mode)
        return original_open(file, mode, *args, **kwargs)

    monkeypatch.setattr(pages, "open", track_open, raising=False)
    # Run the real fsync, including on Windows, rather than mocking away the failure.
    pages.create_pdf(str(output), rows)
    assert sync_modes == ["r+b"]
    with pymupdf.open(output) as pdf:
        assert len(pdf) == len(sizes)
        for page, size in zip(pdf, sizes):
            assert (page.rect.width, page.rect.height) == size
            assert len(page.get_images()) == 1
