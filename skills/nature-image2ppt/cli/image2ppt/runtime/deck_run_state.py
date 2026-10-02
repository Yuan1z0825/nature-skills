import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ACTIVE_PAGE_STATUSES = {"dispatched"}
DISPATCHABLE_PAGE_STATUSES = {"pending"}
DEFAULT_MAX_CONCURRENT_PAGES = 6


def now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def read_json(path, default=None):
    path = Path(path)
    if not path.exists():
        if default is not None:
            return default
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_text(value):
    return hashlib.sha256(str(value).encode("utf-8")).hexdigest()


def run_dir_from_target(target):
    path = Path(target).expanduser().resolve()
    if path.is_dir():
        return path
    if path.name == "deck_manifest.json":
        return path.parent
    raise ValueError(f"Expected run directory or deck_manifest.json: {target}")


def deck_manifest_path(run_dir):
    return Path(run_dir) / "deck_manifest.json"


def page_jobs_path(run_dir):
    return Path(run_dir) / "page_jobs.json"


def run_state_path(run_dir):
    return Path(run_dir) / "run_state.json"


def load_deck(run_dir):
    return read_json(deck_manifest_path(run_dir))


def save_deck(run_dir, deck):
    write_json(deck_manifest_path(run_dir), deck)


def load_jobs(run_dir):
    return read_json(page_jobs_path(run_dir))


def save_jobs(run_dir, jobs):
    write_json(page_jobs_path(run_dir), jobs)


def load_run_state(run_dir):
    return read_json(run_state_path(run_dir), default={"status": "created", "history": []})


def save_run_state(run_dir, state):
    write_json(run_state_path(run_dir), state)


def set_run_status(run_dir, status, note=None):
    state = load_run_state(run_dir)
    if state.get("status") != status:
        state.setdefault("history", []).append(
            {"from": state.get("status"), "to": status, "at": now_iso(), "note": note}
        )
    state["status"] = status
    state["updated_at"] = now_iso()
    save_run_state(run_dir, state)
    return state


def normalize_page_id(value):
    text = str(value).strip()
    if text.startswith("page_"):
        return text
    if text.isdigit():
        return f"page_{int(text):03d}"
    raise ValueError(f"Invalid page id: {value}")


def find_page(jobs, page):
    page_id = normalize_page_id(page)
    for entry in jobs.get("pages", []):
        if entry.get("page_id") == page_id or entry.get("id") == page_id:
            return entry
    raise KeyError(f"Page not found in page_jobs.json: {page_id}")


def resolve_run_path(run_dir, value):
    return resolve_inside(run_dir, value)


def rel_to_run(run_dir, value):
    path = Path(value).resolve()
    return path.relative_to(Path(run_dir).resolve()).as_posix()


def resolve_inside(base_dir, value):
    base = Path(base_dir).resolve()
    path = Path(value)
    if not path.is_absolute():
        path = base / path
    path = path.resolve()
    try:
        path.relative_to(base)
    except ValueError as exc:
        raise ValueError(f"Path is outside allowed directory: {path}") from exc
    return path


def all_pages_have_status(jobs, statuses):
    allowed = set(statuses)
    return all(page.get("status") in allowed for page in jobs.get("pages", []))


def max_concurrent_pages(jobs):
    value = jobs.get("max_concurrent_pages", DEFAULT_MAX_CONCURRENT_PAGES)
    try:
        value = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid max_concurrent_pages: {value}") from exc
    if value < 1:
        raise ValueError("max_concurrent_pages must be >= 1")
    return value


def active_pages(jobs):
    return [page for page in jobs.get("pages", []) if page.get("status") in ACTIVE_PAGE_STATUSES]


def dispatchable_pages(jobs):
    return [
        page
        for page in jobs.get("pages", [])
        if page.get("status") in DISPATCHABLE_PAGE_STATUSES
    ]


def dispatch_slots_available(jobs):
    return max(0, max_concurrent_pages(jobs) - len(active_pages(jobs)))


def update_jobs_run_status(jobs):
    pages = jobs.get("pages", [])
    if pages and all(page.get("status") in {"dispatched", "recorded", "accepted"} for page in pages):
        jobs["run_status"] = "pages_dispatched"
    if pages and all(page.get("status") in {"recorded", "accepted"} for page in pages):
        jobs["run_status"] = "pages_recorded"
    if pages and all(page.get("status") == "accepted" for page in pages):
        jobs["run_status"] = "complete"
    jobs["updated_at"] = now_iso()


def inside_or_missing(page_dir, value):
    path = resolve_inside(page_dir, value)
    if not path.exists():
        raise FileNotFoundError(path)
    return path


def safe_agent_label(agent_id, nickname=None):
    label = str(agent_id).strip()
    if nickname:
        label += f" ({nickname})"
    return label


def page_dir_for(run_dir, page):
    return resolve_inside(run_dir, page["page_dir"])


def ensure_file(path, label):
    path = Path(path)
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"Missing {label}: {path}")
    return path


def ensure_dir(path, label):
    path = Path(path)
    if not path.exists() or not path.is_dir():
        raise FileNotFoundError(f"Missing {label}: {path}")
    return path
