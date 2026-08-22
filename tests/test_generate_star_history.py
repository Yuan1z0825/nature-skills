import datetime as dt
import importlib.util
import pathlib
import tempfile
import unittest
from unittest import mock
from types import SimpleNamespace


SCRIPT = pathlib.Path(__file__).parents[1] / "scripts" / "generate-star-history.py"
SPEC = importlib.util.spec_from_file_location("generate_star_history", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class StarHistoryTests(unittest.TestCase):
    def test_empty_repository_has_no_daily_points(self):
        self.assertEqual(MODULE.build_daily_points([], 0), [])

    def test_missing_timestamp_does_not_produce_a_chart(self):
        items = [{"starred_at": None}, {"login": "example"}]
        with self.assertRaises(MODULE.StarHistoryUnavailable):
            MODULE.build_daily_points(items, 2)

    def test_invalid_timestamp_does_not_produce_a_chart(self):
        items = [{"starred_at": "not-a-date"}]
        with self.assertRaises(MODULE.StarHistoryUnavailable):
            MODULE.build_daily_points(items, 1)

    def test_valid_timestamps_are_sorted_and_accumulated(self):
        items = [
            {"starred_at": "2026-08-03T10:00:00Z"},
            {"starred_at": "2026-08-01T10:00:00Z"},
            {"starred_at": "2026-08-01T11:00:00Z"},
        ]
        self.assertEqual(
            MODULE.build_daily_points(items, 3),
            [
                (dt.date(2026, 8, 1), 2),
                (dt.date(2026, 8, 2), 2),
                (dt.date(2026, 8, 3), 3),
            ],
        )

    def test_valid_records_allow_star_count_changes_during_fetch(self):
        items = [{"starred_at": "2026-08-01T10:00:00Z"}]
        self.assertEqual(
            MODULE.build_daily_points(items, 2),
            [(dt.date(2026, 8, 1), 1)],
        )

    def test_empty_svg_is_valid_for_zero_stars(self):
        svg = MODULE.generate_empty_svg("zpf2234/nature-skills")
        self.assertIn("zpf2234/nature-skills", svg)
        self.assertIn("No stars yet", svg)
        self.assertIn("<svg", svg)

    def test_zero_star_fetch_skips_stargazer_request(self):
        with mock.patch.object(MODULE, "github_json", return_value={"stargazers_count": 0}) as request:
            self.assertEqual(MODULE.fetch_stargazers("owner/repo", None, 1, 0), (0, []))
        request.assert_called_once_with("https://api.github.com/repos/owner/repo", None, 0)

    def test_unusable_api_response_keeps_existing_chart(self):
        with tempfile.TemporaryDirectory() as directory:
            output = pathlib.Path(directory) / "star-history.svg"
            output.write_text("existing chart", encoding="utf-8")
            args = SimpleNamespace(
                repo="owner/repo",
                token=None,
                workers=1,
                retries=0,
                output=str(output),
                cache_bust_readme=[],
            )
            with mock.patch.object(MODULE, "parse_args", return_value=args), mock.patch.object(
                MODULE, "fetch_stargazers", return_value=(1, [{"login": "example"}])
            ):
                self.assertEqual(MODULE.main(), 0)
            self.assertEqual(output.read_text(encoding="utf-8"), "existing chart")

    def test_small_chart_has_integer_y_ticks(self):
        self.assertEqual(MODULE.nice_y_ticks(1), [0, 1])


if __name__ == "__main__":
    unittest.main()
