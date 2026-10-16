import contextlib
import importlib.util
import io
import json
import tempfile
import unittest
import urllib.parse
from pathlib import Path
from unittest.mock import MagicMock, patch


SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "configure_credentials.py"
spec = importlib.util.spec_from_file_location("springer_credentials", SCRIPT)
config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(config)


class SpringerServicesTest(unittest.TestCase):
    def test_cli_stores_services_independently_without_echoing_keys(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(config, "CREDENTIALS_FILE", Path(tmp) / "credentials.json"):
            for service in (None, "metadata", "openaccess", "fulltext"):
                argv = ["set", "springer_nature", "--stdin"] + (["--service", service] if service else [])
                args = config.build_parser().parse_args(argv)
                secret = f"{service or 'legacy'}-secret-value"
                output = io.StringIO()
                with patch.object(config.sys, "stdin", io.StringIO(secret + "\n")), contextlib.redirect_stdout(output):
                    self.assertEqual(config.cmd_set(args), 0)
                self.assertNotIn(secret, output.getvalue())
            saved = config._load(config.CREDENTIALS_FILE)["springer_nature"]
            self.assertEqual(saved, {
                "api_key": "legacy-secret-value", "metadata_api_key": "metadata-secret-value",
                "openaccess_api_key": "openaccess-secret-value", "fulltext_api_key": "fulltext-secret-value",
            })
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                config.cmd_show(config.build_parser().parse_args(["show"]))
            for secret in saved.values():
                self.assertNotIn(secret, output.getvalue())

    def test_validation_uses_only_the_selected_service_grant(self):
        stored = {"api_key": "legacy-secret", "metadata_api_key": "meta-secret",
                  "openaccess_api_key": "oa-secret", "fulltext_api_key": "tdm-secret/metric"}
        for service, field, endpoint, accept in (
            ("metadata", "metadata_api_key", "/meta/v2/json", "application/json"),
            ("openaccess", "openaccess_api_key", "/openaccess/jats", "application/xml"),
            ("fulltext", "fulltext_api_key", "/xmldata/jats", "application/xml"),
        ):
            with self.subTest(service=service):
                response = MagicMock()
                response.__enter__.return_value.status = 200
                args = config.build_parser().parse_args(["validate", "springer_nature", "--service", service])
                output = io.StringIO()
                with patch.object(config, "_load", return_value={"springer_nature": stored}), patch.object(
                    config.urllib.request, "urlopen", return_value=response
                ) as fetch, contextlib.redirect_stdout(output):
                    self.assertEqual(config.cmd_validate(args), 0)
                request = fetch.call_args.args[0]
                url = urllib.parse.urlsplit(request.full_url)
                self.assertEqual(url.netloc, "api.springernature.com")
                self.assertEqual(url.path, endpoint)
                self.assertEqual(urllib.parse.parse_qs(url.query)["api_key"], [stored[field]])
                self.assertEqual(request.get_header("Accept"), accept)
                result = json.loads(output.getvalue())
                self.assertTrue(result["ok"])
                self.assertEqual(result["http_status"], 200)
                for secret in stored.values():
                    self.assertNotIn(secret, output.getvalue())

    def test_legacy_credentials_only_validate_fulltext(self):
        self.assertEqual(config._service_values({"api_key": "legacy"}, "fulltext"), {"api_key": "legacy"})
        for service in ("metadata", "openaccess"):
            self.assertIsNone(config._service_values({"api_key": "legacy"}, service)["api_key"])
        request = config._validation_request("springer_nature", {"api_key": "legacy"})
        self.assertEqual(urllib.parse.urlsplit(request.full_url).path, "/xmldata/jats")

    def test_meta_only_configuration_does_not_validate_fulltext(self):
        args = config.build_parser().parse_args(["validate", "springer_nature"])
        output = io.StringIO()
        with patch.object(config, "_load", return_value={"springer_nature": {"metadata_api_key": "meta-secret"}}), patch.object(
            config.urllib.request, "urlopen"
        ) as fetch, contextlib.redirect_stdout(output):
            self.assertEqual(config.cmd_validate(args), 2)
        fetch.assert_not_called()
        self.assertEqual(json.loads(output.getvalue())["status"], "credentials_missing")

    def test_service_option_is_rejected_for_other_publishers(self):
        for command in ("set", "validate"):
            args = config.build_parser().parse_args([command, "elsevier", "--service", "metadata"])
            with self.assertRaisesRegex(SystemExit, "only supported"):
                args.func(args)


if __name__ == "__main__":
    unittest.main()
