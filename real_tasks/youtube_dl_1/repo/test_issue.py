import unittest

from youtube_dl.utils import match_filter_func


class BooleanFilterTests(unittest.TestCase):
    def test_false_boolean_does_not_pass_positive_filter(self):
        result = match_filter_func("is_live")({"is_live": False})
        self.assertIsNotNone(result)
        self.assertIn("does not pass filter", result)


if __name__ == "__main__":
    unittest.main()
