import json
import unittest

from youtube_dl.utils import js_to_json


class JavascriptStringTests(unittest.TestCase):
    def test_escaped_apostrophe_in_double_quoted_string(self):
        self.assertEqual(json.loads(js_to_json('"it\\\'s"')), "it's")


if __name__ == "__main__":
    unittest.main()
