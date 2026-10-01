import unittest

from youtube_dl.jsinterp import JSInterpreter


class ZeroArgumentFunctionTests(unittest.TestCase):
    def test_nested_call_without_arguments(self):
        source = "function zero(){return 7;} function run(){return zero();}"
        self.assertEqual(JSInterpreter(source).call_function("run"), 7)


if __name__ == "__main__":
    unittest.main()
