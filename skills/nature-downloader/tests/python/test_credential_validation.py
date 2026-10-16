import contextlib
import importlib.util
import io
import json
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import MagicMock, patch


SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "configure_credentials.py"
spec = importlib.util.spec_from_file_location("credential_validation", SCRIPT)
config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(config)


class CredentialValidationTest(unittest.TestCase):
    def validate(self, provider, status=None, error=None, credentials=None):
        response = MagicMock()
        response.__enter__.return_value.status = status
        output = io.StringIO()
        args = config.build_parser().parse_args(["validate", provider])
        stored = {provider: {"api_key": "test-secret"}} if credentials is None else credentials
        with patch.object(config, "_load", return_value=stored), patch.object(
            config.urllib.request, "urlopen", return_value=response, side_effect=error
        ) as fetch, contextlib.redirect_stdout(output):
            code = config.cmd_validate(args)
        return code, json.loads(output.getvalue()), fetch

    def test_only_2xx_responses_succeed_for_every_provider(self):
        for provider in config.PROVIDERS:
            for status in (200, 204, 299, 300, 401, 403, 404, 429, 500, 503):
                with self.subTest(provider=provider, status=status):
                    code, result, _ = self.validate(provider, status=status)
                    self.assertEqual(result["ok"], 200 <= status < 300)
                    self.assertEqual(code, 0 if result["ok"] else 1)
                    self.assertEqual(result["http_status"], status)

    def test_http_errors_remain_distinct_from_invalid_credentials(self):
        for status, expected in ((401, "credentials_invalid"), (403, "credentials_invalid"),
                                 (404, "validation_failed"), (429, "rate_limited"),
                                 (500, "validation_failed")):
            with self.subTest(status=status):
                error = urllib.error.HTTPError("https://example.test/?api_key=test-secret", status, "error", {}, None)
                code, result, _ = self.validate("springer_nature", error=error)
                self.assertEqual(code, 1)
                self.assertFalse(result["ok"])
                self.assertEqual(result["status"], expected)
                self.assertEqual(result["http_status"], status)
                self.assertNotIn("test-secret", json.dumps(result))

    def test_network_errors_do_not_leak_key_bearing_urls(self):
        for error in (urllib.error.URLError("https://example.test/?api_key=test-secret"), TimeoutError("test-secret")):
            code, result, _ = self.validate("springer_nature", error=error)
            self.assertEqual(code, 1)
            self.assertEqual(result["status"], "validation_failed")
            self.assertNotIn("test-secret", json.dumps(result))

    def test_missing_credentials_do_not_send_requests(self):
        code, result, fetch = self.validate("springer_nature", credentials={})
        self.assertEqual(code, 2)
        self.assertEqual(result["status"], "credentials_missing")
        fetch.assert_not_called()


if __name__ == "__main__":
    unittest.main()
