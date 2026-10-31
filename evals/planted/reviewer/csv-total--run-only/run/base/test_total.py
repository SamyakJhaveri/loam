import unittest

from total import total


class TotalTest(unittest.TestCase):
    def test_sums_a_column(self):
        self.assertEqual(total("sales.csv", "amount"), 14.5)


if __name__ == "__main__":
    unittest.main()
