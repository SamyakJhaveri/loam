import tempfile
import unittest

from cache import get
from store import put


class CacheTest(unittest.TestCase):
    def test_get_after_put(self):
        with tempfile.TemporaryDirectory() as root:
            put(root, "abc", "x")
            self.assertEqual(get(root, "abc"), "x")

    def test_missing_key(self):
        with tempfile.TemporaryDirectory() as root:
            self.assertIsNone(get(root, "zzz"))


if __name__ == "__main__":
    unittest.main()
