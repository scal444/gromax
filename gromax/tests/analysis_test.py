import unittest
from gromax.analysis import GromaxData, standardError


class StandardErrorTests(unittest.TestCase):
    def testEmptyList(self):
        self.assertEqual(standardError([]), 0)

    def testSingleValue(self):
        self.assertEqual(standardError([1]), 0)

    def testMultipleValues(self):
        self.assertAlmostEqual(standardError([16.0, 20.0, 24.0]), 2.30940107676)


class GromaxDataTest(unittest.TestCase):

    def testDataReturnedIsCopy(self):
        pass
