import unittest

from youtube_dl.utils import unified_timestamp


class UnifiedTimestampTests(unittest.TestCase):
    def test_pm_in_email_date_format(self):
        self.assertEqual(unified_timestamp("May 16, 2016 11:15 PM"), 1463440500)


if __name__ == "__main__":
    unittest.main()
