import unittest
from gromax.analysis import standardError, _commonKeyVals, GromaxData


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


class GmxDataTest(unittest.TestCase):
    """
        TODO - proper testing of reporting statis.
    """
    def setUp(self):
        self.data = GromaxData()

    def testInsertionsSucceeds(self):
        keys = ["one", "two", "three", "four"]
        vals = [1, 2.5, "three", False]
        for k, v in zip(keys, vals):
            self.data.insertDataPoint(0, 0, 0, k, v)

    def testRemoveWorks(self):
        self.data.insertDataPoint(0, 1, 2, "hi", "bye")
        self.data.remove(0, 1)
        self.assertDictEqual(self.data.groupStatistics(), {})

    def testRemoveOnEmptyDoesntCrash(self):
        self.data.remove(0, 0)
