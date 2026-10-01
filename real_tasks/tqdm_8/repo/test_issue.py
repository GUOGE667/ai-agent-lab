import unittest

from tqdm import tqdm


class CustomBarFormatTests(unittest.TestCase):
    def test_custom_prefix_and_suffix_with_bar(self):
        rendered = tqdm.format_meter(2, 4, 1, ncols=20,
                                     bar_format="X{n_fmt}{bar}Y{total_fmt}")
        self.assertTrue(rendered.startswith("X2"), rendered)
        self.assertTrue(rendered.endswith("Y4"), rendered)


if __name__ == "__main__":
    unittest.main()
