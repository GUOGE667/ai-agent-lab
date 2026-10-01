import unittest

from tornado.ioloop import PeriodicCallback


class PeriodicCallbackTests(unittest.TestCase):
    def test_clock_moving_backwards_still_advances_schedule(self):
        callback = PeriodicCallback(lambda: None, 1000)
        callback._next_timeout = 10.0
        callback._update_next(9.5)
        self.assertEqual(callback._next_timeout, 11.0)


if __name__ == "__main__":
    unittest.main()
