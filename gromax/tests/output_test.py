import unittest
from gromax.output import _serializeParams, _serializeConcurrentGroup, _incrementLines, _wrapInLoop


class SerializeParamsTest(unittest.TestCase):
    def testEmpty(self):
        self.assertEqual(_serializeParams(dict()), "")

    def testKeyValAllString(self):
        params = {"pme": "gpu", "bonded": "cpu"}
        self.assertEqual(_serializeParams(params), "-bonded cpu -pme gpu")

    def testKeyValStringBoolTrue(self):
        params = {"pme": "gpu", "notunepme": True}
        self.assertEqual(_serializeParams(params), "-notunepme -pme gpu")

    def testKeyValStringBoolFalse(self):
        params = {"pme": "gpu", "notunepme": False}
        self.assertEqual(_serializeParams(params), "-pme gpu")

    def testKeyValStringNone(self):
        params = {"pme": "gpu", "notunepme": None}
        self.assertEqual(_serializeParams(params), "-notunepme -pme gpu")

    def testKeyValStringInt(self):
        params = {"pme": "gpu", "nstlist": 80}
        self.assertEqual(_serializeParams(params), "-nstlist 80 -pme gpu")

    def testKeyValStringFloat(self):
        params = {"pme": "gpu", "maxh": 3.5}
        self.assertEqual(_serializeParams(params), "-maxh 3.5 -pme gpu")

    def testPrependGmx(self):
        params = {"pme": "gpu", "maxh": 3.5}
        self.assertEqual(_serializeParams(params, gmx="gmx_mpi"), "gmx_mpi -maxh 3.5 -pme gpu")


class SerializeConcurrentGroupTest(unittest.TestCase):
    param_group = [
        {
            "nt": 4,
            "pinoffset": 0
        },
        {
            "nt": 4,
            "pinoffset": 4
        },
        {
            "nt": 4,
            "pinoffset": 8
        }
    ]

    def testEmptyGroup(self):
        self.assertEqual("", _serializeConcurrentGroup([]))

    def testMultiGroup(self):
        expected: str = "-nt 4 -pinoffset 0&\n-nt 4 -pinoffset 4&\n-nt 4 -pinoffset 8"
        self.assertEqual(_serializeConcurrentGroup(self.param_group), expected)

    def testPrependGmx(self):
        expected: str = "gmx_mpi -nt 4 -pinoffset 0&\ngmx_mpi -nt 4 -pinoffset 4&\ngmx_mpi -nt 4 -pinoffset 8"
        self.assertEqual(_serializeConcurrentGroup(self.param_group, gmx="gmx_mpi"), expected)


class IncrementLinesTest(unittest.TestCase):

    def testNoInput(self):
        self.assertEqual(_incrementLines("", 1), "")

    def testZeroPadding(self):
        single_line: str = "some string"
        self.assertEqual(_incrementLines(single_line, 0), single_line)

    def testInvalid(self):
        with self.assertRaises(ValueError):
            _incrementLines("some string", -5)

    def testPadsMultipleLines(self):
        multi_lines = "some string\nanother string\na third string"
        expected: str = "   some string\n   another string\n   a third string"
        self.assertEqual(expected, _incrementLines(multi_lines, 3))

    def testKeepsOriginalSpacing(self):
        multi_lines = "some string\n  already incremented"
        expected: str = "   some string\n     already incremented"
        self.assertEqual(expected, _incrementLines(multi_lines, 3))


class WrapInLoopTest(unittest.TestCase):
    def testWrapEmptyLoop(self):
        self.assertEqual(_wrapInLoop("", "i", 5), "for i in {1..5}; do\n\ndone")

    def testWrapsLines(self):
        lines: str = "line 1\n  line 2 incremented"
        expected: str = "for var in {1..$trials}; do\n   line 1\n     line 2 incremented\ndone"
        self.assertEqual(expected, _wrapInLoop(lines, "var", "$trials", tab_increment=3))
