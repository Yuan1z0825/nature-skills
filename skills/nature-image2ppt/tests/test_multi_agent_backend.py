import base64
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
from urllib import error
import zipfile
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
CLI_DIR = ROOT / "./cli"
RUNTIME_DIR = CLI_DIR / "image2ppt/runtime"
PROMPT_SCRIPT = ROOT / "scripts/build_page_worker_prompt.py"
sys.path.insert(0, str(CLI_DIR))

CLI_ENV = os.environ.copy()
CLI_ENV["PYTHONPATH"] = (
    str(CLI_DIR)
    if not CLI_ENV.get("PYTHONPATH")
    else str(CLI_DIR) + os.pathsep + CLI_ENV["PYTHONPATH"]
)
os.environ["PYTHONPATH"] = CLI_ENV["PYTHONPATH"]

from image2ppt.runtime import image_gen, runtime_env


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def run_cli(*args):
    return subprocess.run(
        [sys.executable, "-m", "image2ppt.cli", *[str(arg) for arg in args]],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )


def make_minimal_run(tmpdir):
    run_dir = Path(tmpdir)
    page_1 = run_dir / "pages/page_001"
    page_2 = run_dir / "pages/page_002"
    page_1.mkdir(parents=True)
    page_2.mkdir(parents=True)
    write_json(
        run_dir / "deck_manifest.json",
        {
            "schema_version": 1,
            "run_id": "run-test",
            "pages": [
                {
                    "page_id": "page_001",
                    "page_dir": "pages/page_001",
                    "page_request": "pages/page_001/page_request.json",
                },
                {
                    "page_id": "page_002",
                    "page_dir": "pages/page_002",
                    "page_request": "pages/page_002/page_request.json",
                },
            ],
        },
    )
    write_json(run_dir / "run_state.json", {"status": "inputs_prepared", "history": []})
    write_json(
        run_dir / "page_jobs.json",
        {
            "schema_version": 1,
            "run_id": "run-test",
            "max_concurrent_pages": 6,
            "pages": [
                {
                    "page_id": "page_001",
                    "status": "pending",
                    "page_dir": "pages/page_001",
                    "page_request": "pages/page_001/page_request.json",
                    "result": None,
                    "accepted": False,
                },
                {
                    "page_id": "page_002",
                    "status": "pending",
                    "page_dir": "pages/page_002",
                    "page_request": "pages/page_002/page_request.json",
                    "result": None,
                    "accepted": False,
                },
            ],
        },
    )
    for page_dir, page_id in [(page_1, "page_001"), (page_2, "page_002")]:
        write_json(page_dir / "page_request.json", {"schema_version": 1, "page_id": page_id})
    return run_dir


def valid_page_manifest(text="Valid Page"):
    return {
        "schema_version": 1,
        "source": {"width_px": 1600, "height_px": 900},
        "slide": {"width": 13.333, "height": 7.5},
        "content_box": {"left": 0, "top": 0, "width": 13.333, "height": 7.5},
        "text_boxes": [
            {
                "text": text,
                "box_px": [100, 100, 500, 80],
                "font_size": 24,
                "color": "#111111",
            }
        ],
        "shapes": [],
        "images": [],
        "visual_inventory": [],
        "background_strategy": {"type": "native", "color": "#ffffff"},
        "quality_checks": {
            "font_size_calibrated": True,
            "visual_inventory_matched": True,
            "background_strategy_checked": True,
            "shape_corner_geometry_checked": True,
        },
    }


def write_page_outputs(page_dir, text="Valid Page", validation_passed=True, manifest=None):
    write_json(page_dir / "manifest.json", manifest or valid_page_manifest(text))
    write_json(page_dir / "imagegen-jobs.json", {"schema_version": 1, "jobs": []})
    build = subprocess.run(
        [
            sys.executable,
            RUNTIME_DIR / "build_pptx_from_manifest.py",
            page_dir / "manifest.json",
            "--out",
            page_dir / "page.pptx",
        ],
        text=True,
        capture_output=True,
    )
    if build.returncode != 0:
        raise AssertionError(build.stderr or build.stdout)
    (page_dir / "preview.png").write_text("x", encoding="utf-8")
    (page_dir / "split_assets_contact.png").write_text("x", encoding="utf-8")
    write_json(page_dir / "validation.json", {"passed": validation_passed})
    write_json(
        page_dir / "page_result.json",
        {
            "page_manifest": "manifest.json",
            "imagegen_jobs": "imagegen-jobs.json",
            "page_pptx": "page.pptx",
            "preview": "preview.png",
            "contact_sheet": "split_assets_contact.png",
            "validation": "validation.json",
            "page_result": "page_result.json",
        },
    )


class MultiAgentBackendTest(unittest.TestCase):
    def test_codex_oauth_rejects_untrusted_base_url(self):
        with mock.patch.dict(
            os.environ,
            {"CODEX_IMAGES_BASE_URL": "https://example.test/backend-api/codex"},
            clear=False,
        ):
            with self.assertRaisesRegex(RuntimeError, "Codex OAuth credentials may only be sent"):
                image_gen._codex_base_url()

    def test_codex_oauth_accepts_only_official_https_base_url(self):
        with mock.patch.dict(
            os.environ,
            {"CODEX_IMAGES_BASE_URL": "https://chatgpt.com/backend-api/codex/v1"},
            clear=False,
        ):
            self.assertEqual(image_gen.DEFAULT_CODEX_IMAGES_BASE_URL, image_gen._codex_base_url())

    def test_codex_oauth_post_rejects_unofficial_url_before_loading_auth(self):
        with mock.patch.object(image_gen, "_load_codex_auth") as load_auth:
            with self.assertRaisesRegex(RuntimeError, "official ChatGPT Images endpoint"):
                image_gen._post_codex_image_json(
                    "https://example.test/images/generations",
                    {"model": "gpt-image-2", "prompt": "test"},
                    10,
                )
        load_auth.assert_not_called()

    def test_codex_oauth_redirect_handler_refuses_redirect(self):
        redirect_handlers = [
            handler
            for handler in image_gen._CODEX_OPENER.handlers
            if isinstance(handler, image_gen.request.HTTPRedirectHandler)
        ]
        self.assertEqual(
            [image_gen._NoCodexRedirectHandler],
            [type(handler) for handler in redirect_handlers],
        )
        req = image_gen.request.Request(
            "https://chatgpt.com/backend-api/codex/images/generations"
        )
        handler = image_gen._NoCodexRedirectHandler()
        with self.assertRaisesRegex(error.HTTPError, "Refusing Codex OAuth redirect"):
            handler.redirect_request(
                req,
                None,
                302,
                "Found",
                {},
                "https://example.test/capture",
            )

    def test_package_console_entrypoint_help(self):
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "image2ppt.cli",
                "--help",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("CLI for preparing, rebuilding, validating, and finalizing editable PPTX runs.", result.stdout)
        self.assertIn("Command groups", result.stdout)
        self.assertIn("usage: image2ppt", result.stdout)
        for command in ("setup", "doctor", "config", "prepare", "run", "image", "formula"):
            self.assertIn(command, result.stdout)
        for old_command in ("install", "uninstall", "update", "process-asset-sheet", "record-image", "queue-repairs"):
            self.assertNotIn(f"    {old_command}", result.stdout)

    def test_old_top_level_commands_are_removed(self):
        for command in ("status", "install", "uninstall", "update"):
            with self.subTest(command=command):
                result = subprocess.run(
                    [sys.executable, "-m", "image2ppt.cli", command, "--help"],
                    cwd=ROOT,
                    text=True,
                    capture_output=True,
                )
                self.assertNotEqual(0, result.returncode)
                self.assertIn("invalid choice", result.stderr)

    def test_removed_run_prompt_command_is_rejected(self):
        result = subprocess.run(
            [sys.executable, "-m", "image2ppt.cli", "run", "prompt", "--help"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertNotEqual(0, result.returncode)
        self.assertIn("invalid choice", result.stderr)

    def test_runtime_doctor_direct_entrypoint_is_cli_scoped(self):
        result = subprocess.run(
            [sys.executable, str(RUNTIME_DIR / "main.py"), "doctor", "--json"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(0, result.returncode, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(str(ROOT), payload["skill_root"])
        self.assertEqual("PaddleOCR-VL-1.6", payload["ocr"]["model"])
        self.assertEqual("builtin-ink", payload["ocr"]["fallback"]["backend"])
        self.assertNotIn("<repo-path>", json.dumps(payload, ensure_ascii=False))
        self.assertNotIn("pipx upgrade image2ppt", json.dumps(payload, ensure_ascii=False))

    def test_runtime_doctor_text_reports_ocr_and_system_dependencies(self):
        with tempfile.TemporaryDirectory() as tmp:
            env = os.environ.copy()
            env["IMAGE2PPT_CONFIG_HOME"] = tmp
            result = subprocess.run(
                [sys.executable, "-m", "image2ppt.cli", "doctor"],
                cwd=ROOT,
                env=env,
                text=True,
                capture_output=True,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertIn("OCR endpoint:", result.stdout)
            self.assertIn("OCR model: PaddleOCR-VL-1.6", result.stdout)
            self.assertIn("OCR fallback: builtin-ink", result.stdout)
            self.assertIn("PPTX renderer:", result.stdout)
            self.assertIn("image processing:", result.stdout)

    def test_image_batch_command_is_removed(self):
        result = subprocess.run(
            [sys.executable, "-m", "image2ppt.cli", "image", "batch", "--help"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertNotEqual(0, result.returncode)
        self.assertIn("invalid choice", result.stderr)

    def test_image_help_documents_backend_contract(self):
        result = subprocess.run(
            [sys.executable, "-m", "image2ppt.cli", "image", "--help"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("Backend selection:", result.stdout)
        self.assertIn("auto uses Codex OAuth", result.stdout)
        self.assertIn("openai-compatible-api", result.stdout)
        self.assertIn("image2ppt image edit --image pages/page_001/source.png", result.stdout)
        self.assertNotIn("batch", result.stdout)

    def test_image_generate_help_limits_public_parameters(self):
        result = subprocess.run(
            [sys.executable, "-m", "image2ppt.cli", "image", "generate", "--help"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(0, result.returncode, result.stderr)
        for expected in (
            "--backend",
            "--model",
            "--prompt",
            "--prompt-file",
            "--size",
            "--quality",
            "--out",
            "--force",
            "--dry-run",
            "--timeout",
        ):
            self.assertIn(expected, result.stdout)
        for removed in (
            "--n",
            "--background",
            "--output-format",
            "--output-compression",
            "--moderation",
            "--out-dir",
            "--augment",
            "--no-augment",
            "--use-case",
            "--scene",
            "--subject",
            "--composition",
            "--lighting",
            "--palette",
            "--materials",
            "--text",
            "--constraints",
            "--negative",
            "--downscale-max-dim",
            "--downscale-suffix",
        ):
            self.assertNotIn(removed, result.stdout)

    def test_image_edit_help_omits_unsupported_fidelity_flag(self):
        result = subprocess.run(
            [sys.executable, "-m", "image2ppt.cli", "image", "edit", "--help"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("usage: image2ppt image edit", result.stdout)
        self.assertIn("Background cleanup", result.stdout)
        self.assertIn("strict visual reference", result.stdout)
        for expected in ("--backend", "--model", "--size", "--quality", "--image", "--mask", "--out", "--dry-run"):
            self.assertIn(expected, result.stdout)
        self.assertNotIn("--input-fidelity", result.stdout)
        for removed in (
            "--n",
            "--background",
            "--output-format",
            "--output-compression",
            "--moderation",
            "--out-dir",
            "--augment",
            "--text",
            "--downscale-max-dim",
        ):
            self.assertNotIn(removed, result.stdout)

    def test_process_sheet_resolves_asset_source_relative_to_page_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            page_dir = Path(tmp) / "pages/page_001"
            assets_dir = page_dir / "assets"
            assets_dir.mkdir(parents=True)
            Image.new("RGB", (24, 24), "#ff00ff").save(assets_dir / "sheet.png")

            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "image2ppt.cli",
                    "image",
                    "process-sheet",
                    str(page_dir),
                    "--asset-sheet-source",
                    "assets/sheet.png",
                    "--chroma",
                    "copied-sheet.png",
                    "--skip-chroma",
                    "--skip-split",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertTrue((page_dir / "copied-sheet.png").exists())

    def test_process_sheet_accepts_absolute_asset_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            page_dir = root / "pages/page_001"
            page_dir.mkdir(parents=True)
            source = root / "generated-sheet.png"
            Image.new("RGB", (24, 24), "#ff00ff").save(source)

            result = run_cli(
                "image",
                "process-sheet",
                page_dir,
                "--asset-sheet-source",
                source,
                "--chroma",
                "copied-sheet.png",
                "--skip-chroma",
                "--skip-split",
            )

            self.assertEqual(0, result.returncode, result.stderr)
            self.assertTrue((page_dir / "copied-sheet.png").is_file())

    def test_process_sheet_rejects_output_paths_outside_page_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            page_dir = root / "pages/page_001"
            assets_dir = page_dir / "assets"
            assets_dir.mkdir(parents=True)
            source = assets_dir / "sheet.png"
            Image.new("RGB", (24, 24), "#ff00ff").save(source)

            for option in ("--chroma", "--alpha", "--assets-dir", "--split-manifest"):
                for value in (f"../outside-{option[2:]}", str(root / f"absolute-{option[2:]}")):
                    with self.subTest(option=option, value=value):
                        result = run_cli(
                            "image",
                            "process-sheet",
                            page_dir,
                            "--asset-sheet-source",
                            source.relative_to(page_dir),
                            option,
                            value,
                            "--skip-chroma",
                            "--skip-split",
                        )

                        self.assertNotEqual(0, result.returncode)
                        self.assertIn("Output path must", result.stderr)
                        self.assertFalse((page_dir.parent / f"outside-{option[2:]}").exists())
                        self.assertFalse((root / f"absolute-{option[2:]}").exists())
            self.assertFalse((page_dir / "imagegen_asset_sheet_chroma.png").exists())

    def test_process_sheet_rejects_unsafe_asset_names(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            page_dir = root / "pages/page_001"
            assets_dir = page_dir / "assets"
            assets_dir.mkdir(parents=True)
            alpha = assets_dir / "sheet.png"
            Image.new("RGBA", (64, 64), (0, 0, 0, 255)).save(alpha)

            unsafe_names = ("../../escaped", "..\\..\\escaped", "nested/escaped", str(root / "absolute-escaped"))
            for name in unsafe_names:
                with self.subTest(name=name):
                    result = run_cli(
                        "image",
                        "process-sheet",
                        page_dir,
                        "--alpha",
                        alpha.relative_to(page_dir),
                        "--skip-chroma",
                        "--asset-names",
                        name,
                    )

                    self.assertNotEqual(0, result.returncode)
                    self.assertIn("safe filename components", result.stderr)
            self.assertFalse((page_dir.parent / "escaped.png").exists())
            self.assertFalse((root / "absolute-escaped.png").exists())

    def test_process_sheet_scopes_default_outputs_by_job_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            page_dir = Path(tmp) / "pages/page_001"
            assets_dir = page_dir / "assets"
            assets_dir.mkdir(parents=True)

            for job_id, color in (("photo-sheet", "black"), ("icon-sheet", "blue")):
                source = assets_dir / f"{job_id}.png"
                image = Image.new("RGB", (120, 120), "#ff00ff")
                image.paste(color, (24, 24, 96, 96))
                image.save(source)

                result = run_cli(
                    "image",
                    "process-sheet",
                    page_dir,
                    "--job-id",
                    job_id,
                    "--asset-sheet-source",
                    source.relative_to(page_dir),
                    "--asset-names",
                    job_id,
                )
                self.assertEqual(0, result.returncode, result.stderr)
                self.assertTrue((assets_dir / f"{job_id}.asset-sheet-chroma.png").exists())
                self.assertTrue((assets_dir / f"{job_id}.asset-sheet-alpha.png").exists())
                self.assertTrue((assets_dir / f"{job_id}.split-report.json").exists())

            jobs = read_json(page_dir / "imagegen-jobs.json")["jobs"]
            self.assertEqual(["photo-sheet", "icon-sheet"], [job["job_id"] for job in jobs])
            self.assertEqual(["processed", "processed"], [job["status"] for job in jobs])
            self.assertFalse((page_dir / "imagegen_asset_sheet_chroma.png").exists())
            self.assertFalse((page_dir / "imagegen_asset_sheet_alpha.png").exists())
            self.assertFalse((page_dir / "split_assets.json").exists())

    def test_process_sheet_uses_imported_output_by_job_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            page_dir = Path(tmp) / "pages/page_001"
            assets_dir = page_dir / "assets"
            assets_dir.mkdir(parents=True)
            source = assets_dir / "imported-sheet.png"
            image = Image.new("RGB", (120, 120), "#ff00ff")
            image.paste("black", (24, 24, 96, 96))
            image.save(source)
            write_json(
                page_dir / "imagegen-jobs.json",
                {
                    "schema_version": 1,
                    "jobs": [
                        {
                            "job_id": "icon-sheet",
                            "role": "asset_sheet",
                            "status": "recorded",
                            "output": "assets/imported-sheet.png",
                        }
                    ],
                },
            )

            result = run_cli(
                "image",
                "process-sheet",
                page_dir,
                "--job-id",
                "icon-sheet",
                "--asset-names",
                "icon",
            )

            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertTrue((assets_dir / "icon-sheet.asset-sheet-alpha.png").is_file())
            self.assertTrue((assets_dir / "icon-sheet.split-report.json").is_file())
            self.assertTrue((assets_dir / "icon.png").is_file())
            self.assertEqual(read_json(page_dir / "imagegen-jobs.json")["jobs"][0]["status"], "processed")

    def test_process_sheet_checks_existing_alpha_before_copying_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            page_dir = Path(tmp) / "pages/page_001"
            assets_dir = page_dir / "assets"
            assets_dir.mkdir(parents=True)
            source = assets_dir / "icon-sheet.png"
            chroma = assets_dir / "icon-sheet.asset-sheet-chroma.png"
            alpha = assets_dir / "icon-sheet.asset-sheet-alpha.png"
            Image.new("RGB", (32, 32), "blue").save(source)
            Image.new("RGB", (32, 32), "black").save(chroma)
            Image.new("RGBA", (32, 32), (0, 0, 0, 0)).save(alpha)
            chroma_before = chroma.read_bytes()

            result = run_cli(
                "image",
                "process-sheet",
                page_dir,
                "--job-id",
                "icon-sheet",
                "--asset-sheet-source",
                source.relative_to(page_dir),
                "--skip-split",
            )

            self.assertNotEqual(0, result.returncode)
            self.assertIn("Output already exists", result.stderr)
            self.assertEqual(chroma_before, chroma.read_bytes())

    def test_process_sheet_rejects_unsafe_job_id_for_default_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            page_dir = Path(tmp) / "pages/page_001"
            assets_dir = page_dir / "assets"
            assets_dir.mkdir(parents=True)
            source = assets_dir / "sheet.png"
            Image.new("RGB", (32, 32), "#ff00ff").save(source)

            result = run_cli(
                "image",
                "process-sheet",
                page_dir,
                "--job-id",
                "../outside",
                "--asset-sheet-source",
                source.relative_to(page_dir),
                "--skip-split",
            )

            self.assertNotEqual(0, result.returncode)
            self.assertIn("safe filename component", result.stderr)
            self.assertFalse((page_dir.parent / "outside.asset-sheet-chroma.png").exists())

    def test_image_edit_passthrough_preserves_image_argument(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source.png"
            out = Path(tmp) / "out.png"
            Image.new("RGB", (24, 24), "white").save(source)
            env = os.environ.copy()
            env["CODEX_AUTH_FILE"] = str(Path(tmp) / "missing-auth.json")
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "image2ppt.cli",
                    "image",
                    "edit",
                    "--image",
                    str(source),
                    "--prompt",
                    "test",
                    "--out",
                    str(out),
                    "--dry-run",
                ],
                cwd=ROOT,
                env=env,
                text=True,
                capture_output=True,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual([str(source)], payload["image"])
            self.assertEqual("test", payload["prompt"])

    def test_provider_specific_model_routes_to_api_even_when_codex_auth_exists(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out.png"
            auth = Path(tmp) / "auth.json"
            write_json(auth, {"tokens": {"access_token": "test-token"}})
            env = os.environ.copy()
            env.update(
                {
                    "CODEX_AUTH_FILE": str(auth),
                    "OPENAI_API_KEY": "test-api-key",
                    "OPENAI_BASE_URL": "https://images.example.test/v1",
                    "IMAGE2PPT_IMAGE_BACKEND": "auto",
                    "IMAGE2PPT_IMAGE_MODEL": "provider/imagine-image-v2",
                }
            )
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "image2ppt.cli",
                    "image",
                    "generate",
                    "--prompt",
                    "test",
                    "--out",
                    str(out),
                    "--dry-run",
                ],
                cwd=ROOT,
                env=env,
                text=True,
                capture_output=True,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual("openai-compatible-api", payload["backend"])
            self.assertEqual("/v1/images/generations", payload["endpoint"])
            self.assertEqual("provider/imagine-image-v2", payload["model"])
            self.assertNotIn("size", payload)
            self.assertNotIn("quality", payload)

    def test_explicit_api_backend_overrides_codex_for_gpt_image_model(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out.png"
            auth = Path(tmp) / "auth.json"
            write_json(auth, {"tokens": {"access_token": "test-token"}})
            env = os.environ.copy()
            env.update(
                {
                    "CODEX_AUTH_FILE": str(auth),
                    "OPENAI_API_KEY": "test-api-key",
                    "OPENAI_BASE_URL": "https://images.example.test/v1",
                }
            )
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "image2ppt.cli",
                    "image",
                    "generate",
                    "--backend",
                    "openai-compatible-api",
                    "--model",
                    "gpt-image-1.5",
                    "--prompt",
                    "test",
                    "--out",
                    str(out),
                    "--dry-run",
                ],
                cwd=ROOT,
                env=env,
                text=True,
                capture_output=True,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual("openai-compatible-api", payload["backend"])

    def test_explicit_codex_backend_rejects_provider_specific_model(self):
        with tempfile.TemporaryDirectory() as tmp:
            auth = Path(tmp) / "auth.json"
            write_json(auth, {"tokens": {"access_token": "test-token"}})
            env = os.environ.copy()
            env["CODEX_AUTH_FILE"] = str(auth)
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "image2ppt.cli",
                    "image",
                    "generate",
                    "--backend",
                    "codex-oauth",
                    "--model",
                    "provider/imagine-image-v2",
                    "--prompt",
                    "test",
                    "--dry-run",
                ],
                cwd=ROOT,
                env=env,
                text=True,
                capture_output=True,
            )
            self.assertNotEqual(0, result.returncode)
            self.assertIn("supports GPT Image model ids only", result.stderr)

    def test_api_result_supports_base64_and_url_shapes(self):
        encoded = base64.b64encode(b"base64-image").decode("ascii")
        self.assertEqual(b"base64-image", image_gen._api_result_bytes({"b64_json": encoded}, 10))
        with mock.patch.object(
            image_gen,
            "_download_image_result",
            return_value=b"url-image",
        ) as download:
            self.assertEqual(
                b"url-image",
                image_gen._api_result_bytes({"url": "https://cdn.example.test/image.png"}, 10),
            )
        download.assert_called_once_with("https://cdn.example.test/image.png", 10)

    def test_api_client_applies_configured_user_agent_only_to_api_client(self):
        with mock.patch.dict(
            os.environ,
            {
                "OPENAI_API_KEY": "test-key",
                "OPENAI_BASE_URL": "https://images.example.test/v1",
                "IMAGE2PPT_IMAGE_USER_AGENT": "image2ppt-test-client/1.0",
            },
            clear=False,
        ), mock.patch("openai.OpenAI") as openai_client:
            image_gen._create_client()
        self.assertEqual(
            {"User-Agent": "image2ppt-test-client/1.0"},
            openai_client.call_args.kwargs["default_headers"],
        )

    def test_runtime_backend_selection_is_model_aware_and_explicitly_overridable(self):
        values = {
            "IMAGE2PPT_IMAGE_BACKEND": "auto",
            "IMAGE2PPT_IMAGE_MODEL": "provider/imagine-image-v2",
        }
        self.assertEqual(
            ("openai-compatible-api", True),
            runtime_env.select_image_backend(values, codex_ready=True, api_ready=True),
        )
        values.update(
            {
                "IMAGE2PPT_IMAGE_BACKEND": "openai-compatible-api",
                "IMAGE2PPT_IMAGE_MODEL": "gpt-image-2",
            }
        )
        self.assertEqual(
            ("openai-compatible-api", True),
            runtime_env.select_image_backend(values, codex_ready=True, api_ready=True),
        )

    def test_config_persists_generic_backend_model_and_user_agent(self):
        with tempfile.TemporaryDirectory() as tmp:
            env = os.environ.copy()
            env["IMAGE2PPT_CONFIG_HOME"] = tmp
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "image2ppt.cli",
                    "config",
                    "--api-key",
                    "test-api-key",
                    "--base-url",
                    "https://images.example.test/v1",
                    "--image-backend",
                    "openai-compatible-api",
                    "--model",
                    "provider/imagine-image-v2",
                    "--image-user-agent",
                    "image2ppt-test-client/1.0",
                ],
                cwd=ROOT,
                env=env,
                text=True,
                capture_output=True,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            config = runtime_env.read_config_file(Path(tmp) / "config.yaml")
            self.assertEqual("openai-compatible-api", config["IMAGE2PPT_IMAGE_BACKEND"])
            self.assertEqual("provider/imagine-image-v2", config["IMAGE2PPT_IMAGE_MODEL"])
            self.assertEqual("image2ppt-test-client/1.0", config["IMAGE2PPT_IMAGE_USER_AGENT"])
            self.assertNotIn("test-api-key", result.stdout)

    def test_image_edit_dry_run_prefers_codex_oauth_when_auth_exists(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source.png"
            out = Path(tmp) / "out.png"
            auth = Path(tmp) / "auth.json"
            Image.new("RGB", (24, 24), "white").save(source)
            write_json(auth, {"tokens": {"access_token": "test-token"}})
            env = os.environ.copy()
            env["CODEX_AUTH_FILE"] = str(auth)
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "image2ppt.cli",
                    "image",
                    "edit",
                    "--image",
                    str(source),
                    "--prompt",
                    "test",
                    "--out",
                    str(out),
                    "--dry-run",
                ],
                cwd=ROOT,
                env=env,
                text=True,
                capture_output=True,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual("codex-oauth", payload["backend"])
            self.assertEqual("https://chatgpt.com/backend-api/codex/images/edits", payload["endpoint"])
            self.assertEqual("edit", payload["operation"])
            self.assertEqual([str(source)], payload["input_images"])
            self.assertEqual("auto", payload["size"])
            self.assertEqual("auto", payload["quality"])
            self.assertEqual("auto", payload["background"])
            for removed in ("moderation", "output_format", "output_compression", "n"):
                self.assertNotIn(removed, payload)

    def test_image_generate_dry_run_prefers_codex_images_endpoint_when_auth_exists(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out.png"
            auth = Path(tmp) / "auth.json"
            write_json(auth, {"tokens": {"access_token": "test-token"}})
            env = os.environ.copy()
            env["CODEX_AUTH_FILE"] = str(auth)
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "image2ppt.cli",
                    "image",
                    "generate",
                    "--prompt",
                    "test",
                    "--out",
                    str(out),
                    "--dry-run",
                ],
                cwd=ROOT,
                env=env,
                text=True,
                capture_output=True,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual("codex-oauth", payload["backend"])
            self.assertEqual("https://chatgpt.com/backend-api/codex/images/generations", payload["endpoint"])
            self.assertEqual("generate", payload["operation"])
            self.assertEqual([], payload["input_images"])
            self.assertEqual("auto", payload["size"])
            self.assertEqual("auto", payload["quality"])
            self.assertEqual("auto", payload["background"])
            for removed in ("moderation", "output_format", "output_compression", "n"):
                self.assertNotIn(removed, payload)

    def test_codex_oauth_retries_transport_and_5xx_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            auth = Path(tmp) / "auth.json"
            write_json(auth, {"tokens": {"access_token": "test-token"}})

            class FakeResponse:
                def __enter__(self):
                    return self

                def __exit__(self, exc_type, exc, tb):
                    return False

                def read(self, _limit):
                    return b'{"data":[{"b64_json":"aW1hZ2U="}]}'

            http_500 = error.HTTPError(
                "https://example.test",
                500,
                "server error",
                hdrs=None,
                fp=io.BytesIO(b"temporary"),
            )
            env = os.environ.copy()
            env["CODEX_AUTH_FILE"] = str(auth)
            with mock.patch.dict(os.environ, env, clear=False), mock.patch(
                "image2ppt.runtime.image_gen._open_codex_request",
                side_effect=[http_500, FakeResponse()],
            ) as open_request, mock.patch("image2ppt.runtime.image_gen.time.sleep") as sleep:
                response = image_gen._post_codex_image_json(
                    "https://chatgpt.com/backend-api/codex/images/generations",
                    {"model": "gpt-image-2", "prompt": "test"},
                    10,
                )

            self.assertEqual(["aW1hZ2U="], [item["b64_json"] for item in response["data"]])
            self.assertEqual(2, open_request.call_count)
            sleep.assert_called_once()

            with mock.patch.dict(os.environ, env, clear=False), mock.patch(
                "image2ppt.runtime.image_gen._open_codex_request",
                side_effect=[error.URLError("temporary network failure"), FakeResponse()],
            ) as open_request, mock.patch("image2ppt.runtime.image_gen.time.sleep") as sleep:
                response = image_gen._post_codex_image_json(
                    "https://chatgpt.com/backend-api/codex/images/generations",
                    {"model": "gpt-image-2", "prompt": "test"},
                    10,
                )

            self.assertEqual(["aW1hZ2U="], [item["b64_json"] for item in response["data"]])
            self.assertEqual(2, open_request.call_count)
            sleep.assert_called_once()

            http_429 = error.HTTPError(
                "https://example.test",
                429,
                "rate limited",
                hdrs=None,
                fp=io.BytesIO(b"rate limit"),
            )
            with mock.patch.dict(os.environ, env, clear=False), mock.patch(
                "image2ppt.runtime.image_gen._open_codex_request",
                side_effect=http_429,
            ) as open_request, mock.patch("image2ppt.runtime.image_gen.time.sleep") as sleep:
                with self.assertRaisesRegex(RuntimeError, r"HTTP 429"):
                    image_gen._post_codex_image_json(
                        "https://chatgpt.com/backend-api/codex/images/generations",
                        {"model": "gpt-image-2", "prompt": "test"},
                        10,
                    )

            self.assertEqual(1, open_request.call_count)
            sleep.assert_not_called()

    def test_runtime_config_writes_owner_only_yaml(self):
        with tempfile.TemporaryDirectory() as tmp:
            env = os.environ.copy()
            env["IMAGE2PPT_CONFIG_HOME"] = tmp
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "image2ppt.cli",
                    "config",
                    "--api-key",
                    "sk-test-secret",
                    "--base-url",
                    "https://example.test/v1",
                    "--model",
                    "gpt-image-2",
                ],
                cwd=ROOT,
                env=env,
                text=True,
                capture_output=True,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            config_path = Path(tmp) / "config.yaml"
            self.assertTrue(config_path.exists())
            text = config_path.read_text(encoding="utf-8")
            self.assertIn("OPENAI_API_KEY: sk-test-secret", text)
            if sys.platform != "win32":
                mode = config_path.stat().st_mode
                self.assertFalse(mode & 0o077)

    def test_runtime_doctor_json_checks_cli_deps_without_large_tools(self):
        with tempfile.TemporaryDirectory() as tmp:
            env = os.environ.copy()
            env["IMAGE2PPT_CONFIG_HOME"] = tmp
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "image2ppt.cli",
                    "doctor",
                    "--json",
                ],
                cwd=ROOT,
                env=env,
                text=True,
                capture_output=True,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual({"pypdfium2", "PIL", "openai", "yaml", "numpy", "requests"}, set(payload["dependencies"]))
            self.assertFalse(payload["image_backend"]["agent_builtin"]["checked"])
            self.assertIsNone(payload["image_backend"]["agent_builtin"]["ready"])
            self.assertEqual(str(ROOT), payload["skill_root"])
            self.assertIn("rendering", payload)
            self.assertIn("image_processing", payload)
            self.assertIn("internal_resources", payload)

    def test_setup_is_idempotent_and_preserves_config(self):
        with tempfile.TemporaryDirectory() as tmp:
            env = os.environ.copy()
            env["IMAGE2PPT_CONFIG_HOME"] = str(Path(tmp) / "config")
            configured = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "image2ppt.cli",
                    "config",
                    "--api-key",
                    "sk-test-secret",
                    "--base-url",
                    "https://example.test/v1",
                    "--model",
                    "gpt-image-2",
                ],
                cwd=ROOT,
                env=env,
                text=True,
                capture_output=True,
            )
            self.assertEqual(0, configured.returncode, configured.stderr)

            first = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "image2ppt.cli",
                    "setup",
                ],
                cwd=ROOT,
                env=env,
                text=True,
                capture_output=True,
            )
            self.assertEqual(0, first.returncode, first.stderr)
            first_payload = json.loads(first.stdout)
            self.assertEqual("ok", first_payload["setup"])
            config_path = Path(env["IMAGE2PPT_CONFIG_HOME"]) / "config.yaml"
            before = config_path.read_text(encoding="utf-8")

            second = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "image2ppt.cli",
                    "setup",
                ],
                cwd=ROOT,
                env=env,
                text=True,
                capture_output=True,
            )
            self.assertEqual(0, second.returncode, second.stderr)
            second_payload = json.loads(second.stdout)
            self.assertEqual("ok", second_payload["setup"])
            self.assertEqual(before, config_path.read_text(encoding="utf-8"))

    def test_unified_cli_backend_defaults_to_image2ppt_image_cli(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = make_minimal_run(tmp)
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "image2ppt.cli",
                    "run",
                    "backend",
                    run_dir,
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            deck = read_json(run_dir / "deck_manifest.json")
            backend = deck["image_backend"]
            self.assertEqual("image2ppt-image-cli", backend["backend_id"])
            self.assertEqual("image2ppt image", backend["tool_name"])
            self.assertEqual("image2ppt image generate/edit", backend["tool_call"])
            self.assertFalse(backend["requires_openai_api_key"])

    def test_prepare_writes_default_backend_contract(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "slide.png"
            Image.new("RGB", (320, 180), "white").save(source)
            out_root = Path(tmp) / "runs"
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "image2ppt.cli",
                    "prepare",
                    str(source),
                    "--out-root",
                    str(out_root),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            deck_line = next(line for line in result.stdout.splitlines() if line.endswith("deck_manifest.json"))
            deck_path = Path(deck_line)
            self.assertTrue(deck_path.exists())
            deck = read_json(deck_path)
            self.assertEqual("image2ppt-image-cli", deck["image_backend"]["backend_id"])
            request = read_json(deck_path.parent / "pages/page_001/page_request.json")
            self.assertEqual(deck["image_backend"], request["image_backend"])

    def test_prepare_writes_builtin_imagegen_contract_when_selected(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "slide.png"
            Image.new("RGB", (320, 180), "white").save(source)
            out_root = Path(tmp) / "runs"
            result = run_cli(
                "prepare",
                source,
                "--out-root",
                out_root,
                "--image-backend",
                "builtin-imagegen",
                "--no-text-hints",
            )
            self.assertEqual(0, result.returncode, result.stderr)
            deck_line = next(line for line in result.stdout.splitlines() if line.endswith("deck_manifest.json"))
            deck_path = Path(deck_line)
            backend = read_json(deck_path)["image_backend"]
            self.assertEqual("builtin-imagegen", backend["backend_id"])
            self.assertEqual("image_gen.imagegen", backend["tool_name"])
            self.assertIsNone(backend["model"])
            self.assertEqual(
                {"generate": ["prompt"], "edit": ["prompt", "referenced_image_paths"]},
                backend["required_parameters"],
            )
            self.assertEqual(["codex-oauth", "openai-compatible-api"], backend["fallback_order"])
            self.assertEqual(
                ["tool-unavailable", "tool-error", "input-unreadable", "no-valid-local-output"],
                backend["fallback_policy"]["on"],
            )
            self.assertFalse(backend["fallback_policy"]["missing_optional_parameters"])
            self.assertIn("view_image", backend["input_context_policy"])
            self.assertIn("never scan for the newest file", backend["save_path_policy"])
            request = read_json(deck_path.parent / "pages/page_001/page_request.json")
            self.assertEqual(backend, request["image_backend"])

    def test_skill_prompt_script_output_is_accepted_by_dispatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = make_minimal_run(tmp)
            write_json(
                run_dir / "deck_manifest.json",
                {
                    "schema_version": 1,
                    "run_id": "run-test",
                    "image_backend": {"backend_id": "image2ppt-image-cli"},
                    "pages": [],
                },
            )
            result = subprocess.run(
                [sys.executable, "-m", "image2ppt.cli", "run", "next", run_dir, "--json"],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual("dispatch_pages", payload["stage"])
            prompt_path = (run_dir / "pages/page_001/worker-prompt.md").resolve()
            self.assertEqual(str(prompt_path), payload["prompt_file"])
            self.assertIn(str(prompt_path), payload["next_command"])
            self.assertIn("image2ppt run dispatch", payload["next_command"])
            self.assertNotIn("--local", payload["next_command"])

            prompt = subprocess.run(
                [
                    sys.executable,
                    PROMPT_SCRIPT,
                    run_dir,
                    "--page",
                    "page_001",
                    "--out",
                    str(prompt_path),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            self.assertEqual(0, prompt.returncode, prompt.stderr)
            prompt_text = prompt_path.read_text(encoding="utf-8")
            self.assertIn(str(run_dir), prompt_text)
            normalized_prompt = prompt_text.replace("\\", "/")
            expected_reference = str(ROOT / "references/page-decision-tree.md").replace("\\", "/")
            self.assertIn(expected_reference, normalized_prompt)
            self.assertIn("image_gen.imagegen", prompt_text)
            self.assertIn("referenced_image_paths", prompt_text)
            self.assertIn("Missing `mask`, `model`, `size`, `quality`, or `out` never triggers fallback", prompt_text)
            self.assertIn('never a scanned "newest" file', prompt_text)

            local_dispatch = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "image2ppt.cli",
                    "run",
                    "dispatch",
                    run_dir,
                    "--page",
                    "page_001",
                    "--agent-id",
                    "main",
                    "--prompt-file",
                    str(prompt_path),
                    "--local",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            self.assertNotEqual(0, local_dispatch.returncode)
            self.assertIn("--local dispatch is only allowed", local_dispatch.stdout + local_dispatch.stderr)

            dispatch = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "image2ppt.cli",
                    "run",
                    "dispatch",
                    run_dir,
                    "--page",
                    "page_001",
                    "--agent-id",
                    "worker-1",
                    "--prompt-file",
                    str(prompt_path),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            self.assertEqual(0, dispatch.returncode, dispatch.stderr)
            jobs = read_json(run_dir / "page_jobs.json")
            self.assertEqual("dispatched", jobs["pages"][0]["status"])
            self.assertEqual("worker", jobs["pages"][0]["dispatch"]["execution_mode"])

    def test_single_page_next_uses_local_rebuild_with_same_record_flow(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = make_minimal_run(tmp)
            deck = read_json(run_dir / "deck_manifest.json")
            deck["image_backend"] = {"backend_id": "image2ppt-image-cli"}
            deck["pages"] = deck["pages"][:1]
            write_json(run_dir / "deck_manifest.json", deck)
            jobs = read_json(run_dir / "page_jobs.json")
            jobs["pages"] = jobs["pages"][:1]
            write_json(run_dir / "page_jobs.json", jobs)

            next_result = subprocess.run(
                [sys.executable, "-m", "image2ppt.cli", "run", "next", run_dir, "--json"],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            self.assertEqual(0, next_result.returncode, next_result.stderr)
            next_payload = json.loads(next_result.stdout)
            self.assertEqual("rebuild_page_locally", next_payload["stage"])
            self.assertEqual(["page_001"], next_payload["suggested_pages"])
            self.assertIn("image2ppt run dispatch", next_payload["next_command"])
            self.assertIn("--agent-id main", next_payload["next_command"])
            self.assertIn("--local", next_payload["next_command"])

            page_dir = run_dir / "pages/page_001"
            write_page_outputs(page_dir, "Direct Page")

            record_pending = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "image2ppt.cli",
                    "run",
                    "record",
                    run_dir,
                    "--page",
                    "page_001",
                    "--agent-id",
                    "main",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            self.assertNotEqual(0, record_pending.returncode)
            self.assertIn("must be dispatched", record_pending.stderr)

            prompt_path = (run_dir / "pages/page_001/worker-prompt.md").resolve()
            prompt = subprocess.run(
                [
                    sys.executable,
                    PROMPT_SCRIPT,
                    run_dir,
                    "--page",
                    "page_001",
                    "--out",
                    str(prompt_path),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            self.assertEqual(0, prompt.returncode, prompt.stderr)

            dispatch = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "image2ppt.cli",
                    "run",
                    "dispatch",
                    run_dir,
                    "--page",
                    "page_001",
                    "--agent-id",
                    "main",
                    "--prompt-file",
                    str(prompt_path),
                    "--local",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            self.assertEqual(0, dispatch.returncode, dispatch.stderr)
            jobs = read_json(run_dir / "page_jobs.json")
            self.assertEqual("dispatched", jobs["pages"][0]["status"])
            self.assertEqual("main", jobs["pages"][0]["dispatch"]["agent_id"])
            self.assertEqual("local", jobs["pages"][0]["dispatch"]["execution_mode"])

            record = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "image2ppt.cli",
                    "run",
                    "record",
                    run_dir,
                    "--page",
                    "page_001",
                    "--agent-id",
                    "main",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            self.assertEqual(0, record.returncode, record.stderr)
            jobs = read_json(run_dir / "page_jobs.json")
            result_payload = jobs["pages"][0]["result"]
            self.assertEqual("recorded", jobs["pages"][0]["status"])
            self.assertEqual("local-main-agent", result_payload["record_mode"])

    def test_configure_image_backend_writes_deck_and_requests(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = make_minimal_run(tmp)
            result = subprocess.run(
                [
                    sys.executable,
                    RUNTIME_DIR / "configure_image_backend.py",
                    run_dir,
                    "--backend-id",
                    "image2ppt-image-cli",
                    "--tool-name",
                    "image2ppt image",
                    "--model",
                    "gpt-image-2",
                ],
                text=True,
                capture_output=True,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            deck = read_json(run_dir / "deck_manifest.json")
            self.assertEqual("image2ppt-image-cli", deck["image_backend"]["backend_id"])
            request = read_json(run_dir / "pages/page_002/page_request.json")
            self.assertEqual(deck["image_backend"], request["image_backend"])

    def test_configure_image_backend_uses_configured_provider_model_by_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = make_minimal_run(tmp)
            config_home = Path(tmp) / "config-home"
            config_home.mkdir()
            (config_home / "config.yaml").write_text(
                "IMAGE2PPT_IMAGE_MODEL: provider/imagine-image-v2\n",
                encoding="utf-8",
            )
            env = os.environ.copy()
            env["IMAGE2PPT_CONFIG_HOME"] = str(config_home)
            env.pop("IMAGE2PPT_IMAGE_MODEL", None)
            result = subprocess.run(
                [
                    sys.executable,
                    RUNTIME_DIR / "configure_image_backend.py",
                    run_dir,
                    "--backend-id",
                    "openai-compatible-api",
                ],
                env=env,
                text=True,
                capture_output=True,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            deck = read_json(run_dir / "deck_manifest.json")
            self.assertEqual("provider/imagine-image-v2", deck["image_backend"]["model"])
            self.assertEqual(str(config_home), deck["image_backend"]["runtime_home"])
            request = read_json(run_dir / "pages/page_002/page_request.json")
            self.assertEqual("provider/imagine-image-v2", request["image_backend"]["model"])

    def test_prepare_help_accepts_explicit_openai_compatible_backend(self):
        result = run_cli("prepare", "--help")
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("openai-compatible-api", result.stdout)

    def test_builtin_image_backend_rejects_fixed_contract_overrides(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = make_minimal_run(tmp)
            result = run_cli(
                "run",
                "backend",
                run_dir,
                "--mode",
                "builtin-imagegen",
                "--input-context-policy",
                "skip-view-image",
            )
            self.assertNotEqual(0, result.returncode)
            self.assertIn("cannot override the fixed builtin-imagegen contract", result.stderr)

    def test_all_pending_pages_are_dispatchable(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = make_minimal_run(tmp)
            status = subprocess.run(
                [sys.executable, RUNTIME_DIR / "page_job_status.py", run_dir, "--json"],
                text=True,
                capture_output=True,
            )
            self.assertEqual(0, status.returncode, status.stderr)
            payload = json.loads(status.stdout)
            self.assertEqual(["page_001", "page_002"], payload["dispatchable_pages"])

    def test_record_page_result_does_not_store_qa_note_or_known_limits(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = make_minimal_run(tmp)
            jobs = read_json(run_dir / "page_jobs.json")
            page_2 = jobs["pages"][1]
            page_2["status"] = "dispatched"
            page_2["dispatch"] = {"agent_id": "worker-1"}
            write_json(run_dir / "page_jobs.json", jobs)

            page_dir = run_dir / "pages/page_002"
            write_page_outputs(page_dir, "Worker Page")

            result = subprocess.run(
                [
                    sys.executable,
                    RUNTIME_DIR / "record_page_result.py",
                    run_dir,
                    "--page",
                    "page_002",
                    "--agent-id",
                    "worker-1",
                ],
                text=True,
                capture_output=True,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            jobs = read_json(run_dir / "page_jobs.json")
            result_payload = jobs["pages"][1]["result"]
            self.assertEqual("dispatched-worker", result_payload["record_mode"])
            self.assertNotIn("qa_note", result_payload)
            self.assertNotIn("known_limits", result_payload)

    def test_record_page_result_rejects_manifest_without_positioned_boxes(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = make_minimal_run(tmp)
            jobs = read_json(run_dir / "page_jobs.json")
            page_2 = jobs["pages"][1]
            page_2["status"] = "dispatched"
            page_2["dispatch"] = {"agent_id": "worker-1"}
            write_json(run_dir / "page_jobs.json", jobs)

            page_dir = run_dir / "pages/page_002"
            manifest = valid_page_manifest("Missing Box")
            del manifest["text_boxes"][0]["box_px"]
            write_page_outputs(page_dir, manifest=manifest)

            result = subprocess.run(
                [
                    sys.executable,
                    RUNTIME_DIR / "record_page_result.py",
                    run_dir,
                    "--page",
                    "page_002",
                    "--agent-id",
                    "worker-1",
                ],
                text=True,
                capture_output=True,
            )
            combined_output = result.stdout + result.stderr
            self.assertNotEqual(0, result.returncode)
            self.assertIn("Page manifest contract validation failed", combined_output)
            self.assertIn("text_boxes[0].box_px", combined_output)

    def test_record_rejects_failed_validation_then_accepts_fixed_page(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = make_minimal_run(tmp)
            jobs = read_json(run_dir / "page_jobs.json")
            page_2 = jobs["pages"][1]
            page_2["status"] = "dispatched"
            page_2["dispatch"] = {"agent_id": "worker-1"}
            write_json(run_dir / "page_jobs.json", jobs)

            page_dir = run_dir / "pages/page_002"
            write_page_outputs(page_dir, "Refresh Page", validation_passed=False)

            first = subprocess.run(
                [
                    sys.executable,
                    RUNTIME_DIR / "record_page_result.py",
                    run_dir,
                    "--page",
                    "page_002",
                    "--agent-id",
                    "worker-1",
                ],
                text=True,
                capture_output=True,
            )
            self.assertNotEqual(0, first.returncode)
            self.assertIn("passed", first.stdout + first.stderr)
            self.assertIn("run reset", first.stdout + first.stderr)
            jobs = read_json(run_dir / "page_jobs.json")
            self.assertEqual("dispatched", jobs["pages"][1]["status"])

            write_json(page_dir / "validation.json", {"passed": True})
            second = subprocess.run(
                [
                    sys.executable,
                    RUNTIME_DIR / "record_page_result.py",
                    run_dir,
                    "--page",
                    "page_002",
                    "--agent-id",
                    "worker-1",
                ],
                text=True,
                capture_output=True,
            )
            self.assertEqual(0, second.returncode, second.stderr)
            jobs = read_json(run_dir / "page_jobs.json")
            self.assertEqual("recorded", jobs["pages"][1]["status"])
            self.assertIs(jobs["pages"][1]["result"]["validation_passed"], True)

    def test_run_reset_returns_page_to_pending_for_redispatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = make_minimal_run(tmp)
            jobs = read_json(run_dir / "page_jobs.json")
            page_2 = jobs["pages"][1]
            page_2["status"] = "dispatched"
            page_2["dispatch"] = {"agent_id": "worker-1"}
            write_json(run_dir / "page_jobs.json", jobs)

            reset_active = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "image2ppt.cli",
                    "run",
                    "reset",
                    run_dir,
                    "--page",
                    "page_002",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            self.assertNotEqual(0, reset_active.returncode)
            self.assertIn("Do not reset active workers", reset_active.stdout + reset_active.stderr)

            reset_wrong_agent = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "image2ppt.cli",
                    "run",
                    "reset",
                    run_dir,
                    "--page",
                    "page_002",
                    "--agent-id",
                    "worker-2",
                    "--confirm-lost",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            self.assertNotEqual(0, reset_wrong_agent.returncode)
            self.assertIn("Agent id mismatch", reset_wrong_agent.stdout + reset_wrong_agent.stderr)

            reset = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "image2ppt.cli",
                    "run",
                    "reset",
                    run_dir,
                    "--page",
                    "page_002",
                    "--agent-id",
                    "worker-1",
                    "--confirm-lost",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            self.assertEqual(0, reset.returncode, reset.stderr)
            jobs = read_json(run_dir / "page_jobs.json")
            self.assertEqual("pending", jobs["pages"][1]["status"])
            self.assertIsNone(jobs["pages"][1]["dispatch"])
            self.assertIsNone(jobs["pages"][1]["result"])

            reset_pending = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "image2ppt.cli",
                    "run",
                    "reset",
                    run_dir,
                    "--page",
                    "page_002",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            self.assertNotEqual(0, reset_pending.returncode)
            self.assertIn("cannot be reset", reset_pending.stdout + reset_pending.stderr)

    def test_page_build_and_validate_commands(self):
        with tempfile.TemporaryDirectory() as tmp:
            page_dir = Path(tmp) / "pages/page_001"
            page_dir.mkdir(parents=True)
            write_json(page_dir / "manifest.json", valid_page_manifest("Page Build"))

            build = subprocess.run(
                [sys.executable, "-m", "image2ppt.cli", "page", "build", str(page_dir)],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            self.assertEqual(0, build.returncode, build.stderr)
            self.assertTrue((page_dir / "page.pptx").exists())
            self.assertTrue((page_dir / "preview.png").exists())

            validate = subprocess.run(
                [sys.executable, "-m", "image2ppt.cli", "page", "validate", str(page_dir)],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            self.assertEqual(0, validate.returncode, validate.stdout + validate.stderr)

    def test_finalize_rebuilds_final_deck_from_page_manifests(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = make_minimal_run(tmp)
            write_json(run_dir / "notes_manifest.json", {"notes": []})
            deck = read_json(run_dir / "deck_manifest.json")
            deck["slide"] = {"width": 13.333, "height": 7.5}
            deck["page_count"] = 2
            deck["notes_manifest"] = "notes_manifest.json"
            deck["output"] = "final/test_edited.pptx"
            for index, page in enumerate(deck["pages"], start=1):
                page["manifest"] = f"pages/page_{index:03d}/manifest.json"
                page["validation"] = f"pages/page_{index:03d}/validation.json"
            write_json(run_dir / "deck_manifest.json", deck)

            jobs = read_json(run_dir / "page_jobs.json")
            for index, page in enumerate(jobs["pages"], start=1):
                page_dir = run_dir / f"pages/page_{index:03d}"
                write_json(
                    page_dir / "manifest.json",
                    {
                        "schema_version": 1,
                        "source": {"width_px": 1600, "height_px": 900},
                        "slide": {"width": 13.333, "height": 7.5},
                        "content_box": {"left": 0, "top": 0, "width": 13.333, "height": 7.5},
                        "text_boxes": [
                            {
                                "text": f"Manifest Page {index}",
                                "box_px": [100, 100, 500, 80],
                                "font_size": 24,
                                "color": "#111111",
                            }
                        ],
                        "shapes": [],
                        "images": [],
                        "visual_inventory": [],
                        "background_strategy": {"type": "native", "color": "#ffffff"},
                        "quality_checks": {
                            "font_size_calibrated": True,
                            "visual_inventory_matched": True,
                            "background_strategy_checked": True,
                            "shape_corner_geometry_checked": True,
                        },
                    },
                )
                write_json(page_dir / "imagegen-jobs.json", {"schema_version": 1, "jobs": []})
                (page_dir / "page.pptx").write_text("not a pptx", encoding="utf-8")
                (page_dir / "preview.png").write_text("x", encoding="utf-8")
                (page_dir / "split_assets_contact.png").write_text("x", encoding="utf-8")
                write_json(page_dir / "validation.json", {"passed": True})
                write_json(
                    page_dir / "page_result.json",
                    {
                        "page_manifest": "manifest.json",
                        "imagegen_jobs": "imagegen-jobs.json",
                        "page_pptx": "page.pptx",
                        "preview": "preview.png",
                        "contact_sheet": "split_assets_contact.png",
                        "validation": "validation.json",
                        "page_result": "page_result.json",
                    },
                )
                page["status"] = "recorded"
                page["result"] = {"validation_passed": True}
            write_json(run_dir / "page_jobs.json", jobs)

            result = subprocess.run(
                [sys.executable, "-m", "image2ppt.cli", "run", "finalize", run_dir],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            final_pptx = run_dir / "final/test_edited.pptx"
            self.assertTrue(final_pptx.exists())
            with zipfile.ZipFile(final_pptx) as z:
                slide_text = z.read("ppt/slides/slide1.xml").decode("utf-8") + z.read("ppt/slides/slide2.xml").decode("utf-8")
            self.assertIn("Manifest Page 1", slide_text)
            self.assertIn("Manifest Page 2", slide_text)

    def test_finalize_rejects_recorded_manifest_without_positioned_boxes(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = make_minimal_run(tmp)
            write_json(run_dir / "notes_manifest.json", {"notes": []})
            deck = read_json(run_dir / "deck_manifest.json")
            deck["slide"] = {"width": 13.333, "height": 7.5}
            deck["page_count"] = 2
            deck["notes_manifest"] = "notes_manifest.json"
            deck["output"] = "final/test_edited.pptx"
            for index, page in enumerate(deck["pages"], start=1):
                page["manifest"] = f"pages/page_{index:03d}/manifest.json"
                page["validation"] = f"pages/page_{index:03d}/validation.json"
            write_json(run_dir / "deck_manifest.json", deck)

            jobs = read_json(run_dir / "page_jobs.json")
            for index, page in enumerate(jobs["pages"], start=1):
                page_dir = run_dir / f"pages/page_{index:03d}"
                manifest = valid_page_manifest(f"Manifest Page {index}")
                if index == 2:
                    del manifest["text_boxes"][0]["box_px"]
                write_json(page_dir / "manifest.json", manifest)
                write_json(page_dir / "validation.json", {"passed": True})
                page["status"] = "recorded"
                page["result"] = {"validation_passed": True}
            write_json(run_dir / "page_jobs.json", jobs)

            result = subprocess.run(
                [sys.executable, "-m", "image2ppt.cli", "run", "finalize", run_dir],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            combined_output = result.stdout + result.stderr
            self.assertNotEqual(0, result.returncode)
            self.assertIn("page_contract_violations", combined_output)
            self.assertIn("text_boxes[0].box_px", combined_output)

    def test_image_import_records_generated_image(self):
        with tempfile.TemporaryDirectory() as tmp:
            page_dir = Path(tmp) / "page_001"
            page_dir.mkdir()
            write_json(page_dir / "imagegen-jobs.json", {"schema_version": 1, "jobs": []})
            write_json(
                page_dir / "page_request.json",
                {
                    "image_backend": {
                        "backend_id": "builtin-imagegen",
                        "fallback_policy": {
                            "on": [
                                "tool-unavailable",
                                "tool-error",
                                "input-unreadable",
                                "no-valid-local-output",
                            ]
                        },
                    }
                },
            )
            source = Path(tmp) / "generated.png"
            Image.new("RGBA", (12, 12), (255, 0, 0, 255)).save(source)
            result = run_cli(
                "image",
                "import",
                page_dir,
                "--job-id",
                "job-1",
                "--source-image",
                source,
                "--dest",
                "assets/generated.png",
                "--role",
                "asset",
                "--backend",
                "codex-oauth",
                "--fallback-reason",
                "tool-error",
            )
            self.assertEqual(0, result.returncode, result.stderr)
            copied = page_dir / "assets/generated.png"
            self.assertTrue(copied.exists())
            jobs = read_json(page_dir / "imagegen-jobs.json")
            self.assertEqual("recorded", jobs["jobs"][0]["status"])
            self.assertEqual("assets/generated.png", jobs["jobs"][0]["output"])
            self.assertEqual("codex-oauth", jobs["jobs"][0]["backend"])
            self.assertEqual("tool-error", jobs["jobs"][0]["fallback_reason"])

            builtin_result = run_cli(
                "image",
                "import",
                page_dir,
                "--job-id",
                "job-2",
                "--source-image",
                source,
                "--dest",
                "assets/builtin.png",
                "--backend",
                "builtin-imagegen",
            )
            self.assertEqual(0, builtin_result.returncode, builtin_result.stderr)
            jobs = read_json(page_dir / "imagegen-jobs.json")
            self.assertEqual("builtin-imagegen", jobs["jobs"][1]["backend"])
            self.assertIsNone(jobs["jobs"][1]["fallback_reason"])

    def test_image_import_rejects_unreadable_output_and_invalid_provenance(self):
        with tempfile.TemporaryDirectory() as tmp:
            page_dir = Path(tmp) / "page_001"
            page_dir.mkdir()
            write_json(page_dir / "imagegen-jobs.json", {"schema_version": 1, "jobs": []})
            write_json(
                page_dir / "page_request.json",
                {
                    "image_backend": {
                        "backend_id": "builtin-imagegen",
                        "fallback_policy": {"on": ["tool-error"]},
                    }
                },
            )
            unreadable = Path(tmp) / "not-an-image.png"
            unreadable.write_text("not an image", encoding="utf-8")
            unreadable_result = run_cli(
                "image",
                "import",
                page_dir,
                "--job-id",
                "bad-image",
                "--source-image",
                unreadable,
                "--dest",
                "assets/bad.png",
                "--backend",
                "builtin-imagegen",
            )
            self.assertNotEqual(0, unreadable_result.returncode)
            self.assertIn("Generated image is unreadable", unreadable_result.stderr)

            source = Path(tmp) / "generated.png"
            Image.new("RGB", (12, 12), "red").save(source)
            inconsistent_result = run_cli(
                "image",
                "import",
                page_dir,
                "--job-id",
                "bad-provenance",
                "--source-image",
                source,
                "--dest",
                "assets/generated.png",
                "--backend",
                "builtin-imagegen",
                "--fallback-reason",
                "tool-error",
            )
            self.assertNotEqual(0, inconsistent_result.returncode)
            self.assertIn("--fallback-reason requires --backend", inconsistent_result.stderr)
            self.assertFalse((page_dir / "assets/generated.png").exists())

            invalid_pairs = [
                ("builtin-imagegen", "unknown"),
                ("image2ppt-image-cli", "builtin-imagegen"),
                ("image2ppt-image-cli", "unknown"),
                ("openai-compatible-api", "builtin-imagegen"),
                ("openai-compatible-api", "codex-oauth"),
                ("openai-compatible-api", "unknown"),
                ("unsupported-backend", "unknown"),
            ]
            for index, (contract_backend, actual_backend) in enumerate(invalid_pairs):
                with self.subTest(contract_backend=contract_backend, actual_backend=actual_backend):
                    contract = {"backend_id": contract_backend}
                    if contract_backend == "builtin-imagegen":
                        contract["fallback_policy"] = {"on": ["tool-error"]}
                    write_json(page_dir / "page_request.json", {"image_backend": contract})
                    result = run_cli(
                        "image",
                        "import",
                        page_dir,
                        "--job-id",
                        f"invalid-{index}",
                        "--source-image",
                        source,
                        "--dest",
                        f"assets/invalid-{index}.png",
                        "--backend",
                        actual_backend,
                    )
                    self.assertNotEqual(0, result.returncode)

            allowed_pairs = [
                ("image2ppt-image-cli", "codex-oauth"),
                ("image2ppt-image-cli", "openai-compatible-api"),
                ("openai-compatible-api", "openai-compatible-api"),
            ]
            for index, (contract_backend, actual_backend) in enumerate(allowed_pairs):
                with self.subTest(contract_backend=contract_backend, actual_backend=actual_backend):
                    write_json(
                        page_dir / "page_request.json",
                        {"image_backend": {"backend_id": contract_backend}},
                    )
                    result = run_cli(
                        "image",
                        "import",
                        page_dir,
                        "--job-id",
                        f"allowed-{index}",
                        "--source-image",
                        source,
                        "--dest",
                        f"assets/allowed-{index}.png",
                        "--backend",
                        actual_backend,
                    )
                    self.assertEqual(0, result.returncode, result.stderr)


if __name__ == "__main__":
    unittest.main()
