import unittest

from tqdm.contrib import tenumerate


class EnumerateStartTests(unittest.TestCase):
    def test_explicit_start(self):
        self.assertEqual(list(tenumerate(["a", "b"], start=5, disable=True)),
                         [(5, "a"), (6, "b")])

    def test_default_start(self):
        self.assertEqual(list(tenumerate(["a"], disable=True)), [(0, "a")])


if __name__ == "__main__":
    unittest.main()
