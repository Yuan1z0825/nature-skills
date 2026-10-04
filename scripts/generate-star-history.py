#!/usr/bin/env python3
"""Generate a static star-history SVG from GitHub stargazer timestamps."""

from __future__ import annotations

import argparse
import collections
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
GITHUB_GRAPHQL_API = f"{GITHUB_API}/graphql"

STARGAZERS_QUERY = """
query StarHistory($owner: String!, $name: String!, $cursor: String, $first: Int!, $direction: OrderDirection!) {
  repository(owner: $owner, name: $name) {
    stargazerCount
    stargazers(
      first: $first
      after: $cursor
      orderBy: {field: STARRED_AT, direction: $direction}
    ) {
      edges {
        starredAt
      }
      pageInfo {
        hasNextPage
        endCursor
      }
    }
  }
  rateLimit {
    cost
    remaining
    resetAt
  }
}
"""


PAGE_SIZE = 100
MIN_PAGE_SIZE = 25


class TransientGraphQLError(RuntimeError):
    """GitHub reported a retryable server-side GraphQL failure."""


def is_transient_graphql_error(errors: object) -> bool:
    """Deep stargazer pages on large repos often fail with a generic server error."""
    if not isinstance(errors, list):
        return False
    for error in errors:
        message = str(error.get("message", "") if isinstance(error, dict) else error).lower()
        kind = str(error.get("type", "") if isinstance(error, dict) else "").upper()
        if kind in {"RATE_LIMITED", "TIMEOUT"} or any(
            marker in message
            for marker in ("something went wrong", "timeout", "timed out", "try again")
        ):
            return True
    return False


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
        "--cache",
        default="assets/star-history-data.json",
        help=(
            "JSON file holding per-day new-star counts so later runs only fetch "
            "new stars. Pass an empty string to always do a full fetch."
        ),
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
        default=1,
        help=(
            "Deprecated compatibility option. GraphQL cursor pagination is "
            "sequential, so this value is ignored."
        ),
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


def github_graphql(
    query: str,
    variables: dict[str, object],
    token: str | None,
    retries: int,
) -> dict:
    """Execute an authenticated GitHub GraphQL query with bounded retries."""
    if not token:
        raise StarHistoryUnavailable(
            "GitHub GraphQL stargazer pagination requires GITHUB_TOKEN, GH_TOKEN, "
            "or an authenticated gh CLI."
        )

    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": "nature-skills-static-star-history",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    body = json.dumps({"query": query, "variables": variables}).encode("utf-8")
    last_error: Exception | None = None

    for attempt in range(retries + 1):
        request = urllib.request.Request(
            GITHUB_GRAPHQL_API,
            data=body,
            headers=headers,
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            last_error = exc
            if exc.code in {403, 429, 500, 502, 503, 504} and attempt < retries:
                reset = exc.headers.get("X-RateLimit-Reset")
                if exc.code == 403 and reset:
                    delay = max(5, int(reset) - int(time.time()) + 2)
                else:
                    delay = min(60, 2 ** attempt)
                print(
                    f"GraphQL request failed with HTTP {exc.code}; retrying in {delay}s",
                    file=sys.stderr,
                )
                time.sleep(delay)
                continue
            raise
        except (TimeoutError, OSError, urllib.error.URLError) as exc:
            last_error = exc
            if attempt < retries:
                delay = min(60, 2 ** attempt)
                print(
                    f"GraphQL request failed: {exc}; retrying in {delay}s",
                    file=sys.stderr,
                )
                time.sleep(delay)
                continue
            raise

        if not isinstance(payload, dict):
            raise RuntimeError("GitHub GraphQL returned a non-object response")
        errors = payload.get("errors")
        if errors:
            if is_transient_graphql_error(errors):
                last_error = TransientGraphQLError(
                    f"GitHub GraphQL returned errors: {errors}"
                )
                if attempt < retries:
                    delay = min(60, 2 ** attempt)
                    print(
                        f"GraphQL returned a transient error; retrying in {delay}s",
                        file=sys.stderr,
                    )
                    time.sleep(delay)
                    continue
                raise last_error
            raise RuntimeError(f"GitHub GraphQL returned errors: {errors}")
        return payload

    raise RuntimeError(f"GitHub GraphQL request failed after retries: {last_error}")


def fetch_stargazers(
    repo: str,
    token: str | None,
    workers: int,
    retries: int,
) -> tuple[int, list[dict]]:
    """Fetch every active stargazer timestamp using cursor pagination.

    GitHub's REST stargazers endpoint rejects numeric pages above 400. The
    GraphQL connection uses opaque cursors and continues beyond 40,000 stars.
    ``workers`` remains in the signature for CLI compatibility but is ignored
    because each cursor depends on the preceding page.
    """
    del workers
    try:
        owner, name = repo.split("/", 1)
    except ValueError as exc:
        raise ValueError("repo must be in owner/name form") from exc
    if not owner or not name:
        raise ValueError("repo must be in owner/name form")

    cursor: str | None = None
    items: list[dict] = []
    completed = 0
    expected_pages: int | None = None
    total_stars = 0

    page_size = PAGE_SIZE

    while True:
        try:
            payload = github_graphql(
                STARGAZERS_QUERY,
                {
                    "owner": owner,
                    "name": name,
                    "cursor": cursor,
                    "first": page_size,
                    "direction": "ASC",
                },
                token,
                retries,
            )
        except TransientGraphQLError:
            # A persistently failing page is usually too expensive for GitHub;
            # the cursor stays valid, so retry the same position with fewer rows.
            if page_size <= MIN_PAGE_SIZE:
                raise
            page_size = max(MIN_PAGE_SIZE, page_size // 2)
            print(f"Reducing GraphQL page size to {page_size}", file=sys.stderr)
            continue
        data = payload.get("data")
        if not isinstance(data, dict):
            raise RuntimeError("GitHub GraphQL response is missing data")
        repo_info = data.get("repository")
        if not isinstance(repo_info, dict):
            raise RuntimeError(f"Could not read repository metadata for {repo}")

        try:
            total_stars = int(repo_info["stargazerCount"])
            connection = repo_info["stargazers"]
            edges = connection["edges"]
            page_info = connection["pageInfo"]
        except (KeyError, TypeError, ValueError) as exc:
            raise RuntimeError("Malformed GitHub GraphQL stargazer response") from exc
        if (
            not isinstance(connection, dict)
            or not isinstance(edges, list)
            or not isinstance(page_info, dict)
        ):
            raise RuntimeError("Malformed GitHub GraphQL stargazer connection")

        if expected_pages is None:
            if total_stars == 0:
                print(f"No stars found for {repo}; writing an empty history.")
            expected_pages = max(1, math.ceil(total_stars / PAGE_SIZE))
            print(
                f"Fetching {total_stars:,} stars from {repo} via GraphQL "
                f"cursor pagination ({expected_pages} pages expected)"
            )

        for edge in edges:
            if not isinstance(edge, dict):
                items.append({})
            else:
                items.append({"starred_at": edge.get("starredAt")})

        completed += 1
        has_next_page = page_info.get("hasNextPage")
        if not isinstance(has_next_page, bool):
            raise RuntimeError("GitHub GraphQL pageInfo is missing hasNextPage")
        if completed == 1 or completed % 25 == 0 or not has_next_page:
            print(
                f"Fetched {completed} GraphQL page(s); "
                f"collected {len(items):,}/{total_stars:,} stargazers"
            )
        if not has_next_page:
            break

        next_cursor = page_info.get("endCursor")
        if not isinstance(next_cursor, str) or not next_cursor or next_cursor == cursor:
            raise RuntimeError("GitHub GraphQL pagination did not advance its cursor")
        cursor = next_cursor

    if abs(len(items) - total_stars) > 100:
        raise StarHistoryUnavailable(
            f"GitHub reported {total_stars:,} stars but returned {len(items):,} "
            "stargazer timestamps; leaving the existing chart unchanged."
        )
    if len(items) != total_stars:
        print(
            f"Repository changed during pagination: metadata reported {total_stars:,} "
            f"stars and {len(items):,} timestamp records were fetched. "
            "Using the fetched records for this snapshot.",
            file=sys.stderr,
        )
    return len(items), items


CACHE_VERSION = 1
MAX_INCREMENTAL_PAGES = 50
# Allowed drift between cached counts and GitHub's total (un-starred repos).
CACHE_DRIFT_TOLERANCE = 100


def load_daily_cache(path: pathlib.Path, repo: str) -> dict[dt.date, int] | None:
    """Load per-day new-star counts, or None when absent/unusable."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if data["version"] != CACHE_VERSION or data["repo"] != repo:
            return None
        daily = {
            dt.date.fromisoformat(day): int(count)
            for day, count in data["daily"].items()
        }
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        return None
    if not daily or any(count < 0 for count in daily.values()):
        return None
    return daily


def save_daily_cache(path: pathlib.Path, repo: str, daily: dict[dt.date, int]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "version": CACHE_VERSION,
        "repo": repo,
        "daily": {day.isoformat(): daily[day] for day in sorted(daily)},
    }
    path.write_text(json.dumps(payload, indent=1) + "\n", encoding="utf-8")


def fetch_recent_star_dates(
    repo: str,
    token: str | None,
    retries: int,
    since: dt.date,
) -> tuple[int, list[dt.date]]:
    """Fetch newest-first stargazer dates until reaching a day before ``since``.

    Returns GitHub's current total and every star date >= ``since``. Only the
    newest few pages are read, so this avoids expensive deep pagination.
    """
    owner, name = repo.split("/", 1)
    cursor: str | None = None
    recent: list[dt.date] = []
    total_stars = 0

    for _ in range(MAX_INCREMENTAL_PAGES):
        payload = github_graphql(
            STARGAZERS_QUERY,
            {
                "owner": owner,
                "name": name,
                "cursor": cursor,
                "first": PAGE_SIZE,
                "direction": "DESC",
            },
            token,
            retries,
        )
        try:
            repo_info = payload["data"]["repository"]
            total_stars = int(repo_info["stargazerCount"])
            connection = repo_info["stargazers"]
            edges = connection["edges"]
            page_info = connection["pageInfo"]
            dates = [
                dt.datetime.fromisoformat(edge["starredAt"].replace("Z", "+00:00")).date()
                for edge in edges
            ]
        except (KeyError, TypeError, ValueError, AttributeError) as exc:
            raise StarHistoryUnavailable(
                "Malformed GitHub GraphQL response during incremental fetch"
            ) from exc

        recent.extend(day for day in dates if day >= since)
        reached_cached_range = any(day < since for day in dates)
        if reached_cached_range or not page_info.get("hasNextPage"):
            return total_stars, recent

        next_cursor = page_info.get("endCursor")
        if not isinstance(next_cursor, str) or not next_cursor or next_cursor == cursor:
            raise StarHistoryUnavailable("Incremental pagination did not advance its cursor")
        cursor = next_cursor

    raise StarHistoryUnavailable(
        f"Incremental fetch exceeded {MAX_INCREMENTAL_PAGES} pages without reaching the cache"
    )


def merge_recent_into_daily(
    daily: dict[dt.date, int],
    recent: list[dt.date],
    since: dt.date,
) -> dict[dt.date, int]:
    """Replace every day >= ``since`` with freshly counted values."""
    merged = {day: count for day, count in daily.items() if day < since}
    merged.update(collections.Counter(recent))
    return merged


def update_daily_incrementally(
    repo: str,
    token: str | None,
    retries: int,
    daily: dict[dt.date, int],
) -> dict[dt.date, int] | None:
    """Return refreshed counts, or None when a full refresh is needed."""
    since = max(daily)
    try:
        total_stars, recent = fetch_recent_star_dates(repo, token, retries, since)
    except StarHistoryUnavailable as exc:
        print(f"Incremental update unavailable ({exc}); falling back to full fetch.", file=sys.stderr)
        return None
    merged = merge_recent_into_daily(daily, recent, since)
    drift = sum(merged.values()) - total_stars
    if abs(drift) > CACHE_DRIFT_TOLERANCE:
        print(
            f"Cached history differs from GitHub's total by {drift:+,}; "
            "falling back to full fetch.",
            file=sys.stderr,
        )
        return None
    print(
        f"Incremental update: {len(recent):,} star(s) since {since}; "
        f"history now {sum(merged.values()):,} (GitHub reports {total_stars:,})"
    )
    return merged


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

    return points_from_daily(collections.Counter(dates))


def points_from_daily(by_day: collections.Counter | dict[dt.date, int]) -> list[tuple[dt.date, int]]:
    """Turn per-day new-star counts into a cumulative, gap-free series."""
    if not by_day:
        return []
    start = min(by_day)
    end = max(by_day)
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

    cache_path = pathlib.Path(args.cache) if args.cache else None
    daily = load_daily_cache(cache_path, args.repo) if cache_path else None
    if daily is not None:
        daily = update_daily_incrementally(args.repo, args.token, args.retries, daily)

    if daily is None:
        total_stars, items = fetch_stargazers(args.repo, args.token, args.workers, args.retries)
        try:
            points = build_daily_points(items, total_stars)
        except StarHistoryUnavailable as exc:
            print(f"Warning: {exc}", file=sys.stderr)
            return 0
        daily = {}
        previous = 0
        for day, cumulative in points:
            daily[day] = cumulative - previous
            previous = cumulative
    else:
        points = points_from_daily(daily)
    if cache_path and daily:
        save_daily_cache(cache_path, args.repo, daily)
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
