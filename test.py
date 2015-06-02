import unittest

import main


class TestRateStrings(unittest.TestCase):
    def test1(self):
        self.assertEqual(main.rateStrings("kajak", "kajak"), [1])

    def test2(self):
        self.assertEqual(main.rateStrings("nazwa", "zwana"), [3])

    def test3(self):
        self.assertEqual(main.rateStrings("AAGGCCGGCT", "GGCTCCGGCA"), [4])

    def test4(self):
        self.assertEqual(main.rateStrings("babaca", "abaca"), [1, 5])

if __name__ == "__main__":
    unittest.main()