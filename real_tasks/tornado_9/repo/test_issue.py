import collections
import collections.abc
import unittest

# Compatibility for this historical release on Python 3.12.
collections.MutableMapping = collections.abc.MutableMapping

from tornado.httputil import url_concat


class UrlConcatTests(unittest.TestCase):
    def test_none_args_preserves_existing_query(self):
        url = "https://example.test/path?a=1#fragment"
        self.assertEqual(url_concat(url, None), url)


if __name__ == "__main__":
    unittest.main()
