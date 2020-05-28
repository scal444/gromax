import unittest
from gromax.analysis import standardError, _commonKeyVals


class StandardErrorTests(unittest.TestCase):
    def testEmptyList(self):
        self.assertEqual(standardError([]), 0)

    def testSingleValue(self):
        self.assertEqual(standardError([1]), 0)

    def testMultipleValues(self):
        self.assertAlmostEqual(standardError([16.0, 20.0, 24.0]), 2.30940107676)


class CommonKeyValsTest(unittest.TestCase):

    def testOneOrBothNone(self):
        self.assertDictEqual(_commonKeyVals({}, {}), {})
        self.assertDictEqual({}, _commonKeyVals({"a": "b"}, {}))

    def testCompleteEqual(self):
        a = {"a": 1, "b": 2}
        self.assertDictEqual(_commonKeyVals(a, a), a)

    def testPartialMatch(self):
        a = {"a": 1, "b": 2, "c": "five"}
        b = {"a": 5, "b": 2, "c": "five"}
        expected = {"b": 2, "c": "five"}
        self.assertDictEqual(_commonKeyVals(a, b), expected)