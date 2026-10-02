from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import yaml


ROOT = Path(__file__).resolve().parents[1]
CLI_DIR = ROOT / "cli"
sys.path.insert(0, str(CLI_DIR))

from image2ppt.runtime import runtime_env  # noqa: E402


class RuntimeConfigTests(unittest.TestCase):
    def test_update_restricts_existing_config_permissions(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            config = Path(directory) / "config.yaml"
            config.write_text("OPENAI_API_KEY: old-key\n", encoding="utf-8")
            if sys.platform != "win32":
                os.chmod(config, 0o644)

            runtime_env.write_config_file(config, {"OPENAI_API_KEY": "new-key"})

            self.assertEqual(
                runtime_env.read_config_file(config),
                {"OPENAI_API_KEY": "new-key"},
            )
            if sys.platform != "win32":
                self.assertEqual(config.stat().st_mode & 0o777, 0o600)

    def test_failed_serialization_preserves_existing_config(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            config = Path(directory) / "config.yaml"
            original = "OPENAI_API_KEY: existing-key\n"
            config.write_text(original, encoding="utf-8")

            with mock.patch.object(yaml, "safe_dump", side_effect=RuntimeError("write failed")):
                with self.assertRaisesRegex(RuntimeError, "write failed"):
                    runtime_env.write_config_file(config, {"OPENAI_API_KEY": "replacement-key"})

            self.assertEqual(config.read_text(encoding="utf-8"), original)
            self.assertEqual(list(config.parent.glob(f".{config.name}.*")), [])

    def test_failed_flush_or_replace_preserves_existing_config(self) -> None:
        for operation in ("fsync", "replace"):
            with self.subTest(operation=operation), tempfile.TemporaryDirectory() as directory:
                config = Path(directory) / "config.yaml"
                original = b"OPENAI_API_KEY: existing-key\n"
                config.write_bytes(original)

                with mock.patch.object(
                    runtime_env.os, operation, side_effect=OSError("disk error")
                ):
                    with self.assertRaisesRegex(OSError, "disk error"):
                        runtime_env.write_config_file(config, {"OPENAI_API_KEY": "new-key"})

                self.assertEqual(config.read_bytes(), original)
                self.assertEqual(list(config.parent.glob(f".{config.name}.*")), [])


if __name__ == "__main__":
    unittest.main()
