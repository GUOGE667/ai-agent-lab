import unittest

from tornado.ioloop import IOLoop


class ForceCurrentTests(unittest.TestCase):
    def test_explicit_current_can_be_created_when_none_exists(self):
        self.assertIsNone(IOLoop.current(instance=False))
        loop = IOLoop(make_current=True)
        try:
            self.assertIs(IOLoop.current(instance=False), loop)
        finally:
            loop.close()
            IOLoop.clear_current()


if __name__ == "__main__":
    unittest.main()
