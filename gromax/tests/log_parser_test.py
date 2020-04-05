import unittest

from gromax.log_parser import _performanceRegexOp, _typeOfParam, _convert, _commandInputRegexOp
from gromax.log_parser import LogParser, BasicParser


class TypeOfParamTest(unittest.TestCase):
    def testInvalidInput(self):
        with self.assertRaises(ValueError):
            _typeOfParam("invalid")
        with self.assertRaises(ValueError):
            _typeOfParam("")

    def testIntType(self):
        self.assertEqual(_typeOfParam("ntmpi"), int)

    def testFloatType(self):
        self.assertEqual(_typeOfParam("maxh"), float)

    def testBoolType(self):
        self.assertEqual(_typeOfParam("noconfout"), bool)

    def testStrType(self):
        self.assertEqual(_typeOfParam("nb"), str)


class ConvertTest(unittest.TestCase):
    # noinspection PyTypeChecker
    def testInvalidInput(self):
        with self.assertRaises(ValueError):
            _convert("val", None)

    def testStr(self):
        self.assertEqual(_convert("string", str), "string")

    def testInt(self):
        self.assertEqual(_convert("25", int), 25)

    def testFloat(self):
        self.assertAlmostEqual(_convert("1.5", float), 1.5)

    def testBool(self):
        self.assertTrue(_convert("", bool))


class CommandInputParserTest(unittest.TestCase):
    pre_garbage = "Some\nrandom\ntext"
    commandline_regex = "Command line:"
    post_garbage = "Other random text\nPerformance: 25.5 ns/day"

    def _combineArgs(self, inp: str) -> str:
        return "\n".join((self.pre_garbage, self.commandline_regex, inp, self.post_garbage))

    def testNoVal(self):
        self.assertIsNone(_commandInputRegexOp(self.pre_garbage + self.post_garbage))

    def testEmptyParam(self):
        args = "gmx mdrun"
        self.assertDictEqual(_commandInputRegexOp(self._combineArgs(args)), {})

    def testInvalid(self):
        args = "gmx mdrun -maxh blah"
        with self.assertRaises(ValueError):
            _commandInputRegexOp(self._combineArgs(args))

    def testIntParam(self):
        args = "gmx mdrun -ntomp 5"
        self.assertDictEqual(_commandInputRegexOp(self._combineArgs(args)), {"ntomp": 5})

    def testFloatParam(self):
        args = "gmx mdrun -maxh 3.0"
        self.assertDictEqual(_commandInputRegexOp(self._combineArgs(args)), {"maxh": 3.0})

    def testStrParam(self):
        args = "gmx mdrun -nb gpu"
        self.assertDictEqual(_commandInputRegexOp(self._combineArgs(args)), {"nb": "gpu"})

    def testBoolParam(self):
        args = "gmx mdrun -noconfout"
        self.assertDictEqual(_commandInputRegexOp(self._combineArgs(args)), {"noconfout": True})

    def testMultiParam(self):
        args = "gmx_mpi mdrun -noconfout -ntmpi 4 -maxh 2.1 -pme cpu"

        expected = {
            "ntmpi": 4,
            "pme": "cpu",
            "maxh": 2.1,
            "noconfout": True
        }
        self.assertDictEqual(_commandInputRegexOp(self._combineArgs(args)), expected)


class PerformanceParserTest(unittest.TestCase):
    def testsuccessfulParse(self):
        inp = "Performance: 23.5 ns/day"
        self.assertEqual(_performanceRegexOp(inp), {"performance": 23.5})

    def testemptyParse(self):
        self.assertIsNone(_performanceRegexOp(""))

    def testfailingParse(self):
        self.assertIsNone(_performanceRegexOp("Some random text"))


class LogParserTest(unittest.TestCase):

    match_perf = "some text\nPerformance: 25.12 ns/day\nOther text\n"
    match_cmd = "Some text\nCommand line:\ngmx mdrun -deffnm test -maxh 5 -ntomp 4\n\n"
    contents = match_cmd + match_perf

    def testBasicParserContent(self):
        parser = BasicParser()
        self.assertEqual(len(parser._operations), 2)

    def testNoOps(self):
        parser = LogParser()
        self.assertDictEqual(parser.parse(self.contents), {})

    def testOpButNoMatch(self):
        parser = LogParser()
        parser.addOp(_commandInputRegexOp)
        self.assertDictEqual(parser.parse(self.match_perf), {})

    def testSingleOp(self):
        parser = LogParser()
        parser.addOp(_performanceRegexOp)
        self.assertDictEqual(parser.parse(self.contents), {"performance": 25.12})

    def testMultiOp(self):
        parser = LogParser()
        parser.addOp(_commandInputRegexOp)
        parser.addOp(_performanceRegexOp)

        expected = {
            "performance": 25.12,
            "deffnm": "test",
            "maxh": 5.0,
            "ntomp": 4
        }
        self.assertDictEqual(parser.parse(self.contents), expected)
