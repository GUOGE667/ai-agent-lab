import unittest

from query import build_query


class QueryTests(unittest.TestCase):
    def test_encodes_reserved_characters_in_keys_and_values(self):
        self.assertEqual(build_query({"search term": "a&b", "lang": "中文"}), "search+term=a%26b&lang=%E4%B8%AD%E6%96%87")

    def test_empty_query(self):
        self.assertEqual(build_query({}), "")


if __name__ == "__main__":
    unittest.main()
