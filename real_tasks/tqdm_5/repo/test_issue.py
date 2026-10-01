import unittest

from tqdm import tqdm


class DisabledTruthinessTests(unittest.TestCase):
    def test_disabled_instance_with_explicit_total(self):
        self.assertTrue(bool(tqdm(total=10, disable=True)))


if __name__ == "__main__":
    unittest.main()
