import unittest

from tqdm import tqdm


class UnitScaleWithoutTotalTests(unittest.TestCase):
    def test_unknown_total_with_numeric_scale(self):
        rendered = tqdm.format_meter(2, None, 1, unit_scale=2)
        self.assertTrue(rendered.startswith("4it"), rendered)


if __name__ == "__main__":
    unittest.main()
