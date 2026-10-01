import collections
import collections.abc
import tempfile
import unittest
from pathlib import Path

# This historical release predates the collections aliases removed in Python 3.10.
collections.Mapping = collections.abc.Mapping
collections.Sequence = collections.abc.Sequence

import pysnooper


class UnicodeTraceTests(unittest.TestCase):
    def test_chinese_source_and_log_are_utf8(self):
        with tempfile.TemporaryDirectory() as directory:
            log = Path(directory) / "trace.log"

            @pysnooper.snoop(log)
            def traced():
                message = "失败"
                return message

            self.assertEqual(traced(), "失败")
            output = log.read_text(encoding="utf-8")
            self.assertIn('message = "失败"', output)
            self.assertIn("Return value:.. '失败'", output)


if __name__ == "__main__":
    unittest.main()
