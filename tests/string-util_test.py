import unittest
from catdate.bot import split_line_by_words, split_lines

class TestStringUtil(unittest.TestCase):
    def test_splits_lines(self):
        data = "1234567890"
        expected = "1234\n5678\n90"
        actual = split_lines(data, 100/40)
        self.assertEqual(actual, expected)

        expected = "123456\n7890"
        actual = split_lines(data, 100/60)
        self.assertEqual(actual, expected)

    def test_splitting_preserves_words(self):
        data = "word1 word2 a-very-long-word-1111 words"
        expected  = "word1 word2\na-very-long-word-1111\nwords"
        actual = split_line_by_words(data, 100, 40)
        self.assertEqual(actual, expected)


if __name__ == '__main__':
    unittest.main()
