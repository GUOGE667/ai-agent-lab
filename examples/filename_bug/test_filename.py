import unittest

from filename import extension


class FilenameTests(unittest.TestCase):
    def test_multiple_dots(self):
        self.assertEqual(extension("report.final.PDF"), "pdf")

    def test_dotfile_and_trailing_dot(self):
        self.assertEqual(extension(".gitignore"), "")
        self.assertEqual(extension("report."), "")

    def test_no_suffix(self):
        self.assertEqual(extension("README"), "")


if __name__ == "__main__":
    unittest.main()
