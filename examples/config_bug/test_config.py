import unittest

from config import parse_line


class ConfigTests(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(parse_line("NAME=demo"), ("NAME", "demo"))

    def test_equals_in_value(self):
        self.assertEqual(parse_line("TOKEN=a=b=c"), ("TOKEN", "a=b=c"))


if __name__ == "__main__":
    unittest.main()
