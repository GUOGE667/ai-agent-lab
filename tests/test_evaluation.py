import unittest

from issue_agent.evaluation import aggregate_results, classify_result


class EvaluationTests(unittest.TestCase):
    def test_failure_categories_and_aggregate(self):
        base = {
            "baseline_tests": {"exit_code": 1},
            "final_tests": {"exit_code": 0, "timed_out": False},
            "changed_files": ["calc.py"],
            "usage": {"total_tokens": 20},
            "elapsed_seconds": 2.0,
            "tool_error_count": 1,
        }
        passed = dict(base)
        failed = {**base, "final_tests": {"exit_code": 1, "timed_out": False}, "usage": {"total_tokens": 10}, "elapsed_seconds": 1.0}
        invalid = {**base, "baseline_tests": {"exit_code": 0}}
        self.assertEqual(classify_result(passed), "passed")
        self.assertEqual(classify_result(failed), "tests_failed")
        self.assertEqual(classify_result(invalid), "already_passing")
        summary = aggregate_results([passed, failed, invalid])
        self.assertEqual(summary["pass_rate"], 0.333)
        self.assertEqual(summary["outcomes"], {"already_passing": 1, "passed": 1, "tests_failed": 1})
        self.assertEqual(summary["tool_errors"], 3)


if __name__ == "__main__":
    unittest.main()
