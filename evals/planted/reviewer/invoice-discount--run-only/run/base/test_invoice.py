import unittest

from invoice import line_total


class LineTotalTest(unittest.TestCase):
    def test_total_in_cents(self):
        self.assertEqual(line_total(3, "12.50"), 3750)


if __name__ == "__main__":
    unittest.main()
