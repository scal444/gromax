import unittest

from gromax.combination_generator import genNtmpiOptions, determineGpuTasks, applyOptionToAll, applyOptionIf
from gromax.combination_generator import addConfigDependentOptions, createRunOptionsForSingleConfig,  _createBaseOptions
from gromax.hardware_config import HardwareConfig


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

    def testNoGpu(self):
        self.assertEqual(genNtmpiOptions(5, 0), [5])


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


class ApplyOptionToAllTest(unittest.TestCase):

    def testEmpty(self):
        self.assertEqual(applyOptionToAll([], "key", ["value"]), [])

    def testCorrectCombinationsGenerated(self):
        options = [{"o1": "v1"}, {"o2": "v2"}]
        result = applyOptionToAll(options, "new_key", ["val1", "val2"])
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
        self.assertEqual(applyOptionIf([], "key", "val", testPredicate), [])

    def testPartiallyModified(self):
        options = [{"num": 3}, {"num": 4}]
        result = applyOptionIf(options, "key", "val", testPredicate)
        self.assertListEqual(result, [
            {"num": 3},
            {"num": 4,
             "key": "val"}
        ])


class AddConfigDependentOptionsTest(unittest.TestCase):

    def setUp(self):
        self.options = {"pin": "on"}

    def testSingleCPUAndOffset(self):
        config = HardwareConfig(cpu_ids=[5])
        addConfigDependentOptions(self.options, config)
        self.assertDictEqual(self.options, {
            "pin": "on",
            "pinstride": 1,
            "pinoffset": 5,
            "nt": 1,
            "nb": "cpu"
        })

    def testWithGpus(self):
        config = HardwareConfig(cpu_ids=[0, 1], gpu_ids=[1])
        addConfigDependentOptions(self.options, config)
        self.assertDictEqual(self.options, {
            "pin": "on",
            "pinstride": 1,
            "pinoffset": 0,
            "nt": 2,
            "nb": "gpu"
        })

    def testNoGpusAndPinStride(self):
        config = HardwareConfig(cpu_ids=[0, 2, 4])
        addConfigDependentOptions(self.options, config)
        self.assertDictEqual(self.options, {
            "pin": "on",
            "pinstride": 2,
            "pinoffset": 0,
            "nt": 3,
            "nb": "cpu"
        })


class CreateRunOptionsForSingleConfigTestv2016(unittest.TestCase):
    expected_base = {
        **_createBaseOptions(),
        "nt": 4,
        "pinstride": 1,
        "pinoffset": 0,
    }
    version = "2016"

    def setUp(self):
        self.config = HardwareConfig(cpu_ids=[0, 1, 2, 3])

    def testNoGpu(self):
        result = createRunOptionsForSingleConfig(self.config, self.version)
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
        result = createRunOptionsForSingleConfig(self.config, self.version)
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
        result = createRunOptionsForSingleConfig(self.config, self.version)
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
        **_createBaseOptions(),
        "nt": 4,
        "pinstride": 1,
        "pinoffset": 0,
    }
    version = "2018"

    def setUp(self):
        self.config = HardwareConfig(cpu_ids=[0, 1, 2, 3])

    def testNoGpu(self):
        result = createRunOptionsForSingleConfig(self.config, self.version)
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
        result = createRunOptionsForSingleConfig(self.config, self.version)
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
        result = createRunOptionsForSingleConfig(self.config, self.version)
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
        **_createBaseOptions(),
        "nt": 4,
        "pinstride": 1,
        "pinoffset": 0,
    }
    version = "2019"

    def setUp(self):
        self.config = HardwareConfig(cpu_ids=[0, 1, 2, 3])

    def testNoGpu(self):
        result = createRunOptionsForSingleConfig(self.config, self.version)
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
        result = createRunOptionsForSingleConfig(self.config, self.version)
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
        result = createRunOptionsForSingleConfig(self.config, self.version)
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
        **_createBaseOptions(),
        "nt": 4,
        "pinstride": 1,
        "pinoffset": 0,
    }
    version = "2020"

    def setUp(self):
        self.config = HardwareConfig(cpu_ids=[0, 1, 2, 3])

    def testNoGpu(self):
        result = createRunOptionsForSingleConfig(self.config, self.version)
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
        result = createRunOptionsForSingleConfig(self.config, self.version)
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
        result = createRunOptionsForSingleConfig(self.config, self.version)
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


class CreateRunOptionsForConfigGroupTest(unittest.TestCase):
    # Mock out single config here and replace with something we can easily test.
    def testEmptyBreakdown(self):
        pass

    def testSinglebreakdown(self):
        pass

    def testMultiBreakdown(self):
        pass
