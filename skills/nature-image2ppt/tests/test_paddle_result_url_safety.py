"""Result-URL safety tests for paddle_text_hints.py (no network access)."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

RUNTIME = Path(__file__).parents[1] / "cli" / "image2ppt" / "runtime"

for _sibling in ("deck_run_state", "page_text_metrics", "text_hints"):
    sys.modules.setdefault(_sibling, MagicMock())


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


PADDLE = load_module("nature_image2ppt_paddle_url_test", RUNTIME / "paddle_text_hints.py")


def _post_response(job_id: str) -> MagicMock:
    response = MagicMock(status_code=200)
    response.json.return_value = {"data": {"jobId": job_id}}
    return response


def _status_response(json_url: str) -> MagicMock:
    response = MagicMock()
    response.json.return_value = {"data": {"state": "done", "resultUrl": {"jsonUrl": json_url}}}
    return response


class ResultUrlSafetyTests(unittest.TestCase):
    def setUp(self):
        handle = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        handle.write(b"png")
        handle.close()
        self.page = Path(handle.name)
        self.addCleanup(self.page.unlink, missing_ok=True)

    def test_submit_and_fetch_rejects_non_http_result_url(self):
        status = _status_response("file:///etc/hosts")
        with (
            patch.object(PADDLE.requests, "post", return_value=_post_response("job-1")),
            patch.object(PADDLE.requests, "get", side_effect=[status, AssertionError("must not fetch result")]) as getter,
        ):
            with self.assertRaisesRegex(RuntimeError, "non-http"):
                PADDLE.submit_and_fetch(self.page, "token", "model", timeout=60)
        self.assertEqual(getter.call_count, 1)

    def test_submit_and_fetch_rejects_local_result_url_host(self):
        status = _status_response("http://127.0.0.1/result.jsonl")
        with (
            patch.object(PADDLE.requests, "post", return_value=_post_response("job-1")),
            patch.object(PADDLE.requests, "get", side_effect=[status, AssertionError("must not fetch result")]) as getter,
        ):
            with self.assertRaisesRegex(RuntimeError, "local"):
                PADDLE.submit_and_fetch(self.page, "token", "model", timeout=60)
        self.assertEqual(getter.call_count, 1)

    def test_submit_and_fetch_accepts_https_result_url(self):
        jsonl = MagicMock(text='{"result": {"layoutParsingResults": [{"prunedResult": {"page": 1}}]}}')
        status = _status_response("https://results.example.com/job-1.jsonl")
        with (
            patch.object(PADDLE.requests, "post", return_value=_post_response("job-1")),
            patch.object(PADDLE.requests, "get", side_effect=[status, jsonl]) as getter,
        ):
            pages = PADDLE.submit_and_fetch(self.page, "token", "model", timeout=60)
        self.assertEqual(pages, [{"page": 1}])
        self.assertEqual(getter.call_count, 2)


if __name__ == "__main__":
    unittest.main()
