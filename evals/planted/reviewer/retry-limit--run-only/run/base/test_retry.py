import unittest

from retry import should_stop


class ShouldStopTest(unittest.TestCase):
    def test_stops_past_the_limit(self):
        self.assertTrue(should_stop(31, "30s"))

    def test_keeps_going_inside_the_limit(self):
        self.assertFalse(should_stop(29, "30s"))


if __name__ == "__main__":
    unittest.main()
