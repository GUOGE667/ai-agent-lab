import unittest

from slug import slugify


class SlugTests(unittest.TestCase):
    def test_lowercase(self):
        self.assertEqual(slugify("Hello World"), "hello-world")

    def test_repeated_spaces(self):
        self.assertEqual(slugify("A   B"), "a-b")


if __name__ == "__main__":
    unittest.main()
