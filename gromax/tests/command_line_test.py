import unittest
from gromax.command_line import parseArgs


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
