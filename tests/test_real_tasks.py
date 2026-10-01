import json
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from issue_agent.cli import _load_tasks, main


class RealTaskIntegrityTests(unittest.TestCase):
    def test_historical_bugs_have_failing_baselines_and_passing_reference_fixes(self):
        tasks_path = Path(__file__).resolve().parent.parent / "real_tasks" / "tasks.json"
        fixes_path = tasks_path.parent / "checks" / "reference_fixes.json"
        for task in _load_tasks(tasks_path):
            with self.subTest(task=task["id"]):
                source = task["source"]
                self.assertIn(source["project"], {"tqdm/tqdm", "cool-RR/PySnooper"})
                for field in ("buggy_commit", "fixed_commit"):
                    self.assertRegex(source[field], r"\A[0-9a-f]{40}\Z")
                repo = tasks_path.parent / task["repo"]
                self.assertTrue((repo / "LICENCE").is_file() or (repo / "LICENSE").is_file())
        output = StringIO()
        with redirect_stdout(output):
            status = main(["verify", "--tasks", str(tasks_path), "--fixes", str(fixes_path)])
        self.assertEqual(status, 0, output.getvalue())
        summary = json.loads(output.getvalue())
        self.assertEqual(summary["validated"], len(_load_tasks(tasks_path)))
        self.assertTrue(all(row["valid"] for row in summary["tasks"]))


if __name__ == "__main__":
    unittest.main()
