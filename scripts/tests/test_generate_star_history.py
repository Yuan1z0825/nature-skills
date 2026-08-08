from __future__ import annotations

import datetime as dt
import importlib.util
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "generate-star-history.py"
SPEC = importlib.util.spec_from_file_location("generate_star_history", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


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
