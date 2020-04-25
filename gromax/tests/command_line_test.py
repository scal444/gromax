import unittest
from gromax.command_line import parseArgs, parseIDString


class CommandLineInputTest(unittest.TestCase):
    def testInvalidGromacsVersionCaught(self):
        args = ["generate", "--gmx_version", "2015"]
        with self.assertRaises(SystemExit):
            parseArgs(args)

    def testValidGromacsVersionsAccepted(self):
        # TODO import this when centralized and loop over valid ones
        valid_options = ["2016", "2018", "2019", "2020"]
        for opt in valid_options:
            parseArgs(["generate", "--gmx_version", opt])

    def testExitsWithVersion(self):
        with self.assertRaises(SystemExit):
            parseArgs(["--version"])

    def testInvalidModeCaught(self):
        with self.assertRaises(SystemExit):
            parseArgs(["some_command"])


class IDParsingTests(unittest.TestCase):
    def testValidCommas(self):
        self.assertEqual(parseIDString("0,2,3,4"), [0, 2, 3, 4])

    def testValidDash(self):
        self.assertEqual(parseIDString("0-5"), [0, 1, 2, 3, 4, 5])

    def testSizeTwoValidColon(self):
        self.assertEqual(parseIDString("1:3"), [1, 2, 3])

    def testSizeThreeValidColonStrideOne(self):
        self.assertEqual(parseIDString("1:1:5"), [1, 2, 3, 4, 5])

    def testSizeThreeValidColonStrideOther(self):
        self.assertEqual(parseIDString("1:3:12"), [1, 4, 7, 10])

    def testValidSingleInt(self):
        self.assertEqual(parseIDString("5"), [5])

    def testInvalidCommas(self):
        with self.assertRaises(ValueError):
            parseIDString("0,,,3")

    def testInvalidColon(self):
        with self.assertRaises(ValueError):
            parseIDString("3::")

    def testInvalidDash(self):
        with self.assertRaises(ValueError):
            parseIDString("3-")

    def testOtherInvalid(self):
        with self.assertRaises(ValueError):
            parseIDString("a")
