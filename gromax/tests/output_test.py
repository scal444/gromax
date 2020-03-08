import unittest
from gromax.output import _serializeParams, _serializeConcurrentGroup


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
        pass


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
