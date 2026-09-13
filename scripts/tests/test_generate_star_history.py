from __future__ import annotations

import datetime as dt
import importlib.util
import unittest
from pathlib import Path
from unittest import mock


SCRIPT = Path(__file__).resolve().parents[1] / "generate-star-history.py"
SPEC = importlib.util.spec_from_file_location("generate_star_history", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def graphql_page(
    total: int,
    timestamps: list[str],
    *,
    has_next: bool,
    end_cursor: str | None,
) -> dict:
    return {
        "data": {
            "repository": {
                "stargazerCount": total,
                "stargazers": {
                    "edges": [{"starredAt": timestamp} for timestamp in timestamps],
                    "pageInfo": {
                        "hasNextPage": has_next,
                        "endCursor": end_cursor,
                    },
                },
            },
            "rateLimit": {
                "cost": 1,
                "remaining": 999,
                "resetAt": "2026-09-13T04:00:00Z",
            },
        }
    }


class StarHistoryFetchingTests(unittest.TestCase):
    def test_cursor_pagination_collects_all_pages_in_order(self) -> None:
        responses = [
            graphql_page(
                3,
                ["2026-01-01T00:00:00Z", "2026-01-02T00:00:00Z"],
                has_next=True,
                end_cursor="cursor-1",
            ),
            graphql_page(
                3,
                ["2026-01-03T00:00:00Z"],
                has_next=False,
                end_cursor="cursor-2",
            ),
        ]

        with mock.patch.object(MODULE, "github_graphql", side_effect=responses) as request:
            total, items = MODULE.fetch_stargazers("owner/repo", "token", 4, 5)

        self.assertEqual(total, 3)
        self.assertEqual(
            [item["starred_at"] for item in items],
            [
                "2026-01-01T00:00:00Z",
                "2026-01-02T00:00:00Z",
                "2026-01-03T00:00:00Z",
            ],
        )
        self.assertIsNone(request.call_args_list[0].args[1]["cursor"])
        self.assertEqual(request.call_args_list[1].args[1]["cursor"], "cursor-1")

    def test_cursor_pagination_has_no_400_page_ceiling(self) -> None:
        def response_for_cursor(query, variables, token, retries):
            del query, token, retries
            page = int(variables["cursor"] or 0)
            final_page = page == 400
            timestamps = ["2026-01-01T00:00:00Z"] * (1 if final_page else 100)
            return graphql_page(
                40_001,
                timestamps,
                has_next=not final_page,
                end_cursor=None if final_page else str(page + 1),
            )

        with mock.patch.object(
            MODULE,
            "github_graphql",
            side_effect=response_for_cursor,
        ) as request:
            total, items = MODULE.fetch_stargazers("owner/repo", "token", 1, 0)

        self.assertEqual(request.call_count, 401)
        self.assertEqual(total, 40_001)
        self.assertEqual(len(items), 40_001)

    def test_missing_token_fails_with_actionable_message(self) -> None:
        with self.assertRaisesRegex(MODULE.StarHistoryUnavailable, "requires GITHUB_TOKEN"):
            MODULE.github_graphql(MODULE.STARGAZERS_QUERY, {}, None, 0)

    def test_non_advancing_cursor_is_rejected(self) -> None:
        response = graphql_page(
            2,
            ["2026-01-01T00:00:00Z"],
            has_next=True,
            end_cursor=None,
        )

        with mock.patch.object(MODULE, "github_graphql", return_value=response):
            with self.assertRaisesRegex(RuntimeError, "did not advance"):
                MODULE.fetch_stargazers("owner/repo", "token", 1, 0)

    def test_source_no_longer_uses_numeric_rest_pagination(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("after: $cursor", source)
        self.assertNotIn("/stargazers?per_page=100&page=", source)


class StarHistoryRenderingTests(unittest.TestCase):
    def test_default_star_marker_is_prominent(self) -> None:
        vertices = [
            tuple(float(value) for value in vertex.split(","))
            for vertex in MODULE.star_polygon_points(100, 100).split()
        ]
        xs = [vertex[0] for vertex in vertices]
        ys = [vertex[1] for vertex in vertices]

        self.assertGreaterEqual(max(xs) - min(xs), 26.5)
        self.assertGreaterEqual(max(ys) - min(ys), 25)

    def test_x_axis_drops_month_tick_that_would_collide_with_end_date(self) -> None:
        ticks = MODULE.x_axis_ticks(
            dt.date(2026, 4, 24),
            dt.date(2026, 8, 7),
            plot_width=844,
        )

        self.assertNotIn(dt.date(2026, 8, 1), ticks)
        self.assertEqual(ticks[-1], dt.date(2026, 8, 7))

    def test_x_axis_keeps_month_tick_when_end_date_has_room(self) -> None:
        ticks = MODULE.x_axis_ticks(
            dt.date(2026, 4, 24),
            dt.date(2026, 8, 24),
            plot_width=844,
        )

        self.assertIn(dt.date(2026, 8, 1), ticks)
        self.assertEqual(ticks[-1], dt.date(2026, 8, 24))

    def test_svg_uses_a_red_star_and_right_aligned_end_date(self) -> None:
        svg = MODULE.generate_svg(
            "example/project",
            [
                (dt.date(2026, 4, 24), 1),
                (dt.date(2026, 8, 7), 100),
            ],
            dt.datetime(2026, 8, 7, tzinfo=dt.timezone.utc),
        )

        self.assertIn('data-marker="latest-star-count"', svg)
        self.assertIn('fill="#dc2626"', svg)
        self.assertNotIn("<circle", svg)
        self.assertNotIn(">2026-08</text>", svg)
        self.assertIn(
            'text-anchor="end" font-size="12" fill="#6b7280">2026-08-07</text>',
            svg,
        )

    def test_svg_uses_reference_style_current_star_kpi(self) -> None:
        svg = MODULE.generate_svg(
            "example/project",
            [
                (dt.date(2026, 4, 24), 1),
                (dt.date(2026, 8, 7), 100),
            ],
            dt.datetime(2026, 8, 7, tzinfo=dt.timezone.utc),
        )

        self.assertIn('data-kpi="current-star-count"', svg)
        self.assertIn('data-marker="current-star-summary"', svg)
        self.assertIn('fill="#f59e0b"', svg)
        self.assertIn('fill="#e11d48">100</text>', svg)
        self.assertIn(">Current Star Count</text>", svg)
        self.assertNotIn(">100 stars</text>", svg)


if __name__ == "__main__":
    unittest.main()
