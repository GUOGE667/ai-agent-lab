import unittest

from pagination import page


class PaginationTests(unittest.TestCase):
    def test_first_page(self):
        self.assertEqual(page(list(range(7)), 1, 3), [0, 1, 2])

    def test_second_page(self):
        self.assertEqual(page(list(range(7)), 2, 3), [3, 4, 5])

    def test_last_partial_page(self):
        self.assertEqual(page(list(range(7)), 3, 3), [6])


if __name__ == "__main__":
    unittest.main()
