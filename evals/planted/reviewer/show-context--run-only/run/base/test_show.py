import unittest

from show import show


class ShowTest(unittest.TestCase):
    def test_numbers_the_match(self):
        self.assertEqual(show(["a", "bx", "c"], "x"), ["2: bx"])


if __name__ == "__main__":
    unittest.main()
