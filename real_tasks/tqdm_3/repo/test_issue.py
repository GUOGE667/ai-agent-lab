import io
import unittest

from tqdm import tqdm


class UnknownLengthTruthinessTests(unittest.TestCase):
    def test_generator_has_defined_truth_value(self):
        progress = tqdm((value for value in [1, 2]), file=io.StringIO())
        try:
            self.assertTrue(bool(progress))
        finally:
            progress.close()


if __name__ == "__main__":
    unittest.main()
