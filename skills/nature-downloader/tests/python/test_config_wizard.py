import importlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
SCRIPT = ROOT / "scripts" / "configure_school.py"


class ConfigWizardTest(unittest.TestCase):
    def test_start_asks_for_library_resource_url_first(self):
        sys.path.insert(0, str(SRC))
        try:
            wizard = importlib.import_module("wizard")
            wizard = importlib.reload(wizard)
            prompt = wizard.Wizard().start()
        finally:
            if str(SRC) in sys.path:
                sys.path.remove(str(SRC))

        self.assertIn("图书馆", prompt)
        self.assertIn("资源", prompt)
        self.assertIn("链接", prompt)
        self.assertNotIn("请问你所在的学校或单位是", prompt)

    def test_infer_generic_resource_portal_from_resource_url(self):
        sys.path.insert(0, str(SRC))
        try:
            wizard = importlib.import_module("wizard")
            wizard = importlib.reload(wizard)
            result = wizard.infer_access_from_url("https://portal.metaersp.example/personal")
        finally:
            if str(SRC) in sys.path:
                sys.path.remove(str(SRC))

        self.assertEqual(result["entry_type"], "resource_portal")
        self.assertEqual(result["auth_type"], "cas")
        self.assertEqual(result["sso_domain"], "portal.metaersp.example")
        self.assertEqual(result["resource_entry"], "https://portal.metaersp.example/personal")
        self.assertEqual(result["institution_hint"], "portal")

    def test_infer_cas_login_service_callback_from_resource_url(self):
        sys.path.insert(0, str(SRC))
        try:
            wizard = importlib.import_module("wizard")
            wizard = importlib.reload(wizard)
            result = wizard.infer_access_from_url(
                "https://login.university.example/authserver/login?service=https%3A%2F%2Fresources.university.example%2Fservice%2Fcampus%2Fcallback"
            )
        finally:
            if str(SRC) in sys.path:
                sys.path.remove(str(SRC))

        self.assertEqual(result["entry_type"], "cas_login")
        self.assertEqual(result["auth_type"], "cas")
        self.assertEqual(result["sso_domain"], "login.university.example")
        self.assertEqual(result["service_host"], "resources.university.example")
        self.assertEqual(result["institution_hint"], "campus")

    def test_resource_url_flow_can_save_schema_valid_config(self):
        with tempfile.TemporaryDirectory() as tmp:
            old_env = os.environ.copy()
            os.environ["LIT_DL_CONFIG_DIR"] = tmp
            sys.path.insert(0, str(SRC))
            try:
                config = importlib.import_module("config")
                wizard = importlib.import_module("wizard")
                config = importlib.reload(config)
                wizard = importlib.reload(wizard)
                w = wizard.Wizard()
                w.handle_step1("https://portal.metaersp.example/personal")
                result = w.handle_step7("1")

                self.assertEqual(result["next"], "done")
                saved = Path(result["data"]["path"])
                data = json.loads(saved.read_text(encoding="utf-8"))
                self.assertEqual(data["school"]["source"], "resource_url")
                self.assertEqual(data["auth"]["sso_domain"], "portal.metaersp.example")
                self.assertEqual(data["discovery"]["resource_portal_url"], "https://portal.metaersp.example/personal")
            finally:
                if str(SRC) in sys.path:
                    sys.path.remove(str(SRC))
                os.environ.clear()
                os.environ.update(old_env)

    def test_distributed_skill_has_no_institution_presets(self):
        sys.path.insert(0, str(SRC))
        try:
            schools_loader = importlib.import_module("schools_loader")
            schools_loader = importlib.reload(schools_loader)
            presets = schools_loader.load_schools()
        finally:
            if str(SRC) in sys.path:
                sys.path.remove(str(SRC))

        self.assertEqual(presets, [])
        self.assertIsNone(schools_loader.match_school("Example University"))

    def test_cli_show_reports_missing_config(self):
        with tempfile.TemporaryDirectory() as tmp:
            env = os.environ.copy()
            env["LIT_DL_CONFIG_DIR"] = tmp
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "show"],
                cwd=ROOT,
                env=env,
                text=True,
                capture_output=True,
            )

        self.assertEqual(result.returncode, 2)
        self.assertIn("尚未配置", result.stdout)

    def test_cli_url_configures_from_resource_entry(self):
        with tempfile.TemporaryDirectory() as tmp:
            env = os.environ.copy()
            env["LIT_DL_CONFIG_DIR"] = tmp
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "url", "https://portal.metaersp.example/personal"],
                cwd=ROOT,
                env=env,
                text=True,
                capture_output=True,
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertTrue(data["ok"])
        self.assertEqual(data["entry_type"], "resource_portal")
        self.assertEqual(data["sso_domain"], "portal.metaersp.example")

    def test_cli_infer_does_not_save_config(self):
        with tempfile.TemporaryDirectory() as tmp:
            env = os.environ.copy()
            env["LIT_DL_CONFIG_DIR"] = tmp
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "infer", "https://portal.metaersp.example/personal"],
                cwd=ROOT,
                env=env,
                text=True,
                capture_output=True,
            )

            self.assertFalse((Path(tmp) / "school.json").exists())

        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual(data["entry_type"], "resource_portal")

    def test_cli_cnki_url_updates_existing_config(self):
        with tempfile.TemporaryDirectory() as tmp:
            env = os.environ.copy()
            env["LIT_DL_CONFIG_DIR"] = tmp
            configured = subprocess.run(
                [sys.executable, str(SCRIPT), "url", "https://portal.metaersp.example/personal"],
                cwd=ROOT,
                env=env,
                text=True,
                capture_output=True,
            )
            self.assertEqual(configured.returncode, 0, configured.stderr)

            result = subprocess.run(
                [sys.executable, str(SCRIPT), "cnki-url", "https://kns.cnki.net/kns8s/defaultresult/index"],
                cwd=ROOT,
                env=env,
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            data = json.loads(result.stdout)
            self.assertTrue(data["ok"])
            saved = json.loads((Path(tmp) / "school.json").read_text(encoding="utf-8"))
            self.assertEqual(saved["discovery"]["cnki_url"], "https://kns.cnki.net/kns8s/defaultresult/index")


if __name__ == "__main__":
    unittest.main()
