from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TEXT_AUDIT = ROOT / "skills/nature-figure/scripts/audit_pdf_text.py"
COLLISION_AUDIT = ROOT / "skills/nature-figure/scripts/audit_figure_collisions.py"


def write_pdf(path: Path, content: bytes) -> None:
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 200 100] "
        b"/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length %d >>\nstream\n" % len(content) + content + b"\nendstream",
    ]
    out = bytearray(b"%PDF-1.4\n")
    offsets = []
    for number, body in enumerate(objects, 1):
        offsets.append(len(out))
        out += b"%d 0 obj\n" % number + body + b"\nendobj\n"
    xref = len(out)
    out += b"xref\n0 %d\n0000000000 65535 f \n" % (len(objects) + 1)
    for offset in offsets:
        out += b"%010d 00000 n \n" % offset
    out += b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (len(objects) + 1, xref)
    path.write_bytes(bytes(out))


def run(script: Path, *args: object) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), *map(str, args)], capture_output=True, text=True
    )


class PdfTextAuditTests(unittest.TestCase):
    def audit(self, content: bytes) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as tmp:
            pdf = Path(tmp) / "figure.pdf"
            write_pdf(pdf, content)
            return run(TEXT_AUDIT, pdf)

    def test_scaled_text_matrix_with_unit_tf_passes(self) -> None:
        result = self.audit(b"BT /F1 1 Tf 12 0 0 12 20 40 Tm (Hello) Tj ET")
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_shrunk_text_matrix_fails(self) -> None:
        result = self.audit(b"BT /F1 12 Tf 0.25 0 0 0.25 20 40 Tm (Hello) Tj ET")
        self.assertEqual(result.returncode, 1, result.stdout)

    def test_cm_scaling_is_applied(self) -> None:
        result = self.audit(b"q 0.25 0 0 0.25 0 0 cm BT /F1 12 Tf 20 40 Td (Hi) Tj ET Q")
        self.assertEqual(result.returncode, 1, result.stdout)

    def test_plain_tf_still_works(self) -> None:
        self.assertEqual(self.audit(b"BT /F1 8 Tf 20 40 Td (Hi) Tj ET").returncode, 0)
        self.assertEqual(self.audit(b"BT /F1 4 Tf 20 40 Td (Hi) Tj ET").returncode, 1)


class CollisionAuditInputTests(unittest.TestCase):
    def test_non_pdf_input_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            text = Path(tmp) / "notes.txt"
            text.write_text("just some text\n", encoding="utf-8")
            result = run(COLLISION_AUDIT, text, "--json")
        self.assertEqual(result.returncode, 2, result.stdout)
        self.assertNotIn("PASS", result.stdout)
        self.assertIn("not a PDF", result.stderr)


if __name__ == "__main__":
    unittest.main()
