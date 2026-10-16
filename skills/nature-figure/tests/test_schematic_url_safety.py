"""URL safety tests for generate_openrouter_schematic.py (no network access)."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path
from unittest.mock import MagicMock, patch

SKILL = Path(__file__).parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


SCHEMATIC = load_module("nature_figure_schematic_url_test", SKILL / "scripts" / "generate_openrouter_schematic.py")


def _args(tmpdir: str) -> Namespace:
    return Namespace(outdir=tmpdir, basename="schematic", output_format="png", timeout=10, api_url="https://api.example/v1")


class ResponseUrlSafetyTests(unittest.TestCase):
    def test_save_outputs_refuses_non_http_image_url(self):
        response = {"data": [{"media_type": "image/png", "url": "file:///etc/hosts"}]}
        with patch("urllib.request.urlopen", side_effect=AssertionError("must not fetch")) as opened:
            with self.assertRaisesRegex(SystemExit, "non-http"):
                SCHEMATIC.save_outputs(response, {"prompt": "x"}, _args(tempfile.mkdtemp()))
        opened.assert_not_called()

    def test_save_outputs_refuses_local_image_url_host(self):
        response = {"data": [{"media_type": "image/png", "url": "http://127.0.0.1/x.png"}]}
        with patch("urllib.request.urlopen", side_effect=AssertionError("must not fetch")) as opened:
            with self.assertRaisesRegex(SystemExit, "local"):
                SCHEMATIC.save_outputs(response, {"prompt": "x"}, _args(tempfile.mkdtemp()))
        opened.assert_not_called()

    def test_save_outputs_downloads_https_image_url(self):
        response = {"data": [{"media_type": "image/png", "url": "https://cdn.example.com/x.png"}]}
        tmpdir = tempfile.mkdtemp()
        downloaded = MagicMock()
        downloaded.__enter__.return_value.read.return_value = b"PNGDATA"
        with patch("urllib.request.urlopen", return_value=downloaded) as opened:
            SCHEMATIC.save_outputs(response, {"prompt": "x"}, _args(tmpdir))
        opened.assert_called_once()
        self.assertEqual((Path(tmpdir) / "schematic.png").read_bytes(), b"PNGDATA")


if __name__ == "__main__":
    unittest.main()
