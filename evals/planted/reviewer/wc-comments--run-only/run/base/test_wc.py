import os
import tempfile
import unittest

from wc import count_lines


class CountLinesTest(unittest.TestCase):
    def test_counts_lines(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "f.conf")
            with open(path, "w", encoding="utf-8") as fh:
                fh.write("a = 1\nb = 2\n")
            self.assertEqual(count_lines(path), 2)


if __name__ == "__main__":
    unittest.main()
