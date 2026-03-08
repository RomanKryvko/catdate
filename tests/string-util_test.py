import unittest
from catdate.bot import split_lines

class TestStringUtil(unittest.TestCase):
    def test_splits_lines(self):
        data = "1234567890"
        expected = "1234\n5678\n90"
        actual = split_lines(data, 100, 40)
        self.assertEqual(actual, expected)

        expected = "1234\n5678\n90"
        actual = split_lines(data, 1000, 400)
        self.assertEqual(actual, expected)

        expected = "123456\n7890"
        actual = split_lines(data, 100, 60)
        self.assertEqual(actual, expected)


if __name__ == '__main__':
    unittest.main()
