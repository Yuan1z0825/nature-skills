import json
import os
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "configure_credentials.py"


class ConfigureCredentialsTest(unittest.TestCase):
    def test_cli_stdin_saves_key_without_echoing_it(self):
        secret = "publisher-secret-12345678"
        with tempfile.TemporaryDirectory() as tmp:
            env = os.environ.copy()
            env["LIT_DL_CONFIG_DIR"] = tmp
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "set", "elsevier", "--stdin"],
                cwd=ROOT,
                env=env,
                input=secret + "\n",
                text=True,
                capture_output=True,
            )
            credentials_path = Path(tmp) / "credentials.json"
            saved = json.loads(credentials_path.read_text(encoding="utf-8"))
            mode = stat.S_IMODE(credentials_path.stat().st_mode)

        self.assertEqual(result.returncode, 0)
        self.assertNotIn(secret, result.stdout)
        self.assertNotIn(secret, result.stderr)
        self.assertEqual(saved["elsevier"]["api_key"], secret)
        self.assertEqual(mode, 0o600)


if __name__ == "__main__":
    unittest.main()
