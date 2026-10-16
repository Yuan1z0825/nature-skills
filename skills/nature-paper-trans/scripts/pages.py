#!/usr/bin/env python3
"""Prepare reference pages and assemble externally generated images; never call AI."""

import argparse
import contextlib
import hashlib
import html
import io
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import time
from datetime import datetime, timezone
import uuid

if os.name == "nt":
    import msvcrt
else:
    import fcntl

try:
    import pymupdf as fitz
    from PIL import Image
except ImportError as exc:
    print(json.dumps({"error": "dependency_missing", "message": str(exc)}), file=sys.stderr)
    sys.exit(2)


class TaskError(Exception):
    pass


class Parser(argparse.ArgumentParser):
    def error(self, message):
        raise TaskError(message)


def require(condition, message):
    if not condition:
        raise TaskError(message)


A4_PAGE_SIZE_POINTS = (210 * 72 / 25.4, 297 * 72 / 25.4)
# Used only when reading a legacy task created before source page sizes were
# recorded. New tasks always preserve each source PDF page's own size.
LEGACY_PAGE_SIZE_POINTS = A4_PAGE_SIZE_POINTS


def now():
    return datetime.now(timezone.utc).isoformat()


def digest(path):
    require(path.is_file(), "File missing: " + str(path))
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def _publish_without_replace(source, target):
    """Publish a completed temporary file without replacing an existing target."""
    try:
        os.link(source, target)
    except (AttributeError, OSError):
        if os.name != "nt":
            raise
        # Windows rename refuses to replace an existing destination, which
        # preserves the no-overwrite contract when hard links are unavailable.
        os.rename(source, target)


def _sync_directory(path):
    """Durably sync a parent directory where the platform exposes that API."""
    if os.name == "nt":
        return
    directory = os.open(str(path), os.O_RDONLY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)


def atomic_bytes(path, data, replace=True):
    fd, temporary = tempfile.mkstemp(prefix="." + path.name + "-", dir=str(path.parent))
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        if replace:
            os.replace(temporary, path)
        else:
            _publish_without_replace(temporary, path)
        _sync_directory(path.parent)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def save(work, task):
    task["updated_at"] = now()
    atomic_bytes(work / "task.json", json.dumps(task, ensure_ascii=False, indent=2).encode("utf-8"))


def _lock_stream(stream):
    if os.name == "nt":
        # msvcrt locks a byte range. Keep one byte in the lock file and use
        # the blocking mode so concurrent commands wait for the owner.
        stream.seek(0)
        stream.write(b"\0")
        stream.flush()
        stream.seek(0)
        while True:
            try:
                msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
                break
            except OSError:
                time.sleep(0.1)
        return
    fcntl.flock(stream.fileno(), fcntl.LOCK_EX)


def _unlock_stream(stream):
    if os.name == "nt":
        stream.seek(0)
        msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
        return
    fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


@contextlib.contextmanager
def locked(work, create=False):
    if create:
        work.mkdir(parents=True, exist_ok=True)
    require(work.is_dir(), "Work directory missing: " + str(work))
    with (work / ".task.lock").open("a+b") as stream:
        _lock_stream(stream)
        try:
            yield
        finally:
            _unlock_stream(stream)


def migrate_v1(task):
    """Convert in memory without increasing the budget of an existing job."""
    task["version"] = 2
    task["policy"] = {"max_in_flight": 5, "max_attempts_per_page": 1}
    task["legacy_review_exempt"] = True
    for number, old in list(task["pages"].items()):
        require(old.get("state") in ("pending", "reserved", "failed", "recorded"), "Invalid legacy page state")
        require(old.get("attempts") == (0 if old["state"] == "pending" else 1), "Invalid legacy attempt ledger")
        page = {key: old[key] for key in ("input", "input_sha256", "input_dimensions") if key in old}
        page.update(attempts=old["attempts"], attempt_records=[], selected_attempt_id=None,
                    selection_confirmed=True, legacy_output=old["output"])
        if old["attempts"]:
            attempt = {key: value for key, value in old.items()
                       if key not in ("input", "input_sha256", "input_dimensions", "attempts")}
            attempt.setdefault("attempt_id", str(uuid.uuid5(uuid.NAMESPACE_URL,
                               task["task_id"] + "/page/" + number + "/legacy-attempt-1")))
            attempt.update(attempt_number=1, purpose="initial")
            page["attempt_records"].append(attempt)
            if attempt["state"] == "recorded":
                page["selected_attempt_id"] = attempt["attempt_id"]
        task["pages"][number] = page
    return task


def load(work):
    manifest = work / "task.json"
    require(manifest.is_file(), "No task.json; run prepare first")
    with manifest.open(encoding="utf-8") as stream:
        task = json.load(stream)
    require(task.get("version") in (1, 2), "Unsupported task manifest version")
    require(task.get("selected_pages") and isinstance(task.get("pages"), dict), "Invalid task manifest")
    if task["version"] == 1:
        task = migrate_v1(task)
    require(isinstance(task.get("pending_assemblies", {}), dict), "Invalid pending assembly ledger")
    return task


def asset(work, relative):
    path = (work / relative).resolve()
    require(work in path.parents, "Asset path escapes work directory")
    return path


def check_source(task):
    require(digest(Path(task["source"]["path"])) == task["source"]["sha256"], "Source PDF changed")


def check_assets(work, task, allow_pending_missing=False):
    policy = task.get("policy", {})
    require(type(policy.get("max_in_flight")) is int and 1 <= policy["max_in_flight"] <= 10,
            "Invalid in-flight policy")
    require(type(policy.get("max_attempts_per_page")) is int and 1 <= policy["max_attempts_per_page"] <= 2,
            "Invalid per-page policy")
    seen_ids = set()
    for number in task["selected_pages"]:
        page = task["pages"][str(number)]
        source_size = page.get("source_page_size")
        if source_size is not None:
            require(isinstance(source_size, list) and len(source_size) == 2
                    and all(isinstance(value, (int, float)) and value > 0 for value in source_size),
                    "Invalid source page size")
        records = page.get("attempt_records")
        require(isinstance(records, list) and type(page.get("attempts")) is int
                and page["attempts"] == len(records) <= policy["max_attempts_per_page"], "Invalid attempt ledger")
        require(sum(a.get("state") == "reserved" for a in records) <= 1, "Multiple unresolved attempts on a page")
        require(type(page.get("selection_confirmed")) is bool, "Invalid selection state")
        source = asset(work, page["input"])
        if not source.exists() and allow_pending_missing and not records:
            continue
        require(page.get("input_sha256") and digest(source) == page["input_sha256"],
                "Reference image changed: page " + str(number))
        for index, attempt in enumerate(records, 1):
            require(attempt.get("attempt_number") == index, "Invalid attempt number")
            require(attempt.get("state") in ("reserved", "failed", "recorded"), "Invalid attempt state")
            require(attempt.get("purpose") == "initial" if index == 1
                    else attempt.get("purpose") in ("repair", "recovery"), "Invalid attempt purpose")
            identifier = attempt.get("attempt_id")
            require(isinstance(identifier, str) and identifier and identifier not in seen_ids,
                    "Missing or duplicate attempt ID")
            seen_ids.add(identifier)
            if attempt.get("prompt"):
                require(digest(asset(work, attempt["prompt"])) == attempt.get("prompt_sha256"),
                        "Prompt snapshot changed: page " + str(number))
            else:
                require(task.get("legacy_review_exempt"), "Missing prompt snapshot")
            if attempt.get("review") is not None:
                require(attempt["state"] == "recorded", "Unrecorded attempt has an image review")
                validate_review(attempt["review"], attempt, allow_legacy=True)
            target = asset(work, attempt["output"])
            if attempt["state"] == "recorded":
                require(digest(target) == attempt.get("output_sha256"),
                        "Generated image changed: page " + str(number))
                require(isinstance(attempt.get("output_dimensions"), list)
                        and len(attempt["output_dimensions"]) == 2
                        and all(type(v) is int and v > 0 for v in attempt["output_dimensions"]),
                        "Invalid generated image dimensions")
            elif target.exists():
                # Interrupted record: only this attempt may recover this immutable file.
                require(attempt["state"] in ("reserved", "failed"), "Unexpected output: " + str(target))
        selected = page.get("selected_attempt_id")
        require(selected is None or any(a["attempt_id"] == selected and a["state"] == "recorded" for a in records),
                "Selected image is not a recorded attempt")
    require(len(unresolved(task)) <= policy["max_in_flight"], "In-flight budget exceeded in ledger")


def checked(work):
    task = load(work)
    check_source(task)
    check_assets(work, task)
    return task


def selected_pages(value, count):
    if value.strip().lower() == "all":
        return list(range(1, count + 1))
    pages = set()
    for token in value.split(","):
        match = re.fullmatch(r"\s*(\d+)\s*(?:-\s*(\d+)\s*)?", token)
        require(match is not None, "Pages must be all or physical page numbers such as 1-3,5")
        first = int(match.group(1))
        last = int(match.group(2) or first)
        require(1 <= first <= last <= count, "Page selection outside PDF range or reversed")
        pages.update(range(first, last + 1))
    require(pages, "Empty page selection")
    return sorted(pages)


def page_record(task, number):
    require(str(number) in task["pages"], "Page not selected: " + str(number))
    return task["pages"][str(number)]


def source_page_size(task, number, page=None):
    """Return the source PDF page size, including for legacy task ledgers."""
    recorded = (page or page_record(task, number)).get("source_page_size")
    if recorded:
        return recorded
    try:
        with fitz.open(task["source"]["path"]) as source:
            rect = source[number - 1].rect
            return [float(rect.width), float(rect.height)]
    except (OSError, IndexError, KeyError, ValueError):
        return LEGACY_PAGE_SIZE_POINTS


def attempt_record(page, identifier):
    matches = [a for a in page["attempt_records"] if a["attempt_id"] == identifier]
    require(len(matches) == 1, "Attempt ID does not belong to this page")
    return matches[0]


def unresolved(task):
    return [(int(number), attempt) for number, page in task["pages"].items()
            for attempt in page["attempt_records"] if attempt["state"] == "reserved"]


def first_round_complete(task):
    return all(task["pages"][str(n)]["attempt_records"]
               and task["pages"][str(n)]["attempt_records"][0]["state"] in ("recorded", "failed")
               for n in task["selected_pages"])


def available(page):
    return [a for a in page["attempt_records"] if a["state"] == "recorded"]


def selected_attempt(page):
    identifier = page.get("selected_attempt_id")
    return attempt_record(page, identifier) if identifier else None


def page_state(page):
    if not page["attempt_records"]:
        return "pending"
    if any(a["state"] == "reserved" for a in page["attempt_records"]):
        return "unknown"
    return "recorded" if selected_attempt(page) else "failed"


def overview(work, task):
    counts = {name: 0 for name in ("pending", "unknown", "failed", "recorded")}
    pages = []
    for number in task["selected_pages"]:
        page = task["pages"][str(number)]
        state = page_state(page)
        counts[state] += 1
        selected = selected_attempt(page)
        records = []
        for attempt in page["attempt_records"]:
            item = dict(attempt)
            item["state"] = "unknown" if attempt["state"] == "reserved" else attempt["state"]
            item["output"] = str(asset(work, attempt["output"])) if attempt["state"] == "recorded" else None
            if attempt["state"] in ("reserved", "failed") and asset(work, attempt["output"]).is_file():
                item["recoverable_output"] = str(asset(work, attempt["output"]))
            if attempt.get("prompt"):
                item["prompt"] = str(asset(work, attempt["prompt"]))
            item["review_status"] = attempt.get("review", {}).get("status", "unknown")
            records.append(item)
        pages.append({"page": number, "state": state, "attempts": page["attempts"],
                      "input": str(asset(work, page["input"])),
                      "output": str(asset(work, selected["output"])) if selected else None,
                      "selected_attempt_id": page["selected_attempt_id"],
                      "selection_confirmed": page["selection_confirmed"], "attempt_records": records})
    return {"task_id": task["task_id"], "work_dir": str(work), "total": len(pages),
            "policy": {"max_in_flight": min(task["policy"]["max_in_flight"], 10), "max_attempts_per_page": 1},
            "historical_policy": task["policy"], "first_round_complete": first_round_complete(task),
            "in_flight": len(unresolved(task)), "total_attempts": sum(p["attempts"] for p in task["pages"].values()),
            "pending_assemblies": [{key: item[key] for key in ("path", "sha256", "page_count", "missing_pages")}
                                   for item in task.get("pending_assemblies", {}).values()],
            "latest_assembly": task.get("assemblies", [])[-1] if task.get("assemblies") else None,
            "counts": counts, "pages": pages}


def prepare(args, work):
    source = Path(args.pdf).expanduser().resolve()
    require(args.dpi > 0, "DPI must be positive")
    source_hash = digest(source)
    with fitz.open(str(source)) as pdf:
        require(pdf.is_pdf and len(pdf) > 0, "Source must be a nonempty PDF")
        require(not (pdf.is_encrypted or pdf.needs_pass or pdf.metadata.get("encryption")),
                "Encrypted PDFs are not supported")
        selected = selected_pages(args.pages, len(pdf))
        with locked(work, create=True):
            if (work / "task.json").exists():
                task = load(work)
                require(task["source"]["path"] == str(source) and task["source"]["sha256"] == source_hash,
                        "Work directory belongs to a different or changed source PDF")
                require(task["selected_pages"] == selected, "Work directory has a different page selection")
                require(task["dpi"] == args.dpi, "Work directory has a different render DPI")
                check_assets(work, task, allow_pending_missing=True)
            else:
                require(not any((work / name).exists() for name in ("input", "output")),
                        "Untracked input/output directory exists; use a fresh work directory")
                task = {"version": 2, "task_id": str(uuid.uuid4()), "created_at": now(),
                        "source": {"path": str(source), "sha256": source_hash, "page_count": len(pdf)},
                        "dpi": args.dpi, "selected_pages": selected, "pages": {}, "assemblies": [],
                        "policy": {"max_in_flight": 10, "max_attempts_per_page": 1},
                        "legacy_review_exempt": False}
                authorization = getattr(args, "authorization", None)
                if authorization is not None:
                    require(authorization.strip(), "Authorization source must be nonempty")
                    task["authorization"] = authorization.strip()
                for number in selected:
                    task["pages"][str(number)] = {"attempts": 0, "attempt_records": [],
                        "input": "input/page-%04d.png" % number, "selected_attempt_id": None,
                        "selection_confirmed": True}
                save(work, task)
            (work / "input").mkdir(exist_ok=True)
            (work / "output").mkdir(exist_ok=True)
            (work / "prompts").mkdir(exist_ok=True)
            rendered = []
            for number in selected:
                record = task["pages"][str(number)]
                target = asset(work, record["input"])
                source_rect = pdf[number - 1].rect
                source_size = [float(source_rect.width), float(source_rect.height)]
                if record.get("source_page_size") != source_size:
                    record["source_page_size"] = source_size
                    save(work, task)
                if target.exists():
                    continue
                require(record["attempts"] == 0, "Cannot recreate reference after attempt was spent")
                pixmap = pdf[number - 1].get_pixmap(matrix=fitz.Matrix(args.dpi / 72, args.dpi / 72),
                                                  colorspace=fitz.csRGB, alpha=False)
                data = pixmap.tobytes("png")
                record.update(input_sha256=hashlib.sha256(data).hexdigest(),
                              input_dimensions=[pixmap.width, pixmap.height])
                save(work, task)
                atomic_bytes(target, data)
                rendered.append(number)
            check_source(task)
            return dict(overview(work, task), rendered=rendered)


def reserve(args, work):
    prompt_source = Path(args.prompt_file).expanduser().resolve()
    require(prompt_source.is_file(), "Prompt file missing: " + str(prompt_source))
    prompt_data = prompt_source.read_bytes()
    require(prompt_data.decode("utf-8").strip(), "Prompt must be nonempty UTF-8 text")
    with locked(work):
        task = checked(work)
        page = page_record(task, args.page)
        records = page["attempt_records"]
        require(not any(a["state"] == "reserved" for a in records), "An unresolved attempt cannot be resubmitted")
        require(len(unresolved(task)) < task["policy"]["max_in_flight"], "In-flight request limit reached")
        require(not records and page["attempts"] == 0, "This page has already used its single attempt in this round")
        require(args.purpose == "initial", "Only an initial attempt is permitted")
        identifier = str(uuid.uuid4())
        number = len(records) + 1
        prompt_relative = "prompts/" + identifier + ".md"
        (work / "prompts").mkdir(exist_ok=True)
        atomic_bytes(asset(work, prompt_relative), prompt_data, replace=False)
        output = page.get("legacy_output") if number == 1 else None
        attempt = {"attempt_id": identifier, "attempt_number": number, "purpose": args.purpose,
                   "state": "reserved", "reserved_at": now(), "prompt": prompt_relative,
                   "prompt_sha256": hashlib.sha256(prompt_data).hexdigest(), "prompt_source": str(prompt_source),
                   "output": output or "output/page-%04d-attempt-%d.png" % (args.page, number)}
        records.append(attempt)
        page["attempts"] = len(records)
        save(work, task)
        return {"page": args.page, "state": "reserved", "attempts": page["attempts"], "purpose": args.purpose,
                "attempt_id": identifier, "input": str(asset(work, page["input"])),
                "prompt": str(asset(work, prompt_relative)), "prompt_sha256": attempt["prompt_sha256"]}


def normalized_image(path):
    require(path.is_file(), "Generated image missing: " + str(path))
    with Image.open(path) as image:
        image.load()
        require(getattr(image, "n_frames", 1) == 1, "Generated image must contain one frame")
        require(image.width > 0 and image.height > 0, "Generated image has invalid dimensions")
        if "A" in image.getbands() or "transparency" in image.info:
            rgba = image.convert("RGBA")
            rgb = Image.new("RGB", rgba.size, "white")
            rgb.paste(rgba, mask=rgba.getchannel("A"))
        else:
            rgb = image.convert("RGB")
        data = io.BytesIO()
        rgb.save(data, format="PNG")
        return data.getvalue(), [rgb.width, rgb.height]


def record(args, work):
    with locked(work):
        task = checked(work)
        page = page_record(task, args.page)
        attempt = attempt_record(page, args.attempt_id)
        require(attempt["state"] in ("reserved", "failed", "recorded"), "Reserve an attempt before recording")
        generated = Path(args.image).expanduser().resolve()
        require(generated != Path(task["source"]["path"]), "Generated image cannot be the source PDF")
        require(work / "input" not in generated.parents, "Generated image cannot be a reference image")
        data, dimensions = normalized_image(generated)
        image_hash = hashlib.sha256(data).hexdigest()
        duplicates = sorted({int(number) for number, other in task["pages"].items()
                             if int(number) != args.page and any(a.get("output_sha256") == image_hash
                                                                for a in other["attempt_records"])})
        target = asset(work, attempt["output"])
        if attempt["state"] == "recorded":
            require(image_hash == attempt["output_sha256"], "Recorded output cannot be replaced")
            return {"page": args.page, "state": "recorded", "output": str(target), "reused": True,
                    "attempt_id": args.attempt_id, "duplicate_image_pages": duplicates}
        if target.exists():
            require(digest(target) == image_hash, "Existing output differs from recovered attempt")
        else:
            atomic_bytes(target, data, replace=False)
        attempt.update(state="recorded", recorded_at=now(), output_sha256=image_hash,
                       output_dimensions=dimensions, generated_source=str(generated))
        images = available(page)
        # New rounds have one image; late historical results retain the existing selection.
        if not page.get("selected_attempt_id"):
            page.update(selected_attempt_id=images[0]["attempt_id"], selection_confirmed=True)
        save(work, task)
        return {"page": args.page, "state": "recorded", "output": str(target), "dimensions": dimensions,
                "attempt_id": args.attempt_id, "selected_attempt_id": page["selected_attempt_id"],
                "selection_confirmed": page["selection_confirmed"], "duplicate_image_pages": duplicates}


def fail(args, work):
    with locked(work):
        task = checked(work)
        page = page_record(task, args.page)
        attempt = attempt_record(page, args.attempt_id)
        require(attempt["state"] == "reserved", "Only a reserved attempt can be marked failed")
        require(not asset(work, attempt["output"]).exists(),
                "Attempt already has a saved image; recover it with record and its original attempt ID")
        require(args.reason.strip(), "Failure reason must be nonempty")
        attempt.update(state="failed", failed_at=now(), failure_reason=args.reason.strip())
        save(work, task)
        return {"page": args.page, "state": "failed", "attempts": page["attempts"],
                "attempt_id": args.attempt_id, "selected_attempt_id": page["selected_attempt_id"]}


def validate_review(value, attempt=None, allow_legacy=False):
    require(isinstance(value, dict), "Review must be a JSON object")
    require(value.get("status") in ("pass", "issue", "unknown"), "Invalid review status")
    require(isinstance(value.get("observations"), list)
            and all(isinstance(v, str) and v.strip() for v in value["observations"]),
            "Review observations must be a list of nonempty strings")
    require(allow_legacy or bool(value["observations"]), "Review observations must not be empty")


def review(args, work):
    source = Path(args.review_file).expanduser().resolve()
    require(source.is_file(), "Review file missing: " + str(source))
    with source.open(encoding="utf-8") as stream:
        value = json.load(stream)
    with locked(work):
        task = checked(work)
        page = page_record(task, args.page)
        attempt = attempt_record(page, args.attempt_id)
        require(attempt["state"] == "recorded", "Only a recorded image can be reviewed")
        validate_review(value, attempt)
        value = {"status": value["status"], "observations": value["observations"]}
        if attempt.get("review") == value:
            return {"page": args.page, "attempt_id": args.attempt_id, "review": value, "reused": True}
        attempt.update(review=value, reviewed_at=now(), review_source=str(source))
        save(work, task)
        return {"page": args.page, "attempt_id": args.attempt_id, "review": value}


def select(args, work):
    require(args.reason.strip(), "Selection reason must be nonempty")
    with locked(work):
        task = checked(work)
        page = page_record(task, args.page)
        require(len(page["attempt_records"]) > 1, "Selection is only available for historical multi-attempt pages")
        require(not any(a["state"] == "reserved" for a in page["attempt_records"]),
                "Resolve this page's submitted requests before selection")
        attempt = attempt_record(page, args.attempt_id)
        require(attempt["state"] == "recorded", "Only a recorded image can be selected")
        page.update(selected_attempt_id=args.attempt_id, selection_confirmed=True,
                    selection_reason=args.reason.strip(), selected_at=now())
        save(work, task)
        return {"page": args.page, "selected_attempt_id": args.attempt_id,
                "selection_confirmed": True, "output": str(asset(work, attempt["output"]))}


def verify_pdf(path, expected):
    with fitz.open(str(path)) as pdf:
        require(len(pdf) == len(expected), "Assembly verification: page count mismatch")
        for page, item in zip(pdf, expected):
            dimensions = item["dimensions"]
            page_size = item.get("page_size") or LEGACY_PAGE_SIZE_POINTS
            require(abs(page.rect.width - page_size[0]) < 0.02
                    and abs(page.rect.height - page_size[1]) < 0.02,
                    "Assembly verification: page size changed")
            images = page.get_images(full=True)
            require(len(images) == 1 and list(images[0][2:4]) == dimensions,
                    "Assembly verification: embedded pixel dimensions changed")
            require(not page.get_text(), "Assembly verification: unexpected text layer")


@contextlib.contextmanager
def composition(args, work):
    # Resolve the explicitly requested chain, then lock every participating job in path order.
    with locked(work):
        base = checked(work)
        prior = (base.get("assemblies", [])[-1].get("overlay_work_dirs", [])
                 if getattr(args, "reuse_overlays", False) and base.get("assemblies") else [])
    overlay_paths = [Path(p).expanduser().resolve() for p in
                     list(prior) + list(getattr(args, "overlay_work_dir", []) or [])]
    require(work not in overlay_paths, "Base job cannot be its own overlay")
    with contextlib.ExitStack() as stack:
        for path in sorted(set([work] + overlay_paths), key=str):
            stack.enter_context(locked(path))
        task = checked(work)
        require(not unresolved(task), "Resolve all submitted requests before export")
        overlays = []
        for path in overlay_paths:
            update = checked(path)
            require(isinstance(update.get("authorization"), str) and update["authorization"].strip(),
                    "Overlay job requires a recorded explicit user authorization source")
            require(update["source"]["sha256"] == task["source"]["sha256"], "Overlay source PDF differs")
            require(set(update["selected_pages"]).issubset(task["selected_pages"]), "Overlay pages outside base selection")
            require(not unresolved(update), "Resolve all overlay requests before export")
            overlays.append((path, update))
        for path, source in [(work, task)] + overlays:
            for number, page in source["pages"].items():
                for attempt in page["attempt_records"]:
                    image = asset(path, attempt["output"])
                    require(not (attempt["state"] == "failed" and image.is_file()),
                            "Saved result requires record with original attempt ID " + attempt["attempt_id"]
                            + " for page " + number + " and image " + str(image) + " before export")
        yield task, overlays


def compose_pages(work, task, overlays, for_pdf, require_review=True):
    rows = []
    for number in task["selected_pages"]:
        base_page = page_record(task, number)
        image = selected_attempt(base_page)
        chosen = (work, task, base_page, image) if image else None
        note = "" if base_page["attempts"] else "本页尚未生成。"
        for path, update in overlays:
            if number not in update["selected_pages"]:
                continue
            page = page_record(update, number)
            candidate = selected_attempt(page)
            if candidate:
                chosen = (path, update, page, candidate)
                note = ""  # A later successful update supersedes earlier failure notes.
            else:
                note = "本次更新未生成，沿用原结果" if chosen else "本次更新未取得可用生成图。"
        if chosen:
            path, source, page, image = chosen
            require(len(available(page)) < 2 or page["selection_confirmed"],
                    "User must specify an unconfirmed historical version: page " + str(number))
            if require_review and (image.get("prompt") or not source.get("legacy_review_exempt")):
                require(image.get("review"), "Review the selected image before export: page " + str(number))
            rows.append({"source_page": number, "work_dir": str(path), "task_id": source["task_id"],
                         "attempt_id": image["attempt_id"], "image_sha256": image["output_sha256"],
                         "output": image["output"], "dimensions": image["output_dimensions"],
                         "page_size": source_page_size(source, number, page),
                         "review": image.get("review"), "update_note": note})
        else:
            rows.append({"source_page": number, "work_dir": None, "task_id": None,
                         "attempt_id": None, "image_sha256": None, "review": None,
                         "page_size": source_page_size(task, number, base_page),
                         "update_note": note or "本页未取得可用生成图。"})
    return rows


def report_bytes(rows):
    def cell(value):
        value = str(value).replace("\r\n", " ").replace("\r", " ").replace("\n", " ")
        return html.escape(value, quote=False).replace("\\", "\\\\").replace("|", "\\|")
    numbers = "、".join(str(row["source_page"]) for row in rows)
    lines = ["# 逐页检查说明", "", "范围：PDF 原页序第 " + numbers + " 页；检查版式、内容区域及可直接确认的文字问题。", "",
             "| 原页码 | 检查结果 | 位置与说明 |", "| --- | --- | --- |"]
    labels = {"pass": "未见明显问题", "issue": "发现问题", "unknown": "待确认"}
    for row in rows:
        review = row.get("review") or {}
        if row.get("attempt_id"):
            label = labels.get(review.get("status"), "待确认")
            observations = review.get("observations") or ["整页：未记录具体检查说明。"]
        else:
            label, observations = "未生成", []
        notes = list(observations)
        if row.get("update_note"):
            notes.append(row["update_note"])
        lines.append("| " + str(row["source_page"]) + " | " + label + " | " + cell("；".join(notes)) + " |")
    return ("\n".join(lines) + "\n").encode("utf-8")


def export_metadata(task, overlays, rows, target, kind):
    included = [row for row in rows if row.get("attempt_id")]
    mapping = [{"pdf_page": index + 1, "source_page": row["source_page"],
                "attempt_id": row["attempt_id"], "image_sha256": row["image_sha256"]}
               for index, row in enumerate(included)]
    return {"kind": kind, "path": str(target), "created_at": now(), "page_count": len(included),
            "mapping": mapping, "missing_pages": [row["source_page"] for row in rows if not row.get("attempt_id")],
            "overlay_work_dirs": [str(path) for path, _ in overlays], "page_sources": rows}


def check_export_target(work, task, target, suffix):
    require(target.suffix.lower() == suffix, "Output must have a " + suffix + " extension")
    require(target != Path(task["source"]["path"]), "Cannot overwrite source PDF")
    require(target not in (work / "task.json", work / ".task.lock"), "Output conflicts with task data")
    require(not any(root == target or root in target.parents for root in (work / "input", work / "output", work / "prompts")),
            "Export cannot be placed in asset directories")


def create_pdf(temporary, rows):
    with fitz.open() as pdf:
        for row in rows:
            if not row.get("attempt_id"):
                continue
            iw, ih = row["dimensions"]
            width, height = row.get("page_size") or LEGACY_PAGE_SIZE_POINTS
            scale = min(width / iw, height / ih)
            x, y = (width - iw * scale) / 2, (height - ih * scale) / 2
            page = pdf.new_page(width=width, height=height)
            page.draw_rect(page.rect, color=None, fill=(1, 1, 1))
            page.insert_image(fitz.Rect(x, y, x + iw * scale, y + ih * scale),
                              filename=str(asset(Path(row["work_dir"]), row["output"])))
        pdf.save(temporary, deflate=True)
    verify_pdf(temporary, [{"dimensions": row["dimensions"], "page_size": row.get("page_size")}
                          for row in rows if row.get("attempt_id")])
    with open(temporary, "rb") as stream:
        os.fsync(stream.fileno())


def publish_export(work, task, target, metadata, report_target):
    """Publish one report or a PDF/report pair; recover only ledger-owned exact bytes."""
    pending = task.setdefault("pending_assemblies", {})
    previous = pending.get(str(target))
    compatible = bool(previous and previous.get("path") == str(target) and previous.get("mapping") == metadata["mapping"]
                      and previous.get("missing_pages") == metadata["missing_pages"]
                      and previous.get("overlay_work_dirs", []) == metadata["overlay_work_dirs"]
                      and previous.get("page_count") == metadata["page_count"]
                      and previous.get("kind", "assembly") == metadata["kind"])
    if target.exists() or (report_target != target and report_target.exists()):
        require(compatible, "Output already exists without a matching pending export")
    if compatible and previous.get("page_sources"):
        metadata["page_sources"] = previous["page_sources"]
    data = report_bytes(metadata["page_sources"])
    report_hash = hashlib.sha256(data).hexdigest()
    temporary = None
    try:
        if metadata["kind"] == "assembly":
            if target.exists():
                require(digest(target) == previous.get("sha256"), "Existing PDF differs from pending export")
                metadata["sha256"] = previous["sha256"]
                verify_pdf(target, [{"dimensions": r["dimensions"], "page_size": r.get("page_size")}
                                    for r in metadata["page_sources"] if r.get("attempt_id")])
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                fd, temporary = tempfile.mkstemp(prefix=".assembly-", suffix=".pdf", dir=str(target.parent))
                os.close(fd)
                create_pdf(temporary, metadata["page_sources"])
                metadata["sha256"] = digest(Path(temporary))
            metadata.update(report_path=str(report_target), report_sha256=report_hash)
            if report_target.exists():
                require(previous.get("report_path") == str(report_target)
                        and previous.get("report_sha256") == report_hash
                        and digest(report_target) == report_hash, "Existing check report differs from pending export")
        else:
            metadata["sha256"] = report_hash
            if target.exists():
                require(previous.get("sha256") == report_hash and digest(target) == report_hash,
                        "Existing check report differs from pending export")
        pending[str(target)] = metadata
        save(work, task)  # Ownership and both hashes are durable before either publication.
        if temporary:
            _publish_without_replace(temporary, target)
        if not report_target.exists():
            report_target.parent.mkdir(parents=True, exist_ok=True)
            atomic_bytes(report_target, data, replace=False)
        require(digest(target) == metadata["sha256"], "Published output differs from pending export")
        require(digest(report_target) == report_hash, "Published check report differs from pending export")
        _sync_directory(target.parent)
        history = "assemblies" if metadata["kind"] == "assembly" else "reports"
        task.setdefault(history, []).append(metadata)
        pending.pop(str(target))
        save(work, task)
        return bool(previous)
    finally:
        if temporary and os.path.exists(temporary):
            os.unlink(temporary)


def publish_pdf(work, task, target, metadata):
    """Publish only the assembled PDF without creating a review sidecar."""
    pending = task.setdefault("pending_assemblies", {})
    previous = pending.get(str(target))
    compatible = bool(previous and previous.get("path") == str(target)
                      and previous.get("mapping") == metadata["mapping"]
                      and previous.get("missing_pages") == metadata["missing_pages"]
                      and previous.get("overlay_work_dirs", []) == metadata["overlay_work_dirs"]
                      and previous.get("page_count") == metadata["page_count"]
                      and previous.get("kind", "assembly") == "assembly")
    if target.exists():
        require(compatible, "Output already exists without a matching pending export")
    if compatible and previous.get("page_sources"):
        metadata["page_sources"] = previous["page_sources"]
    temporary = None
    try:
        if target.exists():
            require(digest(target) == previous.get("sha256"), "Existing PDF differs from pending export")
            metadata["sha256"] = previous["sha256"]
            verify_pdf(target, [{"dimensions": r["dimensions"], "page_size": r.get("page_size")}
                                for r in metadata["page_sources"] if r.get("attempt_id")])
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            fd, temporary = tempfile.mkstemp(prefix=".assembly-", suffix=".pdf", dir=str(target.parent))
            os.close(fd)
            create_pdf(temporary, metadata["page_sources"])
            metadata["sha256"] = digest(Path(temporary))
        pending[str(target)] = metadata
        save(work, task)
        if temporary:
            _publish_without_replace(temporary, target)
        require(digest(target) == metadata["sha256"], "Published output differs from pending export")
        _sync_directory(target.parent)
        task.setdefault("assemblies", []).append(metadata)
        pending.pop(str(target))
        save(work, task)
        return bool(previous)
    finally:
        if temporary and os.path.exists(temporary):
            os.unlink(temporary)


def assemble(args, work):
    with composition(args, work) as (task, overlays):
        pdf_only = getattr(args, "pdf_only", False)
        rows = compose_pages(work, task, overlays, for_pdf=True, require_review=not pdf_only)
        included = [r for r in rows if r.get("attempt_id")]
        missing = [r["source_page"] for r in rows if not r.get("attempt_id")]
        require(not missing or args.allow_partial, "Missing pages: " + ",".join(map(str, missing)))
        require(included, "No generated pages available")
        target = Path(args.output).expanduser().resolve()
        if missing and not re.search(r"(?:^|[-_. ])partial(?:$|[-_. ])", target.stem, re.IGNORECASE):
            target = target.with_name(target.stem + "-partial" + target.suffix)
        check_export_target(work, task, target, ".pdf")
        if getattr(args, "a4", False):
            for row in rows:
                row["page_size"] = list(A4_PAGE_SIZE_POINTS)
        metadata = export_metadata(task, overlays, rows, target, "assembly")
        if pdf_only:
            recovered = publish_pdf(work, task, target, metadata)
            return {"output": str(target), "pages": len(included),
                    "mapping": metadata["mapping"], "missing_pages": missing, "recovered": recovered}
        report_target = target.with_name(target.stem + "_逐页检查说明.md")
        check_export_target(work, task, report_target, ".md")
        recovered = publish_export(work, task, target, metadata, report_target)
        return {"output": str(target), "report": str(report_target), "pages": len(included),
                "mapping": metadata["mapping"], "missing_pages": missing, "recovered": recovered}


def report(args, work):
    with composition(args, work) as (task, overlays):
        rows = compose_pages(work, task, overlays, for_pdf=False)
        target = Path(args.output).expanduser().resolve()
        check_export_target(work, task, target, ".md")
        metadata = export_metadata(task, overlays, rows, target, "report")
        recovered = publish_export(work, task, target, metadata, target)
        return {"output": str(target), "report": str(target), "rows": len(rows), "recovered": recovered}


def main():
    parser = Parser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("prepare", "status", "reserve", "record", "fail", "review", "select", "assemble", "report"):
        command = commands.add_parser(name)
        command.add_argument("--work-dir", required=True)
        if name == "prepare":
            command.add_argument("--pdf", required=True)
            command.add_argument("--pages", required=True)
            command.add_argument("--dpi", type=int, default=240)
            command.add_argument("--authorization")
        elif name in ("reserve", "record", "fail", "review", "select"):
            command.add_argument("--page", type=int, required=True)
            if name == "reserve":
                command.add_argument("--purpose", choices=("initial",), default="initial")
                command.add_argument("--prompt-file", required=True)
            else:
                command.add_argument("--attempt-id", required=True)
            if name == "record":
                command.add_argument("--image", required=True)
            elif name in ("fail", "select"):
                command.add_argument("--reason", required=True)
            elif name == "review":
                command.add_argument("--review-file", required=True)
        elif name in ("assemble", "report"):
            command.add_argument("--output", required=True)
            command.add_argument("--overlay-work-dir", action="append", default=[])
            command.add_argument("--reuse-overlays", action="store_true")
            if name == "assemble":
                command.add_argument("--allow-partial", action="store_true")
                command.add_argument("--pdf-only", action="store_true")
                command.add_argument("--a4", action="store_true",
                                    help="适用用户明确要求时，将所有输出页统一为 A4")
    args = parser.parse_args()
    work = Path(args.work_dir).expanduser().resolve()
    if args.command == "status":
        with locked(work):
            result = overview(work, checked(work))
    else:
        result = globals()[args.command](args, work)
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(json.dumps({"error": type(exc).__name__, "message": str(exc)}, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)
