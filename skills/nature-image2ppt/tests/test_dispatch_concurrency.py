import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNTIME_DIR = ROOT / "cli/image2ppt/runtime"


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


class DispatchConcurrencyTest(unittest.TestCase):
    def test_page_status_uses_default_capacity_of_six(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp)
            write_json(
                run_dir / "page_jobs.json",
                {
                    "schema_version": 1,
                    "pages": [
                        {"page_id": "page_001", "status": "dispatched"},
                        {"page_id": "page_002", "status": "pending"},
                    ],
                },
            )
            write_json(run_dir / "run_state.json", {"status": "inputs_prepared", "history": []})

            result = subprocess.run(
                [sys.executable, RUNTIME_DIR / "page_job_status.py", run_dir, "--json"],
                text=True,
                capture_output=True,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            status = json.loads(result.stdout)
            self.assertEqual(6, status["max_concurrent_pages"])
            self.assertEqual(["page_001"], status["active_dispatches"])
            self.assertEqual(5, status["dispatch_slots_available"])
            self.assertEqual(["page_002"], status["dispatchable_pages"])

    def test_page_status_reports_batch_capacity_without_acting_as_scheduler(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp)
            write_json(
                run_dir / "page_jobs.json",
                {
                    "schema_version": 1,
                    "max_concurrent_pages": 1,
                    "pages": [
                        {"page_id": "page_001", "status": "dispatched"},
                        {"page_id": "page_002", "status": "pending"},
                    ],
                },
            )
            write_json(run_dir / "run_state.json", {"status": "inputs_prepared", "history": []})

            result = subprocess.run(
                [sys.executable, RUNTIME_DIR / "page_job_status.py", run_dir, "--json"],
                text=True,
                capture_output=True,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            status = json.loads(result.stdout)
            self.assertEqual(1, status["max_concurrent_pages"])
            self.assertEqual(["page_001"], status["active_dispatches"])
            self.assertEqual(0, status["dispatch_slots_available"])
            self.assertEqual(["page_002"], status["dispatchable_pages"])


if __name__ == "__main__":
    unittest.main()
