import unittest

from retry import retry


class RetryTests(unittest.TestCase):
    def test_success_on_final_attempt(self):
        calls = []

        def operation():
            calls.append(1)
            if len(calls) < 3:
                raise RuntimeError("temporary")
            return "ok"

        self.assertEqual(retry(operation, 3), "ok")
        self.assertEqual(len(calls), 3)

    def test_exhausted_attempts_raise_last_error(self):
        calls = []

        def operation():
            calls.append(1)
            raise RuntimeError("still failing")

        with self.assertRaisesRegex(RuntimeError, "still failing"):
            retry(operation, 2)
        self.assertEqual(len(calls), 2)

    def test_invalid_attempt_count(self):
        with self.assertRaises(ValueError):
            retry(lambda: "ok", 0)


if __name__ == "__main__":
    unittest.main()
