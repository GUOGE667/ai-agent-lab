import unittest

from tqdm import tqdm


class AnsiTrimTests(unittest.TestCase):
    def test_trimming_existing_reset_does_not_duplicate_it(self):
        escape = "\x1b"
        bar_format = f"*****{escape}[22m*****{escape}[0m**{{bar:10}}$$$$$$$$$$"
        rendered = tqdm.format_meter(0, 1000, 13, ncols=10, bar_format=bar_format)
        self.assertEqual(rendered, f"*****{escape}[22m*****{escape}[0m")


if __name__ == "__main__":
    unittest.main()
