from __future__ import annotations

import hashlib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

# These behavior-bearing files are pinned to the reviewed migration/hardening baseline. Updating a
# hash is an explicit behavior change and must be accompanied by real conversion
# regression evidence, not only structural unit tests.
BASELINE_SHA256 = {
    "prompts/page-worker-base.md": "b60403e94c76205d7bd2baa9b7886d820ce178671bcb8ad3fa99d0152ccb48c7",
    "prompts/page-worker.md": "bfca72b1544c08df2093f57631408e70c2e40439339f98ba7fa1d21c02306ca8",
    "cli/image2ppt/runtime/_page_artifacts.py": "3c86c1a9adead2046a5a8cdde52d142b8a846ba1fb6b7f6d690fc178fe5ef76a",
    "cli/image2ppt/runtime/split_alpha_components.py": "68f0fb4e9483a99694476e46c06f17d6d47f5e4c24f62be9e41a0eab33af5ce4",
    "cli/image2ppt/runtime/build_pptx_from_manifest.py": "0d9c29e5ff8ffb98440d1123ac014ed6d19e36555e6ccf8ace57f86713d8b91b",
    "cli/image2ppt/runtime/deck_run_state.py": "bd6bb3da7a81d9b8ee262fc606d4e77d97946d8f3de05d247cca56dba33542e6",
    "cli/image2ppt/runtime/finalize_deck_run.py": "835fa3db0c4215c35e7cefca39c20b3879257cd07b5c93d545be230a8bc69da9",
    "cli/image2ppt/runtime/paddle_text_hints.py": "9dae5da054ca768f683c1aa61dc147dda57b475e6bab2cb1cdbcb5ee794788bf",
    "cli/image2ppt/runtime/page_job_status.py": "01e8effade4c3ab6719341c60490cb874f6c9d780e1fdbe00088696362d8703b",
    "cli/image2ppt/runtime/record_page_dispatch.py": "d91b45281c0eafa10801b1344f3c423712b5aeae0aea0231d2243003176f0522",
    "cli/image2ppt/runtime/reset_page_job.py": "81181eb9e5bb42cb973608795592d1a7c1dd04e5bd4ddd339bdc0864f080f42e",
    "cli/image2ppt/runtime/text_hints.py": "8c41aa98d03302dc0eabbc17bdbbd0c167fe0e0c2e94ba3827bdefc321b0a19e",
    "cli/image2ppt/runtime/validate_pptx.py": "f8e9f216e96ada58841120fd6bf5e8b087a306b347acf49f46c0828879b56d0a",
}


class MigrationParityTests(unittest.TestCase):
    def test_behavior_bearing_sources_match_the_migrated_baseline(self) -> None:
        mismatches = []
        for relative, expected in BASELINE_SHA256.items():
            path = ROOT / relative
            content = path.read_bytes().replace(b"\r\n", b"\n") if path.is_file() else None
            actual = hashlib.sha256(content).hexdigest() if content is not None else "missing"
            if actual != expected:
                mismatches.append(f"{relative}: expected {expected}, got {actual}")
        self.assertEqual([], mismatches)

    def test_prompt_keeps_base_then_profile_layering(self) -> None:
        base = (ROOT / "prompts/page-worker-base.md").read_text(encoding="utf-8")
        profile = (ROOT / "prompts/page-worker.md").read_text(encoding="utf-8")
        self.assertIn("Every non-text foreground visual object must be separated", base)
        self.assertIn("Do not invent an object-source strategy", base)
        self.assertIn("This addendum extends the complete local page-reconstructor prompt above", profile)
        self.assertIn("Replace only the base prompt's final page build/validate sequence", profile)


if __name__ == "__main__":
    unittest.main()
