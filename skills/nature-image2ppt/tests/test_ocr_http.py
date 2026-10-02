from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import requests
from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "cli" / "image2ppt" / "runtime"
sys.path.insert(0, str(RUNTIME))

import deck_text_hints  # noqa: E402
import paddle_text_hints  # noqa: E402
import runtime_env  # noqa: E402


class FakeResponse:
    def __init__(self, *, status_code: int = 200, payload: dict | None = None, text: str = "") -> None:
        self.status_code = status_code
        self._payload = payload or {}
        self.text = text

    def json(self) -> dict:
        return self._payload

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise requests.HTTPError(f"status={self.status_code}")


def write_run(run: Path) -> Path:
    page = run / "pages" / "page_001"
    page.mkdir(parents=True)
    image = Image.new("RGB", (640, 360), "white")
    draw = ImageDraw.Draw(image)
    for index in range(8):
        y = 30 + index * 35
        for char in range(8):
            x = 40 + char * 16
            draw.rectangle([x, y, x + 9, y + 18], outline="black", width=2)
    image.save(page / "source.png")
    (run / "deck_manifest.json").write_text(
        json.dumps({"schema_version": 1, "job_dir": str(run), "input_type": "images", "pages": []}),
        encoding="utf-8",
    )
    (run / "page_jobs.json").write_text(
        json.dumps({"schema_version": 1, "pages": [{"page_id": "page_001", "page_dir": "pages/page_001", "status": "pending"}]}),
        encoding="utf-8",
    )
    return page


class PaddleHttpRegressionTests(unittest.TestCase):
    def test_project_config_precedes_legacy_user_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = root / "skill"
            user = root / "user"
            project.mkdir()
            user.mkdir()
            (project / "config.yaml").write_text('PADDLE_OCR_TOKEN: "project-token"\n', encoding="utf-8")
            (user / "config.yaml").write_text('PADDLE_OCR_TOKEN: "user-token"\n', encoding="utf-8")
            with patch.object(runtime_env, "SKILL_ROOT", project), patch.object(
                runtime_env, "DEFAULT_CONFIG_HOME", str(user)
            ), patch.dict(os.environ, {"IMAGE2PPT_CONFIG_HOME": ""}, clear=False):
                self.assertEqual(project / "config.yaml", runtime_env.config_path())
                self.assertEqual("project", runtime_env.config_scope())

    def test_token_environment_has_priority_over_local_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            (home / "config.yaml").write_text('PADDLE_OCR_TOKEN: "config-token"\n', encoding="utf-8")
            with patch.dict(
                os.environ,
                {"IMAGE2PPT_CONFIG_HOME": str(home), "PADDLE_OCR_TOKEN": "environment-token"},
                clear=False,
            ):
                self.assertEqual(deck_text_hints.paddle_token(), "environment-token")

    def test_submit_parameters_and_normal_jsonl_result(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "page.png"
            Image.new("RGB", (20, 20), "white").save(source)
            submitted = FakeResponse(payload={"data": {"jobId": "job-123"}})
            status = FakeResponse(
                payload={"data": {"state": "done", "resultUrl": {"jsonUrl": "https://example.test/result.jsonl"}}}
            )
            payload = {
                "result": {
                    "layoutParsingResults": [
                        {"prunedResult": {"width": 20, "height": 20, "parsing_res_list": []}}
                    ]
                }
            }
            result_file = FakeResponse(text=json.dumps(payload) + "\n")
            with patch.object(paddle_text_hints.requests, "post", return_value=submitted) as post, patch.object(
                paddle_text_hints.requests, "get", side_effect=[status, result_file]
            ) as get:
                pages = paddle_text_hints.submit_and_fetch(source, "secret-token", "PaddleOCR-VL-1.6", 30)
            self.assertEqual(len(pages), 1)
            self.assertEqual(post.call_args.args[0], paddle_text_hints.JOB_URL)
            self.assertEqual(post.call_args.kwargs["headers"]["Authorization"], "bearer secret-token")
            self.assertEqual(post.call_args.kwargs["data"]["model"], "PaddleOCR-VL-1.6")
            optional = json.loads(post.call_args.kwargs["data"]["optionalPayload"])
            self.assertEqual(optional["useDocOrientationClassify"], False)
            self.assertEqual(get.call_count, 2)

    def test_empty_result_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "page.png"
            Image.new("RGB", (20, 20), "white").save(source)
            responses = [
                FakeResponse(payload={"data": {"state": "done", "resultUrl": {"jsonUrl": "https://example.test/empty"}}}),
                FakeResponse(text=""),
            ]
            with patch.object(
                paddle_text_hints.requests,
                "post",
                return_value=FakeResponse(payload={"data": {"jobId": "empty-job"}}),
            ), patch.object(paddle_text_hints.requests, "get", side_effect=responses):
                with self.assertRaisesRegex(RuntimeError, "returned no pages"):
                    paddle_text_hints.submit_and_fetch(source, "token", paddle_text_hints.DEFAULT_MODEL, 30)

    def test_endpoint_error_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "page.png"
            Image.new("RGB", (20, 20), "white").save(source)
            with patch.object(
                paddle_text_hints.requests,
                "post",
                return_value=FakeResponse(status_code=503, text="unavailable"),
            ):
                with self.assertRaisesRegex(RuntimeError, r"submit failed \(503\)"):
                    paddle_text_hints.submit_and_fetch(source, "token", paddle_text_hints.DEFAULT_MODEL, 30)

    def test_failed_job_state_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "page.png"
            Image.new("RGB", (20, 20), "white").save(source)
            with patch.object(
                paddle_text_hints.requests,
                "post",
                return_value=FakeResponse(payload={"data": {"jobId": "failed-job"}}),
            ), patch.object(
                paddle_text_hints.requests,
                "get",
                return_value=FakeResponse(payload={"data": {"state": "failed", "errorMsg": "bad input"}}),
            ):
                with self.assertRaisesRegex(RuntimeError, "PaddleOCR job failed: bad input"):
                    paddle_text_hints.submit_and_fetch(source, "token", paddle_text_hints.DEFAULT_MODEL, 30)

    def test_polling_timeout_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "page.png"
            Image.new("RGB", (20, 20), "white").save(source)
            with patch.object(
                paddle_text_hints.requests,
                "post",
                return_value=FakeResponse(payload={"data": {"jobId": "slow-job"}}),
            ), patch.object(
                paddle_text_hints.requests,
                "get",
                return_value=FakeResponse(payload={"data": {"state": "running"}}),
            ), patch.object(
                paddle_text_hints.time,
                "time",
                side_effect=[100.0, 101.0],
            ):
                with self.assertRaisesRegex(RuntimeError, r"timed out after 0s \(state=running\)"):
                    paddle_text_hints.submit_and_fetch(source, "token", paddle_text_hints.DEFAULT_MODEL, 0)

    def test_network_exception_is_not_reinterpreted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "page.png"
            Image.new("RGB", (20, 20), "white").save(source)
            with patch.object(
                paddle_text_hints.requests,
                "post",
                side_effect=requests.ConnectionError("offline"),
            ):
                with self.assertRaises(requests.ConnectionError):
                    paddle_text_hints.submit_and_fetch(source, "token", paddle_text_hints.DEFAULT_MODEL, 30)

    def test_cloud_failure_falls_back_and_writes_text_hints(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run = Path(tmp) / "run"
            page = write_run(run)
            argv = ["deck_text_hints.py", str(run), "--no-overlay"]
            with patch.object(deck_text_hints, "paddle_token", return_value="configured-token"), patch.object(
                deck_text_hints, "paddle_pages", side_effect=RuntimeError("mock endpoint failure")
            ), patch.object(sys, "argv", argv):
                self.assertEqual(deck_text_hints.main(), 0)
            hints = json.loads((page / "text_hints.json").read_text(encoding="utf-8"))
            self.assertEqual(hints["backend"], "builtin-ink")
            self.assertTrue(hints["lines"])

    def test_image_pages_are_submitted_directly_one_job_per_page(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run = Path(tmp) / "run"
            page_dirs = []
            for index in range(2):
                page = run / "pages" / f"page_{index + 1:03d}"
                page.mkdir(parents=True)
                Image.new("RGB", (40, 30), "white").save(page / "source.png")
                page_dirs.append(page)
            deck = {"input_type": "images"}
            pruned = {"width": 40, "height": 30, "parsing_res_list": []}

            with patch.object(
                paddle_text_hints,
                "submit_and_fetch",
                side_effect=[[pruned], [pruned]],
            ) as submit:
                results = deck_text_hints.paddle_pages(run, deck, page_dirs, "token", 30)

            self.assertEqual(list(results), page_dirs)
            self.assertEqual(
                [call.args[0] for call in submit.call_args_list],
                [page / "source.png" for page in page_dirs],
            )

    def test_original_pdf_is_submitted_as_one_multi_page_job(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run = Path(tmp) / "run"
            input_dir = run / "input"
            input_dir.mkdir(parents=True)
            original = input_dir / "original.pdf"
            original.write_bytes(b"pdf fixture")
            page_dirs = []
            for index in range(2):
                page = run / "pages" / f"page_{index + 1:03d}"
                page.mkdir(parents=True)
                Image.new("RGB", (40, 30), "white").save(page / "source.png")
                page_dirs.append(page)
            deck = {"input_type": "pdf"}
            pruned = {"width": 40, "height": 30, "parsing_res_list": []}

            with patch.object(
                paddle_text_hints,
                "submit_and_fetch",
                return_value=[pruned, pruned],
            ) as submit:
                results = deck_text_hints.paddle_pages(run, deck, page_dirs, "token", 30)

            self.assertEqual(list(results), page_dirs)
            submit.assert_called_once_with(original, "token", paddle_text_hints.DEFAULT_MODEL, 30)

    def test_pdf_without_original_submits_normalized_images_directly(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run = Path(tmp) / "run"
            page = run / "pages" / "page_001"
            page.mkdir(parents=True)
            source = page / "source.png"
            Image.new("RGB", (40, 30), "white").save(source)
            pruned = {"width": 40, "height": 30, "parsing_res_list": []}

            with patch.object(
                paddle_text_hints,
                "submit_and_fetch",
                return_value=[pruned],
            ) as submit:
                results = deck_text_hints.paddle_pages(
                    run,
                    {"input_type": "pdf"},
                    [page],
                    "token",
                    30,
                )

            self.assertEqual(list(results), [page])
            submit.assert_called_once_with(source, "token", paddle_text_hints.DEFAULT_MODEL, 30)

    def test_ocr_blocks_become_content_aware_measured_hints(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            page = Path(tmp)
            image = Image.new("RGB", (320, 180), "white")
            draw = ImageDraw.Draw(image)
            for char in range(8):
                x = 40 + char * 18
                draw.rectangle([x, 60, x + 10, 82], outline="black", width=2)
            image.save(page / "source.png")
            pruned = {
                "width": 320,
                "height": 180,
                "parsing_res_list": [
                    {"block_label": "text", "block_content": "示例文本", "block_bbox": [30, 50, 210, 95]},
                    {"block_label": "image", "block_content": "ignore", "block_bbox": [0, 0, 320, 180]},
                ],
            }
            hints = paddle_text_hints.build_page_hints(page, pruned)
            self.assertEqual(hints["backend"], "paddleocr-vl")
            self.assertEqual([line["text"] for line in hints["lines"]], ["示例文本"])
            self.assertIn(hints["lines"][0]["glyph_source"], {"ink-measured", "bbox-estimate"})
            self.assertIn("font_pt", hints["lines"][0])


if __name__ == "__main__":
    unittest.main()
