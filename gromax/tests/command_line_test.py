import unittest
from gromax.command_line import parseArgs, parseIDString


class CommandLineInputTest(unittest.TestCase):
    def testInvalidGromacsVersionCaught(self):
        args = ["generate", "--gmx_version", "2015"]
        with self.assertRaises(SystemExit):
            parseArgs(args)

    def testValidGromacsVersionsAccepted(self):
        # TODO import this when centralized and loop over valid ones
        valid_options = ["2016", "2018", "2019"]
        for opt in valid_options:
            parseArgs(["generate", "--gmx_version", opt, "--cpu_ids", 0, "--gpu_ids", 0, "--run_file",  "test.sh"])

    def testExitsWithVersion(self):
        with self.assertRaises(SystemExit) as sysexit:
            parseArgs(["--version"])
        self.assertEqual(sysexit.exception.code, 0)

    def testInvalidModeCaught(self):
        with self.assertRaises(SystemExit) as sysexit:
            parseArgs(["some_command"])
        self.assertGreater(sysexit.exception.code, 0)


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
