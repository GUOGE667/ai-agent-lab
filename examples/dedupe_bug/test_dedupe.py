import unittest

from dedupe import unique_in_order


class DedupeTests(unittest.TestCase):
    def test_preserves_first_seen_order(self):
        self.assertEqual(unique_in_order(["z", "a", "z", "b", "a"]), ["z", "a", "b"])

    def test_empty_and_singleton(self):
        self.assertEqual(unique_in_order([]), [])
        self.assertEqual(unique_in_order(["x"]), ["x"])


if __name__ == "__main__":
    unittest.main()
