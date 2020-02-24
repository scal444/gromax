import unittest
from gromax.combination_generator import genNtmpiOptions, determineGpuTasks


class GenNtmpiOptionsTest(unittest.TestCase):

    def testCatchesFailure(self):
        with self.assertRaises(ValueError):
            genNtmpiOptions(0)

    def testSingleCase(self):
        self.assertEqual(genNtmpiOptions(1), [1])

    def testPrimeCase(self):
        self.assertEqual(genNtmpiOptions(5), [1, 5])

    def testEvenCase(self):
        self.assertEqual(genNtmpiOptions(6), [1, 2, 3, 6])

    def testOddCase(self):
        self.assertEqual(genNtmpiOptions(9), [1, 3, 9])

    def testWithNGpu(self):
        self.assertEqual(genNtmpiOptions(6, 2), [2, 6])


class DetermineGpuTasksTest(unittest.TestCase):
    def testOneRankWithPme(self):
        self.assertEqual(determineGpuTasks(1, [0], True), "00")

    def testOneRankNoPme(self):
        self.assertEqual(determineGpuTasks(1, [0], False), "0")

    def testMultiRankNoPme(self):
        self.assertEqual(determineGpuTasks(3, [0], False), "000")

    def testMultiRankOneGpu(self):
        self.assertEqual(determineGpuTasks(3, [0], True), "000")

    def testMultiRankMultiGpu(self):
        self.assertEqual(determineGpuTasks(6, [0, 4], True), "000444")
