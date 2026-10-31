import unittest

from page import title


class TitleTest(unittest.TestCase):
    def test_header_page(self):
        self.assertEqual(title("Title: Hello\n\nHello\nbody"), "Hello")


if __name__ == "__main__":
    unittest.main()
