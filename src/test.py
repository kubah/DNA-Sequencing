import unittest

from src import main


class TestRateStrings(unittest.TestCase):
    def test1(self):
        self.assertEqual(main.rate_strings("kajak", "kajak"), [1])

    def test2(self):
        self.assertEqual(main.rate_strings("nazwa", "zwana"), [3])

    def test3(self):
        self.assertEqual(main.rate_strings("AAGGCCGGCT", "GGCTCCGGCA"), [4])

    def test4(self):
        self.assertEqual(main.rate_strings("babaca", "abaca"), [1, 5])

if __name__ == "__main__":
    unittest.main()