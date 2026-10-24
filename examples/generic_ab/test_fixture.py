import unittest

from fixture import classify_count


class ClassifyCountTests(unittest.TestCase):
    def test_zero(self):
        self.assertEqual(classify_count(0), "empty")

    def test_one(self):
        self.assertEqual(classify_count(1), "single")

    def test_many(self):
        self.assertEqual(classify_count(2), "multiple")
        self.assertEqual(classify_count(17), "multiple")


if __name__ == "__main__":
    unittest.main()
