import unittest

from youtube_dl.utils import dfxp2srt, parse_dfxp_time_expr


class DfxpTimingTests(unittest.TestCase):
    def test_missing_time_is_unknown(self):
        self.assertIsNone(parse_dfxp_time_expr(None))

    def test_paragraph_without_begin_is_skipped(self):
        source = '<tt><body><div><p begin="0" end="1">first</p><p end="2">missing</p></div></body></tt>'
        output = dfxp2srt(source)
        self.assertIn("first", output)
        self.assertNotIn("missing", output)


if __name__ == "__main__":
    unittest.main()
