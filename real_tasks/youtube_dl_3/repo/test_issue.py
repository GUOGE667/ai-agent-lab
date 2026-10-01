import unittest

from youtube_dl.utils import unescapeHTML


class HtmlUnescapeTests(unittest.TestCase):
    def test_entity_after_unknown_ampersand_is_unescaped(self):
        self.assertEqual(unescapeHTML("&foo&amp;bar;"), "&foo&bar;")


if __name__ == "__main__":
    unittest.main()
