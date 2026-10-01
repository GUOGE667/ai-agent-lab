import collections
import collections.abc
import io
import unittest

# This historical release predates the collections aliases removed in Python 3.10.
collections.Mapping = collections.abc.Mapping
collections.Sequence = collections.abc.Sequence

import pysnooper


class CustomRepresentationTests(unittest.TestCase):
    def test_single_type_rule_for_local_variable(self):
        output = io.StringIO()

        @pysnooper.snoop(output, custom_repr=(list, lambda value: f"list-size={len(value)}"))
        def traced():
            values = [1, 2, 3]
            return 4

        self.assertEqual(traced(), 4)
        self.assertIn("values = list-size=3", output.getvalue())


if __name__ == "__main__":
    unittest.main()
