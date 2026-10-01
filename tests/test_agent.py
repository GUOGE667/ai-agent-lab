import tempfile
import unittest
import json
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path

from issue_agent.agent import run_issue
from issue_agent.cli import _check_command, _load_tasks, _save, main
from issue_agent.workspace import Workspace


class WorkspaceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.source = Path(self.temp.name)
        (self.source / "calc.py").write_text("def add(a, b):\n    return a - b\n", encoding="utf-8")
        (self.source / "test_calc.py").write_text(
            "import unittest\nfrom calc import add\n"
            "class T(unittest.TestCase):\n"
            "    def test_add(self): self.assertEqual(add(2, 3), 5)\n", encoding="utf-8"
        )
        (self.source / ".env.local").write_text("OPENAI_API_KEY=private-test-value", encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    def test_copy_edit_and_tests_do_not_touch_source(self):
        with Workspace(self.source, ["{python}", "-m", "unittest", "discover"]) as work:
            self.assertNotIn(".env.local", work.list_files()["files"])
            self.assertNotEqual(work.run_tests()["exit_code"], 0)
            work.replace_text("calc.py", "return a - b", "return a + b")
            self.assertEqual(work.run_tests()["exit_code"], 0)
        self.assertIn("return a - b", (self.source / "calc.py").read_text(encoding="utf-8"))

    def test_path_guards_and_unique_replacement(self):
        with Workspace(self.source, ["{python}", "-m", "unittest"]) as work:
            for path in ("../secret.py", ".env.local", "foo\\bar.py", "/tmp/file.py"):
                with self.subTest(path=path), self.assertRaises(ValueError):
                    work.read_file(path)
            with self.assertRaises(ValueError):
                work.replace_text("calc.py", "not found", "replacement")
            with self.assertRaises(ValueError):
                work.replace_text("test_calc.py", "self.assertEqual", "self.assertTrue")
            for number in range(5):
                work.create_file(f"module_{number}.py", "value = 1\n")
            with self.assertRaises(ValueError):
                work.create_file("module_5.py", "value = 1\n")

    def test_large_source_can_be_read_in_lines_and_edited(self):
        source = "# historical source\n" + "value = 1\n" * 12000
        (self.source / "large.py").write_text(source, encoding="utf-8")
        with Workspace(self.source, ["{python}", "-m", "unittest"]) as work:
            with self.assertRaisesRegex(ValueError, "use read_lines"):
                work.read_file("large.py")
            excerpt = work.read_lines("large.py", 1, 2)
            self.assertIn("1: # historical source", excerpt["content"])
            self.assertIn("2: value = 1", excerpt["content"])
            with self.assertRaises(ValueError):
                work.read_lines("large.py", 0, 2)
            work.replace_text("large.py", "# historical source", "# repaired source")
            self.assertTrue(work.read_lines("large.py", 1, 1)["content"].endswith("# repaired source"))

    def test_mock_agent_loop(self):
        responses = [
            {"id": "r1", "output": [{"type": "function_call", "call_id": "c1", "name": "read_file", "arguments": '{"path":"calc.py"}'}], "usage": {"total_tokens": 10}},
            {"id": "r2", "output": [{"type": "function_call", "call_id": "c2", "name": "replace_text", "arguments": '{"path":"calc.py","old":"return a - b","new":"return a + b"}'}], "usage": {"total_tokens": 10}},
            {"id": "r3", "output": [{"type": "function_call", "call_id": "c3", "name": "run_tests", "arguments": "{}"}], "usage": {"total_tokens": 10}},
            {"id": "r4", "output": [{"type": "message", "content": [{"type": "output_text", "text": "Fixed add; tests pass."}]}], "usage": {"total_tokens": 10}},
        ]
        payloads = []

        def fake_request(payload, _key):
            payloads.append(payload)
            return responses.pop(0)

        with Workspace(self.source, ["{python}", "-m", "unittest", "discover"]) as work:
            result = run_issue(work, "Fix add", "mock-model", "unused-key", request_fn=fake_request)
        self.assertEqual(result.final_tests["exit_code"], 0)
        self.assertEqual(result.usage["total_tokens"], 40)
        self.assertEqual(result.stopped_reason, "completed")
        self.assertEqual(payloads[1]["previous_response_id"], "r1")
        self.assertEqual(len(result.trace), 3)
        with tempfile.TemporaryDirectory() as report_dir:
            output = Path(report_dir) / "run"
            _save(result, self.source, output)
            self.assertIn("+    return a + b", (output / "changes.diff").read_text(encoding="utf-8"))
            self.assertTrue((output / "trace.json").exists())

    def test_live_command_requires_explicit_flag(self):
        with redirect_stderr(StringIO()) as errors:
            status = main(["run", "--repo", str(self.source), "--issue-file", str(self.source / "calc.py"), "--test-command", '["{python}","-m","unittest"]'])
        self.assertEqual(status, 2)
        self.assertIn("--live", errors.getvalue())

    def test_offline_demo_and_task_check(self):
        with tempfile.TemporaryDirectory() as report_dir, redirect_stdout(StringIO()):
            output = Path(report_dir) / "demo"
            self.assertEqual(main(["demo", "--output", str(output)]), 0)
            self.assertTrue((output / "changes.diff").exists())
            summary_path = Path(report_dir) / "summary.json"
            self.assertEqual(main(["analyze", str(output), "--include-demo", "--output", str(summary_path)]), 0)
            self.assertFalse(json.loads(summary_path.read_text(encoding="utf-8"))["valid_for_model_effectiveness"])
            self.assertEqual(main(["check", "--tasks", str(Path(__file__).resolve().parent.parent / "examples" / "tasks.json")]), 0)

    def test_independent_acceptance_rejects_visible_test_overfit(self):
        tasks_path = Path(__file__).resolve().parent.parent / "examples" / "tasks.json"
        task = _load_tasks(tasks_path)[0]
        with Workspace(tasks_path.parent / task["repo"], task["test_command"]) as work:
            self.assertNotIn("checks/acceptance.py", work.list_files()["files"])
            work.replace_text("calculator.py", "return a - b", "return 5 if (a, b) == (2, 3) else -1")
            self.assertEqual(work.run_tests()["exit_code"], 0)
            self.assertNotEqual(work.run_tests(_check_command(task, tasks_path))["exit_code"], 0)
        with Workspace(tasks_path.parent / task["repo"], task["test_command"]) as work:
            work.replace_text("calculator.py", "return a - b", "return a + b")
            self.assertEqual(work.run_tests()["exit_code"], 0)
            self.assertEqual(work.run_tests(_check_command(task, tasks_path))["exit_code"], 0)

    def test_reference_fixes_validate_every_task(self):
        tasks_path = Path(__file__).resolve().parent.parent / "examples" / "tasks.json"
        fixes_path = tasks_path.parent / "checks" / "reference_fixes.json"
        output = StringIO()
        with redirect_stdout(output):
            self.assertEqual(main(["verify", "--tasks", str(tasks_path), "--fixes", str(fixes_path)]), 0)
        summary = json.loads(output.getvalue())
        self.assertEqual(summary["validated"], len(_load_tasks(tasks_path)))
        self.assertTrue(all(row["valid"] for row in summary["tasks"]))


if __name__ == "__main__":
    unittest.main()
