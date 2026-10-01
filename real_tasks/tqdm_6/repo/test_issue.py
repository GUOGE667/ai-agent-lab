import unittest

from tqdm import tqdm


class DisabledIteratorTests(unittest.TestCase):
    def test_list_consumes_iterator_without_length(self):
        self.assertEqual(list(tqdm(iter(range(3)), disable=True)), [0, 1, 2])


if __name__ == "__main__":
    unittest.main()
