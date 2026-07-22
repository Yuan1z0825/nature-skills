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
            "Update the output image reference in this Markdown file with a generated "
            "version query. Repeat for multiple README files."
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


def fetch_stargazers(repo: str, token: str | None, workers: int, retries: int) -> list[dict]:
    repo_url = f"{GITHUB_API}/repos/{repo}"
    repo_info = github_json(repo_url, token, retries)
    if not isinstance(repo_info, dict) or "stargazers_count" not in repo_info:
        raise RuntimeError(f"Could not read repository metadata for {repo}")

    total_stars = int(repo_info["stargazers_count"])
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

    return items


def build_daily_points(items: list[dict]) -> list[tuple[dt.date, int]]:
    dates = []
    for item in items:
        starred_at = item.get("starred_at")
        if not starred_at:
            continue
        dates.append(dt.datetime.fromisoformat(starred_at.replace("Z", "+00:00")).date())

    if not dates:
        raise RuntimeError(
            "GitHub did not return starred_at timestamps. "
            "Make sure the request uses Accept: application/vnd.github.star+json and a token with access."
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


def nice_y_ticks(max_y: int) -> list[int]:
    rough_step = max_y / 5
    power = 10 ** math.floor(math.log10(rough_step)) if rough_step > 0 else 1
    step = power
    for multiplier in (1, 2, 5, 10):
        step = multiplier * power
        if rough_step <= step:
            break
    ticks = list(range(0, int(math.ceil(max_y / step) * step) + 1, int(step)))
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

    for tick in month_ticks(start, end):
        x = x_for(tick)
        label = tick.strftime("%Y-%m") if tick.day == 1 else tick.strftime("%Y-%m-%d")
        grid.append(f'<line x1="{x:.1f}" y1="{top}" x2="{x:.1f}" y2="{top + plot_height}" stroke="#f3f4f6" stroke-width="1"/>')
        grid.append(f'<text x="{x:.1f}" y="{height - 38}" text-anchor="middle" font-size="12" fill="#6b7280">{html.escape(label)}</text>')

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
  <g font-family="{font}">
    {''.join(grid)}
    <line x1="{left}" y1="{top}" x2="{left}" y2="{top + plot_height}" stroke="#d1d5db" stroke-width="1.2"/>
    <line x1="{left}" y1="{top + plot_height}" x2="{width - right}" y2="{top + plot_height}" stroke="#d1d5db" stroke-width="1.2"/>
    <polygon points="{area_points}" fill="#38bdf8" opacity="0.16"/>
    <polyline points="{line_points}" fill="none" stroke="#0284c7" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
    <circle cx="{x_for(end):.1f}" cy="{y_for(total):.1f}" r="4.5" fill="#0284c7" stroke="#ffffff" stroke-width="2"/>
    <text x="{width - right}" y="{y_for(total) - 10:.1f}" text-anchor="end" font-size="13" font-weight="700" fill="#0369a1">{total_text} stars</text>
    <text x="{left}" y="{height - 16}" font-size="12" fill="#9ca3af">Source: GitHub stargazers API · Static snapshot to avoid third-party chart timeouts</text>
  </g>
</svg>
'''


def update_readme_cache_buster(path: pathlib.Path, output_ref: str, token: str) -> None:
    """Version a Markdown image URL so GitHub does not reuse a stale render."""
    original = path.read_text(encoding="utf-8")
    pattern = re.compile(rf"{re.escape(output_ref)}(?:\?v=[A-Za-z0-9._-]+)?")
    updated, replacements = pattern.subn(f"{output_ref}?v={token}", original)
    if replacements == 0:
        raise RuntimeError(f"Could not find {output_ref!r} in {path}")
    if updated != original:
        path.write_text(updated, encoding="utf-8")
    print(f"Updated cache-busting reference in {path} ({replacements} occurrence(s))")


def main() -> int:
    args = parse_args()
    if "/" not in args.repo:
        raise SystemExit("--repo must be in owner/name form")

    items = fetch_stargazers(args.repo, args.token, args.workers, args.retries)
    points = build_daily_points(items)
    output = pathlib.Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    generated_at = dt.datetime.now(dt.timezone.utc)
    output.write_text(generate_svg(args.repo, points, generated_at), encoding="utf-8")
    cache_token = generated_at.strftime("%Y%m%dT%H%M%SZ")
    output_ref = pathlib.PurePosixPath(args.output).as_posix()
    for readme in args.cache_bust_readme:
        update_readme_cache_buster(pathlib.Path(readme), output_ref, cache_token)
    print(f"Wrote {output} with {points[-1][1]:,} stars and {len(points):,} daily points")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
