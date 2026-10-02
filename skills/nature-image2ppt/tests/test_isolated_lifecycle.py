from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageDraw

from support import SKILL_ROOT, complete_visual_review_evidence, filled_arrow_manifest, write_json


class IsolatedLifecycleTests(unittest.TestCase):
    def run_ok(self, command: list[str], *, env: dict[str, str], cwd: Path) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(command, env=env, cwd=cwd, text=True, capture_output=True, check=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    def test_full_lifecycle_from_isolated_skill_copy_without_external_command(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            isolated_parent = Path(tmp) / "isolated-skills"
            isolated = isolated_parent / "image2ppt"
            isolated.mkdir(parents=True)
            for directory in ("cli", "scripts", "prompts", "references", "schemas"):
                shutil.copytree(
                    SKILL_ROOT / directory,
                    isolated / directory,
                    dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
                )
            for name in ("SKILL.md", "requirements.txt"):
                shutil.copy2(SKILL_ROOT / name, isolated / name)

            old_skill_name = "-".join(("image", "to", "editable", "ppt", "skill"))
            other_skill_name = "-".join(("ppt", "to", "editable"))
            self.assertFalse((isolated_parent / old_skill_name).exists())
            self.assertFalse((isolated_parent / other_skill_name).exists())

            if sys.platform == "win32":
                windows_dir = Path(os.environ.get("SystemRoot", "C:/Windows"))
                clean_path = str(windows_dir / "System32" / "WindowsPowerShell" / "v1.0")
            else:
                # Keep only the declared system dependencies while excluding any
                # legacy Image2PPT command. Homebrew and bundled runtimes commonly
                # install LibreOffice/fontconfig outside /usr/bin on macOS.
                allowed_dirs = [path for path in ("/usr/bin", "/bin") if Path(path).is_dir()]
                for command in ("soffice", "libreoffice", "fc-match"):
                    resolved = shutil.which(command)
                    if resolved:
                        allowed_dirs.append(str(Path(resolved).resolve().parent))
                clean_path = os.pathsep.join(dict.fromkeys(allowed_dirs))
            external_command = "edit" + "ppt"
            self.assertIsNone(shutil.which(external_command, path=clean_path))
            env = os.environ.copy()
            env["PATH"] = clean_path
            env["CODEX_HOME"] = str(Path(tmp) / "empty-codex-home")
            env["IMAGE2PPT_CONFIG_HOME"] = str(Path(tmp) / "config")
            env.pop("PADDLE_OCR_TOKEN", None)
            env.pop("PYTHONPATH", None)

            cli = [sys.executable, str(isolated / "cli" / "image2ppt" / "cli.py")]
            doctor = self.run_ok([*cli, "doctor", "--json"], env=env, cwd=isolated)
            doctor_payload = json.loads(doctor.stdout)
            self.assertTrue(doctor_payload["ok"], doctor_payload)
            self.assertEqual(Path(doctor_payload["skill_root"]).resolve(), isolated.resolve())
            self.assertEqual(doctor_payload["ocr"]["selection"], "builtin-ink")

            source = Path(tmp) / "source.png"
            image = Image.new("RGB", (1280, 720), "white")
            draw = ImageDraw.Draw(image)
            for index in range(7):
                x = 120 + index * 120
                draw.ellipse([x, 220, x + 42, 262], outline="#2563EB", width=3)
            image.save(source)
            run = Path(tmp) / "run"
            self.run_ok(
                [*cli, "prepare", str(source), "--job-dir", str(run), "--image-backend", "image2ppt-image-cli"],
                env=env,
                cwd=isolated,
            )
            self.assertTrue((run / "pages/page_001/text_hints.json").is_file())
            next_before = self.run_ok([*cli, "run", "next", str(run), "--json"], env=env, cwd=isolated)
            self.assertEqual(json.loads(next_before.stdout)["stage"], "rebuild_page_locally")

            page = run / "pages" / "page_001"
            filled_arrow_manifest(page)
            prompt = page / "worker-prompt.md"
            self.run_ok(
                [
                    sys.executable,
                    str(isolated / "scripts" / "build_page_worker_prompt.py"),
                    str(run),
                    "--page",
                    "page_001",
                    "--out",
                    str(prompt),
                ],
                env=env,
                cwd=isolated,
            )
            self.assertIn(str(isolated / "cli/image2ppt/cli.py"), prompt.read_text(encoding="utf-8"))
            self.run_ok(
                [
                    *cli,
                    "run",
                    "dispatch",
                    str(run),
                    "--page",
                    "page_001",
                    "--agent-id",
                    "isolated-main",
                    "--prompt-file",
                    str(prompt),
                    "--local",
                ],
                env=env,
                cwd=isolated,
            )
            self.run_ok([*cli, "page", "build", str(page)], env=env, cwd=isolated)
            pending_page_qa = subprocess.run(
                [sys.executable, str(isolated / "scripts" / "run_image2ppt_qa.py"), str(page)],
                env=env,
                cwd=isolated,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(pending_page_qa.returncode, 2, pending_page_qa.stdout + pending_page_qa.stderr)
            page_evidence = page / "visual-review-evidence.json"
            complete_visual_review_evidence(
                page / "visual-review-evidence.template.json", page_evidence
            )
            self.run_ok(
                [
                    sys.executable,
                    str(isolated / "scripts" / "run_image2ppt_qa.py"),
                    str(page),
                    "--visual-review-status",
                    "reviewed",
                    "--visual-review-evidence",
                    str(page_evidence),
                    "--visual-review-notes",
                    "isolated fixture: source and render checked for arrow silhouette, direction, text, and bounds",
                ],
                env=env,
                cwd=isolated,
            )
            self.run_ok(
                [*cli, "page", "validate", str(page), "--report", "validation.json"],
                env=env,
                cwd=isolated,
            )
            self.run_ok([*cli, "page", "contact-sheet", str(page)], env=env, cwd=isolated)
            write_json(
                page / "page_result.json",
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
            self.run_ok(
                [*cli, "run", "record", str(run), "--page", "page_001", "--agent-id", "isolated-main"],
                env=env,
                cwd=isolated,
            )
            next_after = self.run_ok([*cli, "run", "next", str(run), "--json"], env=env, cwd=isolated)
            self.assertEqual(json.loads(next_after.stdout)["stage"], "finalize")
            self.run_ok([*cli, "run", "finalize", str(run)], env=env, cwd=isolated)
            pending_final_qa = subprocess.run(
                [sys.executable, str(isolated / "scripts" / "run_final_image2ppt_qa.py"), str(run)],
                env=env,
                cwd=isolated,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(pending_final_qa.returncode, 2, pending_final_qa.stdout + pending_final_qa.stderr)
            final_evidence = run / "final" / "visual-review-evidence.json"
            complete_visual_review_evidence(
                run / "final" / "visual-review-evidence.template.json", final_evidence
            )
            self.run_ok(
                [
                    sys.executable,
                    str(isolated / "scripts" / "run_final_image2ppt_qa.py"),
                    str(run),
                    "--visual-review-status",
                    "reviewed",
                    "--visual-review-evidence",
                    str(final_evidence),
                    "--visual-review-notes",
                    "isolated fixture: final render checked against the source for arrow, text, and page geometry",
                ],
                env=env,
                cwd=isolated,
            )
            jobs = json.loads((run / "page_jobs.json").read_text(encoding="utf-8"))
            deck = json.loads((run / "deck_manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(jobs["pages"][0]["status"], "accepted")
            self.assertTrue((run / deck["output"]).is_file())
            self.assertTrue(json.loads((run / "final/image2ppt_qa.json").read_text(encoding="utf-8"))["passed"])
            self.assertFalse((run / "image2ppt_jobs.json").exists())


if __name__ == "__main__":
    unittest.main()
