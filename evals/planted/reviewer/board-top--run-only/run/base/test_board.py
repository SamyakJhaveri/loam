import unittest

from board import board

ENTRIES = [{"name": "ada", "votes": 1}, {"name": "bo", "votes": 5}, {"name": "cy", "votes": 3}]


class BoardTest(unittest.TestCase):
    def test_most_votes_first(self):
        self.assertEqual(board(ENTRIES), ["bo", "cy", "ada"])


if __name__ == "__main__":
    unittest.main()
