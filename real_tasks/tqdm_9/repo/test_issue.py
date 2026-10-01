import unittest

from tqdm._tqdm import format_sizeof


class SiBoundaryTests(unittest.TestCase):
    def test_rounding_near_one_thousand_uses_kilo(self):
        self.assertEqual(format_sizeof(999.99), "1.00K")


if __name__ == "__main__":
    unittest.main()
