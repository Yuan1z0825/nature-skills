#!/usr/bin/env python3
"""Generate a static star-history SVG from GitHub stargazer timestamps."""

from __future__ import annotations

import argparse
import collections
import concurrent.futures
import datetime as dt
import html
import json
import math
import os
import pathlib
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request


GITHUB_API = "https://api.github.com"


class StarHistoryUnavailable(RuntimeError):
    """Raised when the API response cannot support a trustworthy chart."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo",
        default=os.environ.get("GITHUB_REPOSITORY", "Yuan1z0825/nature-skills"),
        help="Repository in owner/name form. Defaults to GITHUB_REPOSITORY.",
    )
    parser.add_argument(
        "--output",
        default="assets/star-history.svg",
        help="Output SVG path.",
    )
    parser.add_argument(
        "--cache-bust-readme",
        action="append",
        default=[],
        metavar="PATH",
        help=(
            "Update the output image reference in this Markdown file to a generated "
            "versioned SVG path. Repeat for multiple README files."
        ),
    )
    parser.add_argument(
        "--token",
        default=os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or local_gh_token(),
        help="GitHub token. Defaults to GITHUB_TOKEN, GH_TOKEN, or local gh auth token.",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=4,
        help="Concurrent page fetches. Keep modest to avoid TLS/rate-limit errors.",
    )
    parser.add_argument(
        "--retries",
        type=int,
        default=5,
        help="Retries per GitHub API request.",
    )
    return parser.parse_args()


def local_gh_token() -> str | None:
    """Return the local gh token when available; keep CI independent of gh."""
    try:
        token = subprocess.check_output(
            ["gh", "auth", "token"],
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=10,
        ).strip()
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return None
    return token or None


def github_json(url: str, token: str | None, retries: int) -> object:
    headers = {
        "Accept": "application/vnd.github.star+json",
        "User-Agent": "nature-skills-static-star-history",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    last_error: Exception | None = None
    for attempt in range(retries + 1):
        request = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            last_error = exc
            if exc.code in {403, 429, 500, 502, 503, 504} and attempt < retries:
                reset = exc.headers.get("X-RateLimit-Reset")
                if exc.code == 403 and reset:
                    delay = max(5, int(reset) - int(time.time()) + 2)
                else:
                    delay = min(60, 2 ** attempt)
                print(f"request failed with HTTP {exc.code}; retrying in {delay}s", file=sys.stderr)
                time.sleep(delay)
                continue
            raise
        except (TimeoutError, OSError, urllib.error.URLError) as exc:
            last_error = exc
            if attempt < retries:
                delay = min(60, 2 ** attempt)
                print(f"request failed: {exc}; retrying in {delay}s", file=sys.stderr)
                time.sleep(delay)
                continue
            raise
    raise RuntimeError(f"GitHub request failed after retries: {last_error}")


def fetch_stargazers(repo: str, token: str | None, workers: int, retries: int) -> tuple[int, list[dict]]:
    repo_url = f"{GITHUB_API}/repos/{repo}"
    repo_info = github_json(repo_url, token, retries)
    if not isinstance(repo_info, dict) or "stargazers_count" not in repo_info:
        raise RuntimeError(f"Could not read repository metadata for {repo}")

    total_stars = int(repo_info["stargazers_count"])
    if total_stars == 0:
        print(f"No stars found for {repo}; writing an empty history.")
        return total_stars, []

    pages = max(1, math.ceil(total_stars / 100))
    print(f"Fetching {total_stars:,} stars from {repo} across {pages} pages")

    def fetch_page(page: int) -> tuple[int, list[dict]]:
        url = f"{GITHUB_API}/repos/{repo}/stargazers?per_page=100&page={page}"
        data = github_json(url, token, retries)
        if not isinstance(data, list):
            raise RuntimeError(f"Unexpected stargazers response for page {page}")
        return page, data

    items: list[dict] = []
    completed = 0
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=max(1, workers))
    futures = [executor.submit(fetch_page, page) for page in range(1, pages + 1)]
    try:
        for future in concurrent.futures.as_completed(futures):
            page, page_items = future.result()
            items.extend(page_items)
            completed += 1
            if completed == 1 or completed % 25 == 0 or completed == pages:
                print(f"Fetched {completed}/{pages} pages (latest completed page {page})")
    except Exception:
        for future in futures:
            future.cancel()
        executor.shutdown(wait=False, cancel_futures=True)
        raise
    else:
        executor.shutdown(wait=True)

    return total_stars, items


def build_daily_points(items: list[dict], expected_total: int) -> list[tuple[dt.date, int]]:
    dates = []
    missing_timestamps = 0
    invalid_timestamps = 0
    for item in items:
        if not isinstance(item, dict):
            invalid_timestamps += 1
            continue
        starred_at = item.get("starred_at")
        if not starred_at:
            missing_timestamps += 1
            continue
        try:
            dates.append(dt.datetime.fromisoformat(starred_at.replace("Z", "+00:00")).date())
        except (AttributeError, TypeError, ValueError):
            invalid_timestamps += 1

    if expected_total == 0:
        return []

    skipped = missing_timestamps + invalid_timestamps
    if skipped or not dates:
        raise StarHistoryUnavailable(
            f"GitHub returned {len(dates)} usable starred_at timestamp(s) from "
            f"{len(items)} record(s); leaving the existing chart unchanged. "
            "Check the API Accept header and token permissions."
        )

    dates.sort()
    start = dates[0]
    end = dates[-1]
    by_day = collections.Counter(dates)
    points = []
    running = 0
    day = start
    while day <= end:
        running += by_day.get(day, 0)
        points.append((day, running))
        day += dt.timedelta(days=1)
    return points


def generate_empty_svg(repo: str) -> str:
    """Generate a valid chart placeholder when no star dates are available."""
    width, height = 960, 560
    left, right, top, bottom = 82, 34, 72, 76
    font = "Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif"
    escaped_repo = html.escape(repo, quote=True)
    plot_bottom = height - bottom
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
  <title id="title">Star history for {escaped_repo}</title>
  <desc id="desc">No star history is available for this repository yet.</desc>
  <rect width="100%" height="100%" rx="18" fill="#ffffff"/>
  <text x="{left}" y="34" font-family="{font}" font-size="24" font-weight="700" fill="#111827">Star History</text>
  <text x="{left}" y="58" font-family="{font}" font-size="13" fill="#6b7280">{escaped_repo} · no stars yet</text>
  <g font-family="{font}">
    <line x1="{left}" y1="{top}" x2="{left}" y2="{plot_bottom}" stroke="#d1d5db" stroke-width="1.2"/>
    <line x1="{left}" y1="{plot_bottom}" x2="{width - right}" y2="{plot_bottom}" stroke="#d1d5db" stroke-width="1.2"/>
    <text x="{(left + width - right) / 2:.1f}" y="{top + (plot_bottom - top) / 2:.1f}" text-anchor="middle" font-size="18" fill="#6b7280">No stars yet</text>
    <text x="{left}" y="{height - 16}" font-size="12" fill="#9ca3af">Source: GitHub stargazers API · Static snapshot</text>
  </g>
</svg>
'''


def nice_y_ticks(max_y: int) -> list[int]:
    rough_step = max_y / 5
    power = 10 ** math.floor(math.log10(rough_step)) if rough_step > 0 else 1
    step = power
    for multiplier in (1, 2, 5, 10):
        step = multiplier * power
        if rough_step <= step:
            break
    step = max(1, int(math.ceil(step)))
    ticks = list(range(0, int(math.ceil(max_y / step) * step) + 1, step))
    if ticks[-1] < max_y:
        ticks.append(max_y)
    return ticks


def month_ticks(start: dt.date, end: dt.date, limit: int = 8) -> list[dt.date]:
    current = dt.date(start.year, start.month, 1)
    while current < start:
        current = dt.date(current.year + (current.month == 12), 1 if current.month == 12 else current.month + 1, 1)

    ticks = []
    while current <= end:
        ticks.append(current)
        current = dt.date(current.year + (current.month == 12), 1 if current.month == 12 else current.month + 1, 1)

    if len(ticks) > limit:
        keep_every = math.ceil(len(ticks) / limit)
        ticks = [tick for index, tick in enumerate(ticks) if index % keep_every == 0]
    if end not in ticks:
        ticks.append(end)
    return ticks


def x_axis_ticks(
    start: dt.date,
    end: dt.date,
    plot_width: float,
    limit: int = 8,
    min_end_gap_px: float = 96,
) -> list[dt.date]:
    """Return date ticks with enough room for the exact end-date label."""
    ticks = month_ticks(start, end, limit)
    if len(ticks) < 2 or ticks[-1] != end:
        return ticks

    span_days = max((end - start).days, 1)
    end_gap_px = ((end - ticks[-2]).days / span_days) * plot_width
    if end_gap_px < min_end_gap_px:
        del ticks[-2]
    return ticks


def star_polygon_points(
    cx: float,
    cy: float,
    outer_radius: float = 14,
    inner_radius: float = 6.4,
) -> str:
    """Return the ten alternating vertices of a five-point star."""
    vertices = []
    for index in range(10):
        radius = outer_radius if index % 2 == 0 else inner_radius
        angle = -math.pi / 2 + index * math.pi / 5
        vertices.append(
            f"{cx + radius * math.cos(angle):.1f},"
            f"{cy + radius * math.sin(angle):.1f}"
        )
    return " ".join(vertices)


def generate_svg(
    repo: str,
    points: list[tuple[dt.date, int]],
    generated_at: dt.datetime | None = None,
) -> str:
    start = points[0][0]
    end = points[-1][0]
    total = points[-1][1]

    width, height = 960, 560
    left, right, top, bottom = 82, 34, 72, 76
    plot_width = width - left - right
    plot_height = height - top - bottom
    span_days = max((end - start).days, 1)
    max_y = max(1, total)

    def x_for(day: dt.date) -> float:
        return left + ((day - start).days / span_days) * plot_width

    def y_for(count: int) -> float:
        return top + plot_height - (count / max_y) * plot_height

    reduced = []
    last_day = None
    for day, count in points:
        if last_day is None or (day - last_day).days >= 2 or day == end:
            reduced.append((day, count))
            last_day = day

    line_points = " ".join(f"{x_for(day):.1f},{y_for(count):.1f}" for day, count in reduced)
    area_points = (
        f"{left:.1f},{top + plot_height:.1f} "
        f"{line_points} "
        f"{x_for(end):.1f},{top + plot_height:.1f}"
    )

    grid = []
    for tick in nice_y_ticks(max_y):
        if tick > max_y:
            continue
        y = y_for(tick)
        grid.append(f'<line x1="{left}" y1="{y:.1f}" x2="{width - right}" y2="{y:.1f}" stroke="#e5e7eb" stroke-width="1"/>')
        grid.append(f'<text x="{left - 12}" y="{y + 4:.1f}" text-anchor="end" font-size="12" fill="#6b7280">{tick:,}</text>')

    for tick in x_axis_ticks(start, end, plot_width):
        x = x_for(tick)
        label = tick.strftime("%Y-%m") if tick.day == 1 else tick.strftime("%Y-%m-%d")
        text_anchor = "end" if tick == end else "middle"
        grid.append(f'<line x1="{x:.1f}" y1="{top}" x2="{x:.1f}" y2="{top + plot_height}" stroke="#f3f4f6" stroke-width="1"/>')
        grid.append(f'<text x="{x:.1f}" y="{height - 38}" text-anchor="{text_anchor}" font-size="12" fill="#6b7280">{html.escape(label)}</text>')

    generated_at = generated_at or dt.datetime.now(dt.timezone.utc)
    updated = generated_at.strftime("%Y-%m-%d %H:%M UTC")
    escaped_repo = html.escape(repo, quote=True)
    total_text = f"{total:,}"
    font = "Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif"

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
  <title id="title">Star history for {escaped_repo}</title>
  <desc id="desc">Static star history chart generated from GitHub stargazer timestamps. The repository had {total_text} stars from {start.isoformat()} to {end.isoformat()} when generated at {html.escape(updated)}.</desc>
  <rect width="100%" height="100%" rx="18" fill="#ffffff"/>
  <text x="{left}" y="34" font-family="{font}" font-size="24" font-weight="700" fill="#111827">Star History</text>
  <text x="{left}" y="58" font-family="{font}" font-size="13" fill="#6b7280">{escaped_repo} · {total_text} stars · generated {html.escape(updated)}</text>
  <g data-kpi="current-star-count" role="group" aria-label="Current star count: {total_text}" font-family="{font}">
    <polygon data-marker="current-star-summary" points="{star_polygon_points(748, 31, 13, 6)}" fill="#f59e0b"/>
    <text x="776" y="39" font-size="28" font-weight="800" letter-spacing="-0.5" fill="#e11d48">{total_text}</text>
    <text x="776" y="58" font-size="11.5" fill="#6b7280">Current Star Count</text>
  </g>
  <g font-family="{font}">
    {''.join(grid)}
    <line x1="{left}" y1="{top}" x2="{left}" y2="{top + plot_height}" stroke="#d1d5db" stroke-width="1.2"/>
    <line x1="{left}" y1="{top + plot_height}" x2="{width - right}" y2="{top + plot_height}" stroke="#d1d5db" stroke-width="1.2"/>
    <polygon points="{area_points}" fill="#38bdf8" opacity="0.16"/>
    <polyline points="{line_points}" fill="none" stroke="#0284c7" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
    <polygon data-marker="latest-star-count" points="{star_polygon_points(x_for(end), y_for(total))}" fill="#dc2626" stroke="#ffffff" stroke-width="2.5" stroke-linejoin="round"/>
    <text x="{left}" y="{height - 16}" font-size="12" fill="#9ca3af">Source: GitHub stargazers API · Static snapshot to avoid third-party chart timeouts</text>
  </g>
</svg>
'''


def versioned_output_path(output: pathlib.Path, token: str) -> pathlib.Path:
    """Return a sibling path whose filename changes on every chart update."""
    return output.with_name(f"{output.stem}-{token}{output.suffix}")


def remove_old_versioned_outputs(output: pathlib.Path, keep: pathlib.Path) -> None:
    """Keep only the current versioned chart so snapshots do not accumulate."""
    token_pattern = re.compile(
        rf"^{re.escape(output.stem)}-\d{{8}}T\d{{6}}Z{re.escape(output.suffix)}$"
    )
    for candidate in output.parent.glob(f"{output.stem}-*{output.suffix}"):
        if candidate != keep and token_pattern.fullmatch(candidate.name):
            candidate.unlink()
            print(f"Removed stale versioned chart {candidate}")


def update_readme_cache_buster(
    path: pathlib.Path,
    output_ref: str,
    versioned_ref: str,
) -> None:
    """Use a versioned image path so GitHub cannot reuse a stale Camo render."""
    with path.open("r", encoding="utf-8", newline="") as handle:
        original = handle.read()
    output_path = pathlib.PurePosixPath(output_ref)
    versioned_pattern = (
        rf"{re.escape(output_path.parent.as_posix())}/"
        rf"{re.escape(output_path.stem)}(?:-\d{{8}}T\d{{6}}Z)?"
        rf"{re.escape(output_path.suffix)}(?:\?v=[A-Za-z0-9._-]+)?"
    )
    updated, replacements = re.subn(versioned_pattern, versioned_ref, original)
    if replacements == 0:
        raise RuntimeError(f"Could not find {output_ref!r} in {path}")
    if updated != original:
        with path.open("w", encoding="utf-8", newline="") as handle:
            handle.write(updated)
    print(f"Updated versioned chart reference in {path} ({replacements} occurrence(s))")


def main() -> int:
    args = parse_args()
    if "/" not in args.repo:
        raise SystemExit("--repo must be in owner/name form")

    total_stars, items = fetch_stargazers(args.repo, args.token, args.workers, args.retries)
    try:
        points = build_daily_points(items, total_stars)
    except StarHistoryUnavailable as exc:
        print(f"Warning: {exc}", file=sys.stderr)
        return 0
    output = pathlib.Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    generated_at = dt.datetime.now(dt.timezone.utc)
    svg = generate_svg(args.repo, points, generated_at) if points else generate_empty_svg(args.repo)
    previous_svg = output.read_text(encoding="utf-8") if output.exists() else None
    if previous_svg == svg:
        print(f"{output} is already up to date")
        return 0
    output.write_text(svg, encoding="utf-8")
    cache_token = generated_at.strftime("%Y%m%dT%H%M%SZ")
    versioned_output = versioned_output_path(output, cache_token)
    versioned_output.write_text(svg, encoding="utf-8")
    remove_old_versioned_outputs(output, versioned_output)
    output_ref = pathlib.PurePosixPath(args.output).as_posix()
    versioned_ref = pathlib.PurePosixPath(versioned_output).as_posix()
    for readme in args.cache_bust_readme:
        update_readme_cache_buster(
            pathlib.Path(readme),
            output_ref,
            versioned_ref,
        )
    total = points[-1][1] if points else 0
    print(
        f"Wrote {output} and {versioned_output} with "
        f"{total:,} stars and {len(points):,} daily points"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
