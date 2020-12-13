import unittest

import gromax.combination_generator as cg
from gromax.hardware_config import HardwareConfig


class GenNtmpiOptionsTest(unittest.TestCase):
    def testCatchesFailure(self):
        with self.assertRaises(ValueError):
            cg.genNtmpiOptions(0, 0)

    def testSingleCase(self):
        self.assertEqual(cg.genNtmpiOptions(1, 1), [1])

    def testPrimeCase(self):
        self.assertEqual(cg.genNtmpiOptions(3, 1), [1, 3])

    def testEvenCase(self):
        self.assertEqual(cg.genNtmpiOptions(6, 1), [1, 2, 3])

    def testOddCase(self):
        self.assertEqual(cg.genNtmpiOptions(9, 1), [1, 3])

    def testWithNGpu(self):
        self.assertEqual(cg.genNtmpiOptions(6, 2), [2, 6])

    def testNoGpu(self):
        self.assertEqual(cg.genNtmpiOptions(5, 0), [5])


class DetermineGpuTasksTest(unittest.TestCase):
    def testOneRankWithPme(self):
        self.assertEqual(cg.determineGpuTasks(1, [0], True), "00")

    def testOneRankNoPme(self):
        self.assertEqual(cg.determineGpuTasks(1, [0], False), "0")

    def testMultiRankNoPme(self):
        self.assertEqual(cg.determineGpuTasks(3, [0], False), "000")

    def testMultiRankOneGpu(self):
        self.assertEqual(cg.determineGpuTasks(3, [0], True), "000")

    def testMultiRankMultiGpu(self):
        self.assertEqual(cg.determineGpuTasks(6, [0, 4], True), "000444")


class ApplyOptionToAllTest(unittest.TestCase):

    def testEmpty(self):
        self.assertEqual(cg.applyOptionToAll([], "key", ["value"]), [])

    def testCorrectCombinationsGenerated(self):
        options = [{"o1": "v1"}, {"o2": "v2"}]
        result = cg.applyOptionToAll(options, "new_key", ["val1", "val2"])
        self.assertEqual(result, [
            {"o1": "v1", "new_key": "val1"},
            {"o1": "v1", "new_key": "val2"},
            {"o2": "v2", "new_key": "val1"},
            {"o2": "v2", "new_key": "val2"},
        ])


def testPredicate(opt) -> bool:
    return opt["num"] > 3


class ApplyOptionIfTests(unittest.TestCase):
    def testEmpty(self):
        self.assertEqual(cg.applyOptionIf([], "key", "val", testPredicate), [])

    def testPartiallyModified(self):
        options = [{"num": 3}, {"num": 4}]
        result = cg.applyOptionIf(options, "key", "val", testPredicate)
        self.assertListEqual(result, [
            {"num": 3},
            {"num": 4,
             "key": "val"}
        ])


class PruneOptionIfTests(unittest.TestCase):
    def testEmpty(self):
        self.assertEqual(cg.pruneOptionIf([], testPredicate), [])

    def testRemoveWorks(self):
        options = [{"num": 3}, {"num": 4}]
        result = cg.pruneOptionIf(options, testPredicate)
        self.assertListEqual(result, [
            {"num": 3},
        ])

    def testNoMatches(self):
        options = [{"num": 3}, {"num": 2}]
        result = cg.pruneOptionIf(options, testPredicate)
        self.assertListEqual(result, options)


class AddConfigDependentOptionsTest(unittest.TestCase):

    def setUp(self):
        self.options = {"pin": "on"}

    def testSingleCPUAndOffset(self):
        config = HardwareConfig(cpu_ids=[5])
        cg.addConfigDependentOptions(self.options, config)
        self.assertDictEqual(self.options, {
            "pin": "on",
            "pinstride": 1,
            "pinoffset": 5,
            "nt": 1,
            "nb": "cpu"
        })

    def testWithGpus(self):
        config = HardwareConfig(cpu_ids=[0, 1], gpu_ids=[1])
        cg.addConfigDependentOptions(self.options, config)
        self.assertDictEqual(self.options, {
            "pin": "on",
            "pinstride": 1,
            "pinoffset": 0,
            "nt": 2,
            "nb": "gpu"
        })

    def testNoGpusAndPinStride(self):
        config = HardwareConfig(cpu_ids=[0, 2, 4])
        cg.addConfigDependentOptions(self.options, config)
        self.assertDictEqual(self.options, {
            "pin": "on",
            "pinstride": 2,
            "pinoffset": 0,
            "nt": 3,
            "nb": "cpu"
        })


class CreateRunOptionsForSingleConfigTestv2016(unittest.TestCase):
    expected_base = {
        **cg._createBaseOptions(),
        "nt": 4,
        "pinstride": 1,
        "pinoffset": 0,
    }
    version = "2016"

    def setUp(self):
        self.config = HardwareConfig(cpu_ids=[0, 1, 2, 3])

    def testNoGpu(self):
        result = cg.createRunOptionsForSingleConfig(self.config, self.version)
        expected = [
            {
                **self.expected_base,
                "ntmpi": 4,
                "ntomp": 1,
                "nb": "cpu"
            }
        ]
        self.assertCountEqual(result, expected)

    def testSingleGPU(self):
        self.maxDiff = None
        self.config.gpu_ids = [0]
        result = cg.createRunOptionsForSingleConfig(self.config, self.version)
        expected = [
            {
                **self.expected_base,
                "ntmpi": 4,
                "ntomp": 1,
                "nb": "gpu",
                "gputasks": "0000"
            },
            {
                **self.expected_base,
                "ntmpi": 2,
                "ntomp": 2,
                "nb": "gpu",
                "gputasks": "00"
            },
            {
                **self.expected_base,
                "ntmpi": 1,
                "ntomp": 4,
                "nb": "gpu",
                "gputasks": "0"
            },
        ]
        self.assertCountEqual(result, expected)

    def testMultiGPU(self):
        self.config.gpu_ids = [0, 1]
        result = cg.createRunOptionsForSingleConfig(self.config, self.version)
        expected = [
            {
                **self.expected_base,
                "ntmpi": 4,
                "ntomp": 1,
                "nb": "gpu",
                "gputasks": "0011"
            },
            {
                **self.expected_base,
                "ntmpi": 2,
                "ntomp": 2,
                "nb": "gpu",
                "gputasks": "01"
            },
        ]
        self.assertCountEqual(result, expected)


class CreateRunOptionsForSingleConfigTestv2018(unittest.TestCase):
    expected_base = {
        **cg._createBaseOptions(),
        "nt": 4,
        "pinstride": 1,
        "pinoffset": 0,
    }
    version = "2018"

    def setUp(self):
        self.config = HardwareConfig(cpu_ids=[0, 1, 2, 3])

    def testNoGpu(self):
        result = cg.createRunOptionsForSingleConfig(self.config, self.version)
        expected = [
            {
                **self.expected_base,
                "ntmpi": 4,
                "ntomp": 1,
                "nb": "cpu"
            }
        ]
        self.assertCountEqual(result, expected)

    def testSingleGPU(self):
        self.maxDiff = None
        self.config.gpu_ids = [0]
        result = cg.createRunOptionsForSingleConfig(self.config, self.version)
        expected = [
            {
                **self.expected_base,
                "ntmpi": 4,
                "ntomp": 1,
                "nb": "gpu",
                "pme": "cpu",
                "gputasks": "0000"
            },
            {
                **self.expected_base,
                "ntmpi": 2,
                "ntomp": 2,
                "nb": "gpu",
                "pme": "cpu",
                "gputasks": "00"
            },
            {
                **self.expected_base,
                "ntmpi": 1,
                "ntomp": 4,
                "nb": "gpu",
                "pme": "cpu",
                "gputasks": "0"
            },
            # PME = gpu cases need npme=1
            {
                **self.expected_base,
                "ntmpi": 4,
                "ntomp": 1,
                "nb": "gpu",
                "pme": "gpu",
                "npme": 1,
                "gputasks": "0000"
            },
            {
                **self.expected_base,
                "ntmpi": 2,
                "ntomp": 2,
                "nb": "gpu",
                "pme": "gpu",
                "npme": 1,
                "gputasks": "00"
            },
            # Note the double gputask even though there's only one rank
            {
                **self.expected_base,
                "ntmpi": 1,
                "ntomp": 4,
                "nb": "gpu",
                "pme": "gpu",
                "gputasks": "00"
            },
        ]
        self.assertCountEqual(result, expected)

    def testMultiGPU(self):
        self.config.gpu_ids = [0, 1]
        result = cg.createRunOptionsForSingleConfig(self.config, self.version)
        expected = [
            {
                **self.expected_base,
                "ntmpi": 4,
                "ntomp": 1,
                "nb": "gpu",
                "pme": "cpu",
                "gputasks": "0011"
            },
            {
                **self.expected_base,
                "ntmpi": 2,
                "ntomp": 2,
                "nb": "gpu",
                "pme": "cpu",
                "gputasks": "01"
            },
            # PME = gpu cases need npme=1
            {
                **self.expected_base,
                "ntmpi": 4,
                "ntomp": 1,
                "nb": "gpu",
                "pme": "gpu",
                "npme": 1,
                "gputasks": "0011"
            },
            {
                **self.expected_base,
                "ntmpi": 2,
                "ntomp": 2,
                "nb": "gpu",
                "pme": "gpu",
                "npme": 1,
                "gputasks": "01"
            },

        ]
        self.assertCountEqual(result, expected)


class CreateRunOptionsForSingleConfigTestv2019(unittest.TestCase):
    expected_base = {
        **cg._createBaseOptions(),
        "nt": 4,
        "pinstride": 1,
        "pinoffset": 0,
    }
    version = "2019"

    def setUp(self):
        self.config = HardwareConfig(cpu_ids=[0, 1, 2, 3])

    def testNoGpu(self):
        result = cg.createRunOptionsForSingleConfig(self.config, self.version)
        expected = [
            {
                **self.expected_base,
                "ntmpi": 4,
                "ntomp": 1,
                "nb": "cpu"
            }
        ]
        self.assertCountEqual(result, expected)

    def testSingleGPU(self):
        self.maxDiff = None
        self.config.gpu_ids = [0]
        result = cg.createRunOptionsForSingleConfig(self.config, self.version)
        expected = [
            # bonded = cpu cases
            {
                **self.expected_base,
                "ntmpi": 4,
                "ntomp": 1,
                "nb": "gpu",
                "pme": "cpu",
                "bonded": "cpu",
                "gputasks": "0000"
            },
            {
                **self.expected_base,
                "ntmpi": 2,
                "ntomp": 2,
                "nb": "gpu",
                "bonded": "cpu",
                "pme": "cpu",
                "gputasks": "00"
            },
            {
                **self.expected_base,
                "ntmpi": 1,
                "ntomp": 4,
                "nb": "gpu",
                "bonded": "cpu",
                "pme": "cpu",
                "gputasks": "0"
            },
            # PME = gpu cases need npme=1
            {
                **self.expected_base,
                "ntmpi": 4,
                "ntomp": 1,
                "nb": "gpu",
                "bonded": "cpu",
                "pme": "gpu",
                "npme": 1,
                "gputasks": "0000"
            },
            {
                **self.expected_base,
                "ntmpi": 2,
                "ntomp": 2,
                "nb": "gpu",
                "bonded": "cpu",
                "pme": "gpu",
                "npme": 1,
                "gputasks": "00"
            },
            # Note the double gputask even though there's only one rank
            {
                **self.expected_base,
                "ntmpi": 1,
                "ntomp": 4,
                "nb": "gpu",
                "bonded": "cpu",
                "pme": "gpu",
                "gputasks": "00"
            },

            # Bonded = gpu cases
            {
                **self.expected_base,
                "ntmpi": 4,
                "ntomp": 1,
                "nb": "gpu",
                "bonded": "gpu",
                "pme": "cpu",
                "gputasks": "0000"
            },
            {
                **self.expected_base,
                "ntmpi": 2,
                "ntomp": 2,
                "nb": "gpu",
                "bonded": "gpu",
                "pme": "cpu",
                "gputasks": "00"
            },
            {
                **self.expected_base,
                "ntmpi": 1,
                "ntomp": 4,
                "nb": "gpu",
                "bonded": "gpu",
                "pme": "cpu",
                "gputasks": "0"
            },
            # PME = gpu cases need npme=1
            {
                **self.expected_base,
                "ntmpi": 4,
                "ntomp": 1,
                "nb": "gpu",
                "bonded": "gpu",
                "pme": "gpu",
                "npme": 1,
                "gputasks": "0000"
            },
            {
                **self.expected_base,
                "ntmpi": 2,
                "ntomp": 2,
                "nb": "gpu",
                "bonded": "gpu",
                "pme": "gpu",
                "npme": 1,
                "gputasks": "00"
            },
            # Note the double gputask even though there's only one rank
            {
                **self.expected_base,
                "ntmpi": 1,
                "ntomp": 4,
                "nb": "gpu",
                "bonded": "gpu",
                "pme": "gpu",
                "gputasks": "00"
            },
        ]
        self.assertCountEqual(result, expected)

    def testMultiGPU(self):
        self.config.gpu_ids = [0, 1]
        result = cg.createRunOptionsForSingleConfig(self.config, self.version)
        expected = [
            # bonded = cpu
            {
                **self.expected_base,
                "ntmpi": 4,
                "ntomp": 1,
                "nb": "gpu",
                "bonded": "cpu",
                "pme": "cpu",
                "gputasks": "0011"
            },
            {
                **self.expected_base,
                "ntmpi": 2,
                "ntomp": 2,
                "nb": "gpu",
                "bonded": "cpu",
                "pme": "cpu",
                "gputasks": "01"
            },
            # PME = gpu cases need npme=1
            {
                **self.expected_base,
                "ntmpi": 4,
                "ntomp": 1,
                "nb": "gpu",
                "bonded": "cpu",
                "pme": "gpu",
                "npme": 1,
                "gputasks": "0011"
            },
            {
                **self.expected_base,
                "ntmpi": 2,
                "ntomp": 2,
                "nb": "gpu",
                "bonded": "cpu",
                "pme": "gpu",
                "npme": 1,
                "gputasks": "01"
            },
            # bonded = gpu
            {
                **self.expected_base,
                "ntmpi": 4,
                "ntomp": 1,
                "nb": "gpu",
                "bonded": "gpu",
                "pme": "cpu",
                "gputasks": "0011"
            },
            {
                **self.expected_base,
                "ntmpi": 2,
                "ntomp": 2,
                "nb": "gpu",
                "bonded": "gpu",
                "pme": "cpu",
                "gputasks": "01"
            },
            # PME = gpu cases need npme=1
            {
                **self.expected_base,
                "ntmpi": 4,
                "ntomp": 1,
                "nb": "gpu",
                "bonded": "gpu",
                "pme": "gpu",
                "npme": 1,
                "gputasks": "0011"
            },
            {
                **self.expected_base,
                "ntmpi": 2,
                "ntomp": 2,
                "nb": "gpu",
                "bonded": "gpu",
                "pme": "gpu",
                "npme": 1,
                "gputasks": "01"
            },

        ]
        self.assertCountEqual(result, expected)


class CreateRunOptionsForSingleConfigTestv2020(unittest.TestCase):
    """
        Note that without P2P GPU stuff, this is the same as 2019.
    """
    expected_base = {
        **cg._createBaseOptions(),
        "nt": 4,
        "pinstride": 1,
        "pinoffset": 0,
    }
    version = "2020"

    def setUp(self):
        self.config = HardwareConfig(cpu_ids=[0, 1, 2, 3])

    def testNoGpu(self):
        result = cg.createRunOptionsForSingleConfig(self.config, self.version)
        expected = [
            {
                **self.expected_base,
                "ntmpi": 4,
                "ntomp": 1,
                "nb": "cpu"
            }
        ]
        self.assertCountEqual(result, expected)

    def testSingleGPU(self):
        self.maxDiff = None
        self.config.gpu_ids = [0]
        result = cg.createRunOptionsForSingleConfig(self.config, self.version)
        expected = [
            # bonded = cpu cases
            {
                **self.expected_base,
                "ntmpi": 1,
                "ntomp": 4,
                "nb": "gpu",
                "bonded": "cpu",
                "pme": "cpu",
                "update": "gpu",
                "gputasks": "0"
            },
            # PME = gpu cases need npme=1
            {
                **self.expected_base,
                "ntmpi": 4,
                "ntomp": 1,
                "nb": "gpu",
                "bonded": "cpu",
                "pme": "gpu",
                "npme": 1,
                "update": "gpu",
                "gputasks": "0000"
            },
            {
                **self.expected_base,
                "ntmpi": 2,
                "ntomp": 2,
                "nb": "gpu",
                "bonded": "cpu",
                "pme": "gpu",
                "npme": 1,
                "update": "gpu",
                "gputasks": "00"
            },
            # Note the double gputask even though there's only one rank
            {
                **self.expected_base,
                "ntmpi": 1,
                "ntomp": 4,
                "nb": "gpu",
                "bonded": "cpu",
                "pme": "gpu",
                "update": "gpu",
                "gputasks": "00"
            },

            # Bonded = gpu cases
            {
                **self.expected_base,
                "ntmpi": 1,
                "ntomp": 4,
                "nb": "gpu",
                "bonded": "gpu",
                "pme": "cpu",
                "update": "gpu",
                "gputasks": "0"
            },
            # PME = gpu cases need npme=1
            {
                **self.expected_base,
                "ntmpi": 4,
                "ntomp": 1,
                "nb": "gpu",
                "bonded": "gpu",
                "pme": "gpu",
                "npme": 1,
                "update": "gpu",
                "gputasks": "0000"
            },
            {
                **self.expected_base,
                "ntmpi": 2,
                "ntomp": 2,
                "nb": "gpu",
                "bonded": "gpu",
                "pme": "gpu",
                "npme": 1,
                "update": "gpu",
                "gputasks": "00"
            },
            # Note the double gputask even though there's only one rank
            {
                **self.expected_base,
                "ntmpi": 1,
                "ntomp": 4,
                "nb": "gpu",
                "bonded": "gpu",
                "pme": "gpu",
                "update": "gpu",
                "gputasks": "00"
            },
            # update = cpu cases
            {
                **self.expected_base,
                "ntmpi": 4,
                "ntomp": 1,
                "nb": "gpu",
                "pme": "cpu",
                "bonded": "cpu",
                "update": "cpu",
                "gputasks": "0000"
            },
            {
                **self.expected_base,
                "ntmpi": 2,
                "ntomp": 2,
                "nb": "gpu",
                "bonded": "cpu",
                "pme": "cpu",
                "update": "cpu",
                "gputasks": "00"
            },
            {
                **self.expected_base,
                "ntmpi": 1,
                "ntomp": 4,
                "nb": "gpu",
                "bonded": "cpu",
                "pme": "cpu",
                "update": "cpu",
                "gputasks": "0"
            },
            # PME = gpu cases need npme=1
            {
                **self.expected_base,
                "ntmpi": 4,
                "ntomp": 1,
                "nb": "gpu",
                "bonded": "cpu",
                "pme": "gpu",
                "npme": 1,
                "update": "cpu",
                "gputasks": "0000"
            },
            {
                **self.expected_base,
                "ntmpi": 2,
                "ntomp": 2,
                "nb": "gpu",
                "bonded": "cpu",
                "pme": "gpu",
                "npme": 1,
                "update": "cpu",
                "gputasks": "00"
            },
            # Note the double gputask even though there's only one rank
            {
                **self.expected_base,
                "ntmpi": 1,
                "ntomp": 4,
                "nb": "gpu",
                "bonded": "cpu",
                "pme": "gpu",
                "update": "cpu",
                "gputasks": "00"
            },

            # Bonded = gpu cases
            {
                **self.expected_base,
                "ntmpi": 4,
                "ntomp": 1,
                "nb": "gpu",
                "bonded": "gpu",
                "pme": "cpu",
                "update": "cpu",
                "gputasks": "0000"
            },
            {
                **self.expected_base,
                "ntmpi": 2,
                "ntomp": 2,
                "nb": "gpu",
                "bonded": "gpu",
                "pme": "cpu",
                "update": "cpu",
                "gputasks": "00"
            },
            {
                **self.expected_base,
                "ntmpi": 1,
                "ntomp": 4,
                "nb": "gpu",
                "bonded": "gpu",
                "pme": "cpu",
                "update": "cpu",
                "gputasks": "0"
            },
            # PME = gpu cases need npme=1
            {
                **self.expected_base,
                "ntmpi": 4,
                "ntomp": 1,
                "nb": "gpu",
                "bonded": "gpu",
                "pme": "gpu",
                "npme": 1,
                "update": "cpu",
                "gputasks": "0000"
            },
            {
                **self.expected_base,
                "ntmpi": 2,
                "ntomp": 2,
                "nb": "gpu",
                "bonded": "gpu",
                "pme": "gpu",
                "npme": 1,
                "update": "cpu",
                "gputasks": "00"
            },
            # Note the double gputask even though there's only one rank
            {
                **self.expected_base,
                "ntmpi": 1,
                "ntomp": 4,
                "nb": "gpu",
                "bonded": "gpu",
                "pme": "gpu",
                "update": "cpu",
                "gputasks": "00"
            },
        ]
        self.assertCountEqual(result, expected)

    def testMultiGPU(self):
        self.config.gpu_ids = [0, 1]
        result = cg.createRunOptionsForSingleConfig(self.config, self.version)
        expected = [
            # bonded = cpu
            {
                **self.expected_base,
                "ntmpi": 4,
                "ntomp": 1,
                "nb": "gpu",
                "bonded": "cpu",
                "pme": "cpu",
                "update": "cpu",
                "gputasks": "0011"
            },
            {
                **self.expected_base,
                "ntmpi": 2,
                "ntomp": 2,
                "nb": "gpu",
                "bonded": "cpu",
                "pme": "cpu",
                "update": "cpu",
                "gputasks": "01"
            },
            # PME = gpu cases need npme=1
            {
                **self.expected_base,
                "ntmpi": 4,
                "ntomp": 1,
                "nb": "gpu",
                "bonded": "cpu",
                "pme": "gpu",
                "npme": 1,
                "update": "cpu",
                "gputasks": "0011"
            },
            {
                **self.expected_base,
                "ntmpi": 2,
                "ntomp": 2,
                "nb": "gpu",
                "bonded": "cpu",
                "pme": "gpu",
                "npme": 1,
                "update": "cpu",
                "gputasks": "01"
            },
            # bonded = gpu
            {
                **self.expected_base,
                "ntmpi": 4,
                "ntomp": 1,
                "nb": "gpu",
                "bonded": "gpu",
                "pme": "cpu",
                "update": "cpu",
                "gputasks": "0011"
            },
            {
                **self.expected_base,
                "ntmpi": 2,
                "ntomp": 2,
                "nb": "gpu",
                "bonded": "gpu",
                "pme": "cpu",
                "update": "cpu",
                "gputasks": "01"
            },
            # PME = gpu cases need npme=1
            {
                **self.expected_base,
                "ntmpi": 4,
                "ntomp": 1,
                "nb": "gpu",
                "bonded": "gpu",
                "pme": "gpu",
                "npme": 1,
                "update": "cpu",
                "gputasks": "0011"
            },
            {
                **self.expected_base,
                "ntmpi": 2,
                "ntomp": 2,
                "nb": "gpu",
                "bonded": "gpu",
                "pme": "gpu",
                "npme": 1,
                "update": "cpu",
                "gputasks": "01"
            },
            # update = gpu options
            # PME = gpu cases need npme=1
            {
                **self.expected_base,
                "ntmpi": 4,
                "ntomp": 1,
                "nb": "gpu",
                "bonded": "cpu",
                "pme": "gpu",
                "npme": 1,
                "update": "gpu",
                "gputasks": "0011"
            },
            {
                **self.expected_base,
                "ntmpi": 2,
                "ntomp": 2,
                "nb": "gpu",
                "bonded": "cpu",
                "pme": "gpu",
                "npme": 1,
                "update": "gpu",
                "gputasks": "01"
            },
            # bonded = gpu
            # PME = gpu cases need npme=1
            {
                **self.expected_base,
                "ntmpi": 4,
                "ntomp": 1,
                "nb": "gpu",
                "bonded": "gpu",
                "pme": "gpu",
                "npme": 1,
                "update": "gpu",
                "gputasks": "0011"
            },
            {
                **self.expected_base,
                "ntmpi": 2,
                "ntomp": 2,
                "nb": "gpu",
                "bonded": "gpu",
                "pme": "gpu",
                "npme": 1,
                "update": "gpu",
                "gputasks": "01"
            },
        ]
        self.assertCountEqual(result, expected)


class CreateRunOptionsForConfigGroupTest(unittest.TestCase):
    common = {
        'nsteps': 5000,
        'resetstep': 2500,
        'pin': 'on',
        'noconfout': True,
        'nstlist': 80,
        'pinstride': 1,
        'nb': 'gpu',

    }

    def testEmptyBreakdown(self):
        self.assertEqual(cg.createRunOptionsForConfigGroup([], "2020"), [])

    def testFailsInvalidVersion(self):
        with self.assertRaises(ValueError):
            cg.createRunOptionsForConfigGroup([HardwareConfig(cpu_ids=[0])], "2015")

    def testSinglebreakdown(self):
        configs = [HardwareConfig(cpu_ids=[0, 1, 2, 3], gpu_ids=[0])]
        result = cg.createRunOptionsForConfigGroup(configs, "2016")
        expected = [
            [
                {
                    **self.common,
                    'nt': 4,
                    'pinoffset': 0,
                    'ntmpi': 1,
                    'ntomp': 4,
                    'gputasks': '0'
                },
            ],
            [
                {
                    **self.common,
                    'nt': 4,
                    'pinoffset': 0,
                    'ntmpi': 2,
                    'ntomp': 2,
                    'gputasks': '00'
                },
            ],
            [
                {
                    **self.common,
                    'nt': 4,
                    'pinoffset': 0,
                    'ntmpi': 4,
                    'ntomp': 1,
                    'gputasks': '0000'
                },
            ]
        ]
        self.assertCountEqual(result, expected)

    def testMultiBreakdown(self):
        configs = [HardwareConfig(cpu_ids=[0, 1], gpu_ids=[0]), HardwareConfig(cpu_ids=[2, 3], gpu_ids=[1])]
        result = cg.createRunOptionsForConfigGroup(configs, "2016")
        expected = [
            [
                {
                     **self.common,
                     'nt': 2,
                     'pinoffset': 0,
                     'ntmpi': 1,
                     'ntomp': 2,
                     'gputasks': '0'
                },
                {
                    **self.common,
                    'nt': 2,
                    'pinoffset': 2,
                    'ntmpi': 1,
                    'ntomp': 2,
                    'gputasks': '1'
                }
            ],
            [
                {
                    **self.common,
                    'nt': 2,
                    'pinoffset': 0,
                    'ntmpi': 2,
                    'ntomp': 1,
                    'gputasks': '00'
                },
                {
                    **self.common,
                    'nt': 2,
                    'pinoffset': 2,
                    'ntmpi': 2,
                    'ntomp': 1,
                    'gputasks': '11'
                 }
            ]
        ]
        self.assertCountEqual(result, expected)
