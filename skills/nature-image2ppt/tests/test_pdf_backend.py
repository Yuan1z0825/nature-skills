from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "cli" / "image2ppt" / "runtime"
sys.path.insert(0, str(RUNTIME))

import _input_normalization
from _input_normalization import render_pdf_pages


class PdfiumBackendTest(unittest.TestCase):
    def test_pdf_page_renders_at_requested_dpi(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "中文 空格"
            root.mkdir()
            pdf = root / "source.pdf"
            Image.new("RGB", (100, 60), "white").save(pdf, "PDF", resolution=72.0)

            outputs = render_pdf_pages(pdf, root / "输出 页", dpi=144)
            pdf.unlink()

            self.assertEqual(1, len(outputs))
            self.assertFalse(pdf.exists())
            with Image.open(outputs[0]) as rendered:
                self.assertEqual((200, 120), rendered.size)
                self.assertEqual("RGB", rendered.mode)

    def test_multi_page_pdf_preserves_page_order_size_and_color(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pdf = root / "source.pdf"
            images = [
                Image.new("RGB", (120, 60), (235, 30, 30)),
                Image.new("RGB", (70, 140), (30, 30, 235)),
            ]
            try:
                images[0].save(
                    pdf,
                    "PDF",
                    save_all=True,
                    append_images=images[1:],
                    resolution=72.0,
                    quality=100,
                    subsampling=0,
                )
            finally:
                for image in images:
                    image.close()

            outputs = render_pdf_pages(pdf, root / "pages", dpi=72)

            self.assertEqual(["page_001", "page_002"], [path.parent.name for path in outputs])
            expected = [((120, 60), 0), ((70, 140), 2)]
            for output, (size, dominant) in zip(outputs, expected):
                with Image.open(output) as rendered:
                    self.assertEqual(size, rendered.size)
                    self.assertEqual("RGB", rendered.mode)
                    center = rendered.getpixel((size[0] // 2, size[1] // 2))
                self.assertGreater(center[dominant], 180)
                self.assertLess(max(center[channel] for channel in range(3) if channel != dominant), 100)

    def test_legacy_ppt_conversion_uses_requested_dpi(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "legacy.ppt"
            source.write_bytes(b"legacy-ppt-placeholder")
            observed_dpi = []

            def convert_ppt_to_pptx(_source: Path, out_dir: Path) -> Path:
                converted = out_dir / "legacy.pptx"
                converted.write_bytes(b"converted-pptx-placeholder")
                return converted

            def convert_office_to_pdf(_source: Path, out_dir: Path) -> Path:
                converted = out_dir / "legacy.pdf"
                converted.write_bytes(b"converted-pdf-placeholder")
                return converted

            def render_pdf_pages(_pdf: Path, pages_dir: Path, dpi: int) -> list[Path]:
                observed_dpi.append(dpi)
                page = pages_dir / "page_001" / "source.png"
                page.parent.mkdir(parents=True, exist_ok=True)
                Image.new("RGB", (10, 10), "white").save(page)
                return [page]

            with (
                mock.patch.object(_input_normalization, "convert_ppt_to_pptx", side_effect=convert_ppt_to_pptx),
                mock.patch.object(_input_normalization, "collect_notes_from_pptx", return_value=[]),
                mock.patch.object(_input_normalization, "convert_office_to_pdf", side_effect=convert_office_to_pdf),
                mock.patch.object(_input_normalization, "render_pdf_pages", side_effect=render_pdf_pages),
            ):
                manifest = _input_normalization.normalize_inputs(
                    [source],
                    job_dir=root / "job",
                    dpi=123,
                )

            self.assertEqual([123], observed_dpi)
            self.assertTrue(manifest.is_file())


if __name__ == "__main__":
    unittest.main()
