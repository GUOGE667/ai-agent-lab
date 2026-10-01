import unittest

from tqdm._main import RE_SHLEX


class OptionBoundaryTests(unittest.TestCase):
    def test_embedded_double_dash_is_not_an_option(self):
        self.assertEqual(RE_SHLEX.findall("value--oops --total 5"), ["total"])


if __name__ == "__main__":
    unittest.main()
