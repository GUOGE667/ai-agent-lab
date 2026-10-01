import unittest

from median import median


class MedianTests(unittest.TestCase):
    def test_odd_length(self):
        self.assertEqual(median([9, 1, 4]), 4)

    def test_even_length(self):
        self.assertEqual(median([10, 2, 8, 4]), 6)

    def test_empty_input(self):
        with self.assertRaises(ValueError):
            median([])


if __name__ == "__main__":
    unittest.main()
