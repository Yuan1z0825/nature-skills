from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNTIME_DIR = ROOT / "cli" / "image2ppt" / "runtime"
SCRIPT_DIR = ROOT / "scripts"


class ScriptInventoryTests(unittest.TestCase):
    def test_required_local_entrypoints_exist(self) -> None:
        required = {
            ROOT / "cli/image2ppt/cli.py",
            SCRIPT_DIR / "build_page_worker_prompt.py",
            SCRIPT_DIR / "run_image2ppt_qa.py",
            SCRIPT_DIR / "run_final_image2ppt_qa.py",
            SCRIPT_DIR / "visual_review_evidence.py",
            SCRIPT_DIR / "inspect_region_decomposition.py",
            SCRIPT_DIR / "inspect_arrow_atomicity.py",
            RUNTIME_DIR / "paddle_text_hints.py",
            RUNTIME_DIR / "deck_text_hints.py",
            RUNTIME_DIR / "build_pptx_from_manifest.py",
            RUNTIME_DIR / "validate_pptx.py",
            RUNTIME_DIR / "finalize_deck_run.py",
            ROOT / "schemas/page-manifest-v2.schema.json",
        }
        self.assertEqual([str(path) for path in sorted(required) if not path.is_file()], [])

    def test_doctor_is_the_only_runtime_preflight(self) -> None:
        self.assertFalse((SCRIPT_DIR / "check_runtime.py").exists())
        self.assertTrue((ROOT / "cli/image2ppt/runtime/runtime_env.py").is_file())

    def test_deprecated_parallel_entrypoints_are_absent(self) -> None:
        names = {
            "prepare_inputs.py",
            "run_page_experiment.py",
            "normalize_paddle_ocr.py",
            "assemble_image2ppt_plans.py",
            "package_image2ppt.py",
        }
        present = [path.name for root in (RUNTIME_DIR, SCRIPT_DIR) for path in root.glob("*.py") if path.name in names]
        self.assertEqual(present, [])

    def test_no_symlink_escapes_the_skill(self) -> None:
        escaped = []
        for path in ROOT.rglob("*"):
            if path.is_symlink():
                try:
                    path.resolve().relative_to(ROOT.resolve())
                except ValueError:
                    escaped.append(str(path))
        self.assertEqual(escaped, [])


if __name__ == "__main__":
    unittest.main()
