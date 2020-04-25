import argparse
import unittest
import gromax.main as gmx


class SelectWorkflowTest(unittest.TestCase):
    def setUp(self):
        self.args = argparse.Namespace()

    def testGenerateMode(self):
        self.args.mode = "generate"
        workflow = gmx._selectWorkflow(self.args)
        self.assertEqual(workflow, gmx._executeGenerateWorkflow)

    def testExecuteMode(self):
        self.args.mode = "execute"
        workflow = gmx._selectWorkflow(self.args)
        self.assertEqual(workflow, gmx._executeExecuteWorkflow)

    def testAnalyzeMode(self):
        self.args.mode = "analyze"
        workflow = gmx._selectWorkflow(self.args)
        self.assertEqual(workflow, gmx._executeAnalyzeWorkflow)

    def testUnsupported(self):
        self.args.mode = "some_mode"
        with self.assertRaises(ValueError):
            gmx._selectWorkflow(self.args)


class IDParsingTests(unittest.TestCase):
    def testValidCommas(self):
        self.assertEqual(gmx._parseIDString("0,2,3,4"), [0, 2, 3, 4])

    def testValidDash(self):
        self.assertEqual(gmx._parseIDString("0-5"), [0, 1, 2, 3, 4, 5])

    def testSizeTwoValidColon(self):
        self.assertEqual(gmx._parseIDString("1:3"), [1, 2, 3])

    def testSizeThreeValidColonStrideOne(self):
        self.assertEqual(gmx._parseIDString("1:1:5"), [1, 2, 3, 4, 5])

    def testSizeThreeValidColonStrideOther(self):
        self.assertEqual(gmx._parseIDString("1:3:12"), [1, 4, 7, 10])

    def testValidSingleInt(self):
        self.assertEqual(gmx._parseIDString("5"), [5])

    def testInvalidCommas(self):
        with self.assertRaises(ValueError):
            gmx._parseIDString("0,,,3")

    def testInvalidColon(self):
        with self.assertRaises(ValueError):
            gmx._parseIDString("3::")

    def testInvalidDash(self):
        with self.assertRaises(ValueError):
            gmx._parseIDString("3-")

    def testOtherInvalid(self):
        with self.assertRaises(ValueError):
            gmx._parseIDString("a")

