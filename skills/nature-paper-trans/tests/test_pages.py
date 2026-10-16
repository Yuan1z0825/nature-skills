#!/usr/bin/env python3
"""Exercise isolated page jobs with temporary PDFs/PNGs; never call image generation."""

from concurrent.futures import ThreadPoolExecutor
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock
import uuid

import fitz
from PIL import Image

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "pages.py"


class PagesTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="nature-paper-trans-tests-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.job = self.root / "job"
        self.source = self.root / "source.pdf"
        self.prompt = self.root / "prompt.md"
        self.prompt.write_text("Translate the supplied source page into Chinese.\n", encoding="utf-8")
        self.red = self.image("red.png", (240, 10, 20))
        self.blue = self.image("blue.png", (20, 40, 240))
        self.green = self.image("green.png", (20, 200, 40))

    def image(self, name, color):
        path = self.root / name
        Image.new("RGB", (32, 48), color).save(path)
        return path

    def invoke(self, command, *arguments):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), command, "--work-dir", str(self.job), *map(str, arguments)],
            text=True, capture_output=True, timeout=30,
        )
        raw = result.stdout if result.returncode == 0 else result.stderr
        try:
            value = json.loads(raw)
        except json.JSONDecodeError:
            self.fail("Non-JSON CLI result: " + repr(result))
        return result.returncode, value

    def ok(self, command, *arguments):
        code, value = self.invoke(command, *arguments)
        self.assertEqual(code, 0, value)
        return value

    def rejected(self, command, *arguments):
        code, value = self.invoke(command, *arguments)
        self.assertNotEqual(code, 0, value)
        return value

    def source_pdf(self, count, sizes=None):
        with fitz.open() as pdf:
            for number in range(1, count + 1):
                width, height = (sizes or [(80, 100)] * count)[number - 1]
                page = pdf.new_page(width=width, height=height)
                page.insert_text((8, 20), "Page %d" % number, fontsize=8)
            pdf.save(self.source)

    def prepare(self, count=1, selection="all"):
        self.source_pdf(count)
        return self.ok("prepare", "--pdf", self.source, "--pages", selection, "--dpi", 72)

    def reserve(self, page=1):
        return self.ok("reserve", "--page", page, "--prompt-file", self.prompt)["attempt_id"]

    def reject_reservation(self, page=1):
        return self.rejected("reserve", "--page", page, "--prompt-file", self.prompt)

    def record(self, page, attempt, image=None):
        return self.ok("record", "--page", page, "--attempt-id", attempt, "--image", image or self.red)

    def fail_attempt(self, page, attempt):
        return self.ok("fail", "--page", page, "--attempt-id", attempt,
                       "--reason", "Explicit tool failure; no result was returned")

    def review(self, page, attempt, status="pass", observations=None):
        value = {"status": status, "observations": observations or ["Source content regions remain readable"]}
        path = self.root / ("review-" + str(uuid.uuid4()) + ".json")
        path.write_text(json.dumps(value), encoding="utf-8")
        return self.ok("review", "--page", page, "--attempt-id", attempt, "--review-file", path)

    def first_result(self, page=1, status="pass", observations=None, image=None):
        attempt = self.reserve(page)
        self.record(page, attempt, image)
        self.review(page, attempt, status, observations)
        return attempt

    def page_module(self):
        spec = importlib.util.spec_from_file_location("nature_paper_trans_pages_under_test", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def assembly_args(self, target):
        return SimpleNamespace(output=str(target), allow_partial=False,
                               overlay_work_dir=[], reuse_overlays=False)

    def report_rows(self, path):
        text = Path(path).read_text(encoding="utf-8")
        rows = [line for line in text.splitlines() if re.match(r"^\|\s*\d+\s*\|", line)]
        return text, rows

    def assert_pdf(self, path, colors, page_sizes=None):
        page_sizes = page_sizes or [(80, 100)] * len(colors)
        with fitz.open(path) as pdf:
            self.assertEqual(len(pdf), len(colors))
            for page, color, page_size in zip(pdf, colors, page_sizes):
                self.assertAlmostEqual(page.rect.width, page_size[0], places=2)
                self.assertAlmostEqual(page.rect.height, page_size[1], places=2)
                self.assertEqual(page.get_text(), "")
                images = page.get_images(full=True)
                self.assertEqual(len(images), 1)
                self.assertEqual(tuple(images[0][2:4]), (32, 48))
                with Image.open(io.BytesIO(pdf.extract_image(images[0][0])["image"])) as image:
                    self.assertEqual(image.convert("RGB").getpixel((16, 24)), color)

    def test_ten_inflight_reservations_are_atomic(self):
        prepared = self.prepare(12)
        self.assertEqual(prepared["policy"]["max_attempts_per_page"], 1)
        def reserve_one(page):
            return self.invoke("reserve", "--page", page, "--prompt-file", self.prompt)
        with ThreadPoolExecutor(max_workers=12) as pool:
            results = list(pool.map(reserve_one, range(1, 13)))
        accepted = [value for code, value in results if code == 0]
        self.assertEqual(len(accepted), 10, results)
        self.assertEqual(len({value["attempt_id"] for value in accepted}), 10)
        self.fail_attempt(accepted[0]["page"], accepted[0]["attempt_id"])
        self.reserve(next(page for page, (code, _) in enumerate(results, 1) if code))

    def test_same_page_concurrent_reservation_spends_only_one_attempt(self):
        self.prepare()
        def reserve_one(_):
            return self.invoke("reserve", "--page", 1, "--prompt-file", self.prompt)
        with ThreadPoolExecutor(max_workers=4) as pool:
            results = list(pool.map(reserve_one, range(4)))
        self.assertEqual(sum(code == 0 for code, _ in results), 1, results)

    def test_missing_prompt_cannot_spend_an_attempt(self):
        self.prepare()
        self.rejected("reserve", "--page", 1)
        self.rejected("reserve", "--page", 1, "--prompt-file", self.root / "missing.md")
        self.reserve()

    def test_prompt_snapshot_survives_source_edits_and_detects_tampering(self):
        self.prepare()
        original = self.prompt.read_bytes()
        result = self.ok("reserve", "--page", 1, "--prompt-file", self.prompt)
        snapshot = Path(result["prompt"])
        self.assertEqual(snapshot.read_bytes(), original)
        self.prompt.write_text("A revised prompt for a future invocation.\n", encoding="utf-8")
        self.record(1, result["attempt_id"])
        self.review(1, result["attempt_id"])
        self.assertEqual(snapshot.read_bytes(), original)
        snapshot.write_text("An accidental change to the immutable snapshot.\n", encoding="utf-8")
        self.rejected("assemble", "--output", self.root / "tampered.pdf")

    def test_unknown_and_failed_calls_cannot_retry_even_after_prepare(self):
        self.prepare()
        attempt = self.reserve()
        self.reject_reservation()
        self.fail_attempt(1, attempt)
        self.reject_reservation()
        self.rejected("reserve", "--page", 1, "--purpose", "recovery", "--prompt-file", self.prompt,
                      "--reason", "A failure does not authorize a second call")
        self.ok("prepare", "--pdf", self.source, "--pages", "all", "--dpi", 72)
        self.reject_reservation()
        self.assertEqual(self.ok("status")["total_attempts"], 1)

    def test_confirmed_material_issue_does_not_authorize_a_second_call(self):
        self.prepare()
        self.first_result(status="issue", observations=["The right column omits an entire results paragraph"])
        self.reject_reservation()
        self.rejected("reserve", "--page", 1, "--purpose", "repair", "--prompt-file", self.prompt)
        self.assertEqual(self.ok("status")["total_attempts"], 1)

    def test_old_v2_two_call_policy_cannot_grant_another_call(self):
        for state in ("recorded", "failed"):
            with self.subTest(state=state):
                self.job = self.root / ("old-v2-" + state)
                self.source = self.root / ("source-" + state + ".pdf")
                self.legacy_v2_job(states=(state,), selected=1 if state == "recorded" else None)
                self.reject_reservation()
                self.assertEqual(self.ok("status")["total_attempts"], 1)

    def test_records_are_idempotent_and_cannot_replace_an_attempt(self):
        self.prepare()
        attempt = self.reserve()
        self.rejected("record", "--page", 1, "--attempt-id", "wrong-id", "--image", self.red)
        self.record(1, attempt)
        self.record(1, attempt)
        self.rejected("record", "--page", 1, "--attempt-id", attempt, "--image", self.blue)
        self.rejected("fail", "--page", 1, "--attempt-id", attempt, "--reason", "Cannot discard a result")

    def test_interrupted_record_image_is_reported_and_recovered_by_original_id(self):
        for state in ("reserved", "failed"):
            with self.subTest(state=state):
                self.job = self.root / ("interrupted-" + state)
                self.source = self.root / ("interrupted-" + state + ".pdf")
                self.prepare()
                attempt = self.reserve()
                if state == "failed":
                    self.fail_attempt(1, attempt)
                pending = self.ok("status")["pages"][0]["attempt_records"][0]
                self.assertIsNone(pending["output"])
                self.assertNotIn("recoverable_output", pending)
                task = json.loads((self.job / "task.json").read_text(encoding="utf-8"))
                saved = self.job / task["pages"]["1"]["attempt_records"][0]["output"]
                saved.write_bytes(self.red.read_bytes())
                pending = self.ok("status")["pages"][0]["attempt_records"][0]
                self.assertIsNone(pending["output"])
                self.assertEqual(pending["recoverable_output"], str(saved.resolve()))
                if state == "reserved":
                    self.rejected("fail", "--page", 1, "--attempt-id", attempt, "--reason", "Manifest save interrupted")
                self.reject_reservation()
                target = self.root / ("recovered-" + state + ".pdf")
                report = self.root / ("unrecorded-" + state + ".md")
                for command, destination in (("assemble", target), ("report", report)):
                    rejection = self.rejected(command, "--output", destination)
                    self.assertFalse(destination.exists())
                    if state == "failed":
                        self.assertIn("record", rejection["message"])
                self.record(1, attempt, saved)
                self.review(1, attempt)
                result = self.ok("assemble", "--output", target)
                self.assert_pdf(result["output"], [(240, 10, 20)])
                self.assertTrue(Path(result["report"]).is_file())
                self.assertEqual(self.ok("status")["total_attempts"], 1)

    def test_unknown_attempt_blocks_even_partial_assembly(self):
        self.prepare(2)
        self.first_result(1)
        pending = self.reserve(2)
        target = self.root / "partial.pdf"
        self.rejected("assemble", "--output", target, "--allow-partial")
        self.fail_attempt(2, pending)
        result = self.ok("assemble", "--output", target, "--allow-partial")
        self.assertEqual(result["missing_pages"], [2])
        self.assertEqual([(item["pdf_page"], item["source_page"]) for item in result["mapping"]], [(1, 1)])

    def test_a4_assembly_preserves_source_order_and_publishes_a_report(self):
        self.prepare(3, "3,1")
        third = self.first_result(3, image=self.blue)
        first = self.first_result(1, image=self.red)
        target = self.root / "ordered.pdf"
        result = self.ok("assemble", "--output", target)
        self.assertEqual([(item["pdf_page"], item["source_page"], item["attempt_id"])
                          for item in result["mapping"]], [(1, 1, first), (2, 3, third)])
        self.assert_pdf(target, [(240, 10, 20), (20, 40, 240)])
        _, rows = self.report_rows(result["report"])
        self.assertEqual([int(re.match(r"^\|\s*(\d+)", row).group(1)) for row in rows], [1, 3])
        original = {path: Path(path).read_bytes() for path in (result["output"], result["report"])}
        self.rejected("assemble", "--output", target)
        self.assertEqual({path: Path(path).read_bytes() for path in original}, original)

    def test_pdf_only_assembly_skips_review_and_report(self):
        self.prepare()
        attempt = self.reserve()
        self.record(1, attempt, self.red)
        target = self.root / "pdf-only.pdf"
        result = self.ok("assemble", "--output", target, "--pdf-only")
        self.assertEqual(result["output"], str(target.resolve()))
        self.assertNotIn("report", result)
        self.assertTrue(target.is_file())
        self.assertFalse(target.with_name(target.stem + "_逐页检查说明.md").exists())
        self.assert_pdf(target, [(240, 10, 20)])

    def test_assembly_preserves_mixed_source_page_sizes(self):
        self.source_pdf(2, sizes=[(80, 100), (140, 70)])
        self.ok("prepare", "--pdf", self.source, "--pages", "all", "--dpi", 72)
        first = self.reserve(1)
        self.record(1, first, self.red)
        second = self.reserve(2)
        self.record(2, second, self.blue)
        target = self.root / "mixed-sizes.pdf"
        result = self.ok("assemble", "--output", target, "--pdf-only")
        self.assert_pdf(target, [(240, 10, 20), (20, 40, 240)], [(80, 100), (140, 70)])

    def test_explicit_a4_option_converts_all_pages(self):
        self.prepare()
        attempt = self.reserve()
        self.record(1, attempt, self.red)
        target = self.root / "a4.pdf"
        self.ok("assemble", "--output", target, "--pdf-only", "--a4")
        self.assert_pdf(target, [(240, 10, 20)], [(210 * 72 / 25.4, 297 * 72 / 25.4)])

    def test_report_has_all_four_page_outcomes_and_escapes_table_content(self):
        self.prepare(4)
        self.first_result(1, observations=["PASS_LOCATION"])
        self.first_result(2, status="issue", observations=["ISSUE_LOCATION A|B <script>bad</script>\n| 99 | injected | row |"])
        self.first_result(3, status="unknown", observations=["UNKNOWN_LOCATION small formula cannot be read"])
        self.fail_attempt(4, self.reserve(4))
        result = self.ok("assemble", "--output", self.root / "outcomes.pdf", "--allow-partial")
        text, rows = self.report_rows(result["report"])
        self.assertEqual(len(rows), 4)
        for row, outcome in zip(rows, ("未见明显问题", "发现问题", "待确认", "未生成")):
            self.assertIn(outcome, row)
        self.assertIn("ISSUE_LOCATION", rows[1])
        self.assertNotIn("<script>", text)
        for row in rows:
            separators, escaped = 0, False
            for char in row:
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == "|":
                    separators += 1
            self.assertEqual(separators, 4, row)

    def test_all_failed_pages_produce_only_a_complete_missing_page_report(self):
        self.prepare(2)
        for page in (1, 2):
            self.fail_attempt(page, self.reserve(page))
        target = self.root / "no-images.pdf"
        self.rejected("assemble", "--output", target, "--allow-partial")
        self.assertFalse(target.exists())
        report = self.root / "all-failed.md"
        self.ok("report", "--output", report)
        _, rows = self.report_rows(report)
        self.assertEqual(len(rows), 2)
        self.assertTrue(all("未生成" in row for row in rows))

    def test_standalone_report_requires_a_review_of_the_new_image(self):
        self.prepare()
        attempt = self.reserve()
        self.record(1, attempt)
        target = self.root / "review-gated.md"
        self.rejected("report", "--output", target)
        self.assertFalse(target.exists())
        self.review(1, attempt, "issue", ["The figure caption is incomplete"])
        self.ok("report", "--output", target)
        _, rows = self.report_rows(target)
        self.assertEqual(len(rows), 1)
        self.assertIn("发现问题", rows[0])

    def test_historical_selection_drives_both_pdf_and_report(self):
        self.legacy_v2_job()
        result = self.ok("assemble", "--output", self.root / "historical.pdf")
        self.assert_pdf(result["output"], [(20, 40, 240)])
        text, rows = self.report_rows(result["report"])
        self.assertEqual(len(rows), 1)
        self.assertIn("SECOND_PASS", text)
        self.assertNotIn("FIRST_ISSUE", text)
        self.assertIn("未见明显问题", rows[0])
        self.reject_reservation()

    def test_unconfirmed_historical_choice_requires_explicit_selection(self):
        attempts = self.legacy_v2_job(selected=1, confirmed=False)
        target = self.root / "chosen-history.pdf"
        self.rejected("assemble", "--output", target)
        self.rejected("report", "--output", self.root / "unchosen-history.md")
        self.ok("select", "--page", 1, "--attempt-id", attempts[1], "--reason", "The user explicitly chose the second historical image")
        result = self.ok("assemble", "--output", target)
        self.assert_pdf(result["output"], [(20, 40, 240)])

    def test_late_historical_result_preserves_the_already_selected_image(self):
        attempts = self.legacy_v2_job(states=("failed", "recorded"), selected=2)
        self.record(1, attempts[0], self.red)
        self.review(1, attempts[0], "issue", ["LATE_FIRST_ISSUE"])
        self.assertEqual(self.ok("status")["pages"][0]["selected_attempt_id"], attempts[1])
        result = self.ok("assemble", "--output", self.root / "late-history.pdf")
        self.assert_pdf(result["output"], [(20, 40, 240)])
        text, _ = self.report_rows(result["report"])
        self.assertIn("SECOND_PASS", text)
        self.assertNotIn("LATE_FIRST_ISSUE", text)

    def test_pdf_and_report_recover_after_final_ledger_save_fails(self):
        self.prepare()
        self.first_result()
        module = self.page_module()
        target = self.root / "published-before-ledger.pdf"
        report = target.with_name(target.stem + "_逐页检查说明.md")
        real_save = module.save
        def fail_after_publication(work, task):
            if target.exists() and report.exists():
                raise OSError("Interrupted after publishing both files, before recording completion")
            return real_save(work, task)
        with mock.patch.object(module, "save", side_effect=fail_after_publication):
            with self.assertRaises(OSError):
                module.assemble(self.assembly_args(target), self.job)
        original = {path: path.read_bytes() for path in (target, report)}
        self.ok("assemble", "--output", self.root / "another-output.pdf")
        self.ok("assemble", "--output", target)
        self.assertEqual({path: path.read_bytes() for path in original}, original)
        self.rejected("assemble", "--output", target)

    def test_pair_publication_recovers_a_missing_report_without_changing_pdf(self):
        self.prepare()
        self.first_result()
        module = self.page_module()
        target = self.root / "partial-pair.pdf"
        report = target.with_name(target.stem + "_逐页检查说明.md")
        real_publish = module._publish_without_replace
        def fail_report_publication(source, destination):
            if Path(destination) == report:
                raise OSError("Interrupted before publishing the report")
            return real_publish(source, destination)
        with mock.patch.object(module, "_publish_without_replace", side_effect=fail_report_publication):
            with self.assertRaises(OSError):
                module.assemble(self.assembly_args(target), self.job)
        self.assertTrue(target.exists())
        self.assertFalse(report.exists())
        before = target.read_bytes()
        result = self.ok("assemble", "--output", target)
        self.assertEqual(target.read_bytes(), before)
        self.assertTrue(Path(result["report"]).is_file())

    def test_pair_publication_rebuilds_missing_files_and_rejects_foreign_or_tampered_files(self):
        for state in ("missing", "foreign-pdf", "tampered-report"):
            with self.subTest(state=state):
                self.job = self.root / ("pair-job-" + state)
                self.source = self.root / ("pair-source-" + state + ".pdf")
                self.prepare()
                self.first_result()
                module = self.page_module()
                target = self.root / ("pair-" + state + ".pdf")
                report = target.with_name(target.stem + "_逐页检查说明.md")
                def fail_publication(source, destination):
                    raise OSError("Interrupted before publication")
                with mock.patch.object(module, "_publish_without_replace", side_effect=fail_publication):
                    with self.assertRaises(OSError):
                        module.assemble(self.assembly_args(target), self.job)
                self.assertFalse(target.exists())
                self.assertFalse(report.exists())
                if state == "missing":
                    result = self.ok("assemble", "--output", target)
                    self.assert_pdf(result["output"], [(240, 10, 20)])
                    self.assertTrue(Path(result["report"]).is_file())
                else:
                    occupied = target if state == "foreign-pdf" else report
                    content = self.source.read_bytes() if state == "foreign-pdf" else b"Changed report contents\n"
                    occupied.write_bytes(content)
                    self.rejected("assemble", "--output", target)
                    self.assertEqual(occupied.read_bytes(), content)

    def prepare_overlay(self, name, pages, authorization="The user explicitly requested these source pages again", source=None):
        base = self.job
        self.job = self.root / name
        args = ["--pdf", source or self.source, "--pages", pages, "--dpi", 72]
        if authorization is not None:
            args += ["--authorization", authorization]
        self.ok("prepare", *args)
        return base

    def test_authorized_selected_page_update_merges_without_regenerating_other_pages(self):
        self.prepare(3)
        for page, image in ((1, self.red), (2, self.green), (3, self.blue)):
            self.first_result(page, image=image, observations=["BASE_PAGE_%d" % page])
        base = self.prepare_overlay("page-two-update", "2")
        overlay = self.job
        replacement = self.image("replacement.png", (180, 20, 180))
        self.first_result(2, image=replacement, status="issue", observations=["UPDATED_PAGE_TWO_ISSUE"])
        self.assertEqual(self.ok("status")["total_attempts"], 1)
        self.job = base
        result = self.ok("assemble", "--output", self.root / "updated.pdf", "--overlay-work-dir", overlay)
        self.assert_pdf(result["output"], [(240, 10, 20), (180, 20, 180), (20, 40, 240)])
        text, rows = self.report_rows(result["report"])
        self.assertEqual(len(rows), 3)
        self.assertIn("UPDATED_PAGE_TWO_ISSUE", rows[1])
        self.assertNotIn("BASE_PAGE_2", text)
        self.assertEqual(self.ok("status")["total_attempts"], 3)
        base = self.prepare_overlay("page-three-failed-update", "3")
        failed_overlay = self.job
        self.fail_attempt(3, self.reserve(3))
        self.job = base
        retained = self.ok("assemble", "--output", self.root / "retained.pdf", "--reuse-overlays",
                           "--overlay-work-dir", failed_overlay)
        self.assert_pdf(retained["output"], [(240, 10, 20), (180, 20, 180), (20, 40, 240)])
        _, retained_rows = self.report_rows(retained["report"])
        self.assertIn("UPDATED_PAGE_TWO_ISSUE", retained_rows[1])
        self.assertIn("BASE_PAGE_3", retained_rows[2])
        self.assertEqual(retained_rows[2].split("|")[2].strip(), "未见明显问题")
        task = json.loads((self.job / "task.json").read_text(encoding="utf-8"))
        note = next(page["update_note"] for page in task["assemblies"][-1]["page_sources"]
                    if page["source_page"] == 3)
        self.assertTrue(note)
        self.assertIn(note, retained_rows[2])
        base = self.prepare_overlay("page-three-successful-update", "3")
        latest_overlay = self.job
        self.first_result(3, image=self.green, observations=["LATEST_PAGE_THREE"])
        self.job = base
        latest = self.ok("assemble", "--output", self.root / "latest.pdf", "--reuse-overlays",
                         "--overlay-work-dir", latest_overlay)
        self.assert_pdf(latest["output"], [(240, 10, 20), (180, 20, 180), (20, 200, 40)])
        _, latest_rows = self.report_rows(latest["report"])
        self.assertIn("LATEST_PAGE_THREE", latest_rows[2])
        self.assertNotIn(note, latest_rows[2])
        self.assertEqual(self.ok("status")["total_attempts"], 3)

    def test_overlay_requires_authorization_matching_source_and_selected_page_scope(self):
        self.prepare(3, "1-2")
        for page in (1, 2):
            self.first_result(page)
        base, original_source = self.job, self.source
        for problem in ("authorization", "source", "scope"):
            with self.subTest(problem=problem):
                self.job = base
                source = original_source
                if problem == "source":
                    source = self.root / "different-source.pdf"
                    with fitz.open() as pdf:
                        for _ in range(3):
                            pdf.new_page(width=90, height=110)
                        pdf.save(source)
                self.prepare_overlay("invalid-overlay-" + problem, "3" if problem == "scope" else "2",
                                     authorization=None if problem == "authorization" else "User requested regeneration",
                                     source=source)
                overlay = self.job
                self.first_result(3 if problem == "scope" else 2, image=self.blue)
                self.job = base
                target = self.root / ("invalid-" + problem + ".pdf")
                self.rejected("assemble", "--output", target, "--overlay-work-dir", overlay)
                self.assertFalse(target.exists())
        self.assertEqual(self.ok("status")["total_attempts"], 2)

    def legacy_job(self, count=6):
        self.source_pdf(count)
        (self.job / "input").mkdir(parents=True)
        (self.job / "output").mkdir()
        pages = {}
        for number in range(1, count + 1):
            relative = "input/page-%04d.png" % number
            target = self.job / relative
            Image.new("RGB", (80, 100), "white").save(target)
            pages[str(number)] = {"state": "pending", "attempts": 0, "input": relative,
                                  "input_sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
                                  "input_dimensions": [80, 100], "output": "output/page-%04d.png" % number}
        task = {"version": 1, "task_id": str(uuid.uuid4()), "created_at": "2026-01-01T00:00:00+00:00",
                "source": {"path": str(self.source), "sha256": hashlib.sha256(self.source.read_bytes()).hexdigest(),
                           "page_count": count}, "dpi": 72, "selected_pages": list(range(1, count + 1)),
                "pages": pages, "assemblies": []}
        (self.job / "task.json").write_text(json.dumps(task), encoding="utf-8")

    def legacy_v2_job(self, states=("recorded", "recorded"), selected=2, confirmed=True):
        self.legacy_job(1)
        manifest = self.job / "task.json"
        task = json.loads(manifest.read_text(encoding="utf-8"))
        old = task["pages"]["1"]
        (self.job / "prompts").mkdir()
        records = []
        for index, state in enumerate(states, 1):
            identifier = "historical-attempt-%d" % index
            prompt = "prompts/%s.md" % identifier
            (self.job / prompt).write_bytes(self.prompt.read_bytes())
            output = "output/page-0001-attempt-%d.png" % index
            record = {"attempt_id": identifier, "attempt_number": index,
                      "purpose": "initial" if index == 1 else "repair", "state": state,
                      "reserved_at": "2026-01-01T00:00:00+00:00", "prompt": prompt,
                      "prompt_sha256": hashlib.sha256(self.prompt.read_bytes()).hexdigest(), "output": output}
            if state == "recorded":
                image = self.red if index == 1 else self.blue
                (self.job / output).write_bytes(image.read_bytes())
                record.update(output_sha256=hashlib.sha256(image.read_bytes()).hexdigest(),
                              output_dimensions=[32, 48], review={"status": "issue" if index == 1 else "pass",
                              "severity": "material" if index == 1 else "none", "retry_eligible": False,
                              "observations": ["FIRST_ISSUE" if index == 1 else "SECOND_PASS"]})
            records.append(record)
        task.update(version=2, policy={"max_in_flight": 10, "max_attempts_per_page": 2}, legacy_review_exempt=False)
        task["pages"]["1"] = {key: old[key] for key in ("input", "input_sha256", "input_dimensions")}
        task["pages"]["1"].update(attempts=len(records), attempt_records=records,
                                  selected_attempt_id=records[selected - 1]["attempt_id"] if selected else None,
                                  selection_confirmed=confirmed)
        manifest.write_text(json.dumps(task), encoding="utf-8")
        return [record["attempt_id"] for record in records]

    def test_v1_migration_preserves_existing_budget_and_inflight_limit(self):
        self.legacy_job()
        self.ok("status")
        attempts = [self.reserve(page) for page in range(1, 6)]
        self.reject_reservation(6)
        self.fail_attempt(1, attempts[0])
        self.reject_reservation(1)
        self.reserve(6)
        self.ok("prepare", "--pdf", self.source, "--pages", "all", "--dpi", 72)
        self.reject_reservation(1)

    def test_v1_pending_page_new_result_requires_review_after_migration(self):
        self.legacy_job(1)
        attempt = self.reserve()
        self.record(1, attempt)
        target = self.root / "new-legacy-result.pdf"
        self.rejected("assemble", "--output", target)
        self.review(1, attempt)
        result = self.ok("assemble", "--output", target)
        self.assert_pdf(result["output"], [(240, 10, 20)])

    def test_v1_existing_results_and_unresolved_calls_survive_migration(self):
        self.legacy_job(3)
        manifest = self.job / "task.json"
        task = json.loads(manifest.read_text(encoding="utf-8"))
        output = self.job / task["pages"]["1"]["output"]
        output.write_bytes(self.red.read_bytes())
        task["pages"]["1"].update(state="recorded", attempts=1,
                                  output_sha256=hashlib.sha256(output.read_bytes()).hexdigest(), output_dimensions=[32, 48])
        task["pages"]["2"].update(state="reserved", attempts=1, attempt_id="old-pending")
        task["pages"]["3"].update(state="failed", attempts=1, failure_reason="Original failure")
        manifest.write_text(json.dumps(task), encoding="utf-8")
        before = manifest.read_bytes()
        self.ok("status")
        self.assertEqual(manifest.read_bytes(), before)
        self.reject_reservation(2)
        self.record(2, "old-pending", self.blue)
        result = self.ok("assemble", "--output", self.root / "legacy-partial.pdf", "--allow-partial")
        self.assertEqual(result["missing_pages"], [3])
        self.assert_pdf(result["output"], [(240, 10, 20), (20, 40, 240)])
        _, rows = self.report_rows(result["report"])
        self.assertEqual(len(rows), 3)
        self.assertIn("待确认", rows[0])
        self.assertIn("待确认", rows[1])
        self.assertIn("未生成", rows[2])
        standalone = self.root / "legacy-status.md"
        self.ok("report", "--output", standalone)
        _, standalone_rows = self.report_rows(standalone)
        self.assertEqual(len(standalone_rows), 3)
        self.assertIn("待确认", standalone_rows[0])
        self.assertIn("待确认", standalone_rows[1])
        self.ok("prepare", "--pdf", self.source, "--pages", "all", "--dpi", 72)
        for page in (1, 2, 3):
            self.reject_reservation(page)


if __name__ == "__main__":
    unittest.main()
