import os
import unittest
import gromax.testutils as testutils
import gromax.hardware_config as hardware_config
from unittest.mock import patch


class ProcessorIDContentTests(unittest.TestCase):

    def testGoodSingleProcessor(self):
        cpu_ids = [0]
        self.assertTrue(hardware_config.checkProcessorIDContent(cpu_ids))

    def testGoodOffsetFromZero(self):
        cpu_ids = [1]
        self.assertTrue(hardware_config.checkProcessorIDContent(cpu_ids))

    def testGoodMultipleProcessors(self):
        cpu_ids = [1, 2]
        self.assertTrue(hardware_config.checkProcessorIDContent(cpu_ids))

    def testGoodLongStride(self):
        cpu_ids = [1, 4, 7]
        self.assertTrue(hardware_config.checkProcessorIDContent(cpu_ids))

    @patch('gromax.hardware_config.fatal_error')
    def testFailIfNotList(self, mock_fatal_error):
        cpu_ids = 1
        # TODO this is ugly, but mocking out fatal_error causes the function to continue
        with self.assertRaises(TypeError):
            hardware_config.checkProcessorIDContent(cpu_ids)
        self.assertTrue(mock_fatal_error.called)

    @patch('gromax.hardware_config.fatal_error')
    def testFailIfContentsString(self, mock_fatal_error):
        cpu_ids = ["1"]
        hardware_config.checkProcessorIDContent(cpu_ids)
        self.assertTrue(mock_fatal_error.called)

    @patch('gromax.hardware_config.fatal_error')
    def testFailIfContentsFloat(self, mock_fatal_error):
        cpu_ids = [1.5]
        hardware_config.checkProcessorIDContent(cpu_ids)
        self.assertTrue(mock_fatal_error.called)

    @patch('gromax.hardware_config.fatal_error')
    def testFailIfAnElementIsNonInt(self, mock_fatal_error):
        cpu_ids = [1, 2, 3.5, 4, 5]
        hardware_config.checkProcessorIDContent(cpu_ids)
        self.assertTrue(mock_fatal_error.called)

    @patch('gromax.hardware_config.fatal_error')
    def testFailIfNegativeIDs(self, mock_fatal_error):
        cpu_ids = [-1, 3]
        hardware_config.checkProcessorIDContent(cpu_ids)
        self.assertTrue(mock_fatal_error.called)

    @patch('gromax.hardware_config.fatal_error')
    def testFailIfInconsistentStride(self, mock_fatal_error):
        cpu_ids = [1, 3, 5, 8]
        hardware_config.checkProcessorIDContent(cpu_ids)
        self.assertTrue(mock_fatal_error.called)


def filePath(file_name):
    # TODO consider wrapping around this in testutils (like LoadTestFile or TestFilePath)
    return os.path.abspath(testutils.get_relative_path(file_name))


class HardwareConfigEqualityTest(unittest.TestCase):
    def setUp(self):
        self.config1 = hardware_config.HardwareConfig()
        self.config1.cpu_ids = [0, 2, 4]
        self.config1.gpu_ids = [0]
        self.config2 = hardware_config.HardwareConfig()
        self.config2.cpu_ids = [0, 2, 4]
        self.config2.gpu_ids = [0]

    def testEmpty(self):
        self.assertEqual(hardware_config.HardwareConfig(), hardware_config.HardwareConfig())

    def testEqual(self):
        self.assertEqual(self.config1, self.config2)

    def testNotEqual(self):
        self.config1.cpu_ids = [0, 2]
        self.assertNotEqual(self.config1, self.config2)

    def testNonSensical(self):
        self.assertNotEqual(self.config1, [])
        self.assertNotEqual(self.config1, None)
        self.assertNotEqual(self.config1, "what?")


class HardwareConfigFromFileTests(unittest.TestCase):
    def testLoadsFromConfigFileWithIds(self):
        file = filePath("testdata/hardwareconfig_GoodMultiple.json")
        config = hardware_config.HardwareConfig(file)
        self.assertEqual(config._cpu_ids, [0, 1, 2, 3])

    def testLoadsFromConfigFileWithSingleIDAsList(self):
        file = filePath("testdata/hardwareconfig_GoodSingleID.json")
        config = hardware_config.HardwareConfig(file)
        self.assertEqual(config._cpu_ids, [0])

    def testLoadsFromNumberOfProcessors(self):
        file = filePath("testdata/hardwareconfig_GoodNumProcs.json")
        config = hardware_config.HardwareConfig(file)
        self.assertEqual(config.num_cpus, 4)
        self.assertEqual(config._cpu_ids, [0, 1, 2, 3])

    def testNumProcsAndProcIDsWorkTogether(self):
        file = filePath("testdata/hardwareconfig_GoodWithBothCpuComponents.json")
        config = hardware_config.HardwareConfig(file)
        self.assertEqual(config.num_cpus, 4)
        self.assertEqual(config._cpu_ids, [0, 1, 2, 3])

    def testLoadsGpuIdsWithCpuIds(self):
        file = filePath("testdata/hardwareconfig_GoodCpuIdAndGpuID.json")
        config = hardware_config.HardwareConfig(file)
        self.assertEqual(config.num_cpus, 4)
        self.assertEqual(config._cpu_ids, [0, 1, 2, 3])
        self.assertEqual(config._gpu_ids, [0, 1])

    def testLoadsGpuIdsWithCpuProcNumber(self):
        file = filePath("testdata/hardwareconfig_GoodCpuNumAndGpuID.json")
        config = hardware_config.HardwareConfig(file)
        self.assertEqual(config.num_cpus, 5)
        self.assertEqual(config._gpu_ids, [0, 1])

    def testLoadsEmptyGpuId(self):
        file = filePath("testdata/hardwareconfig_GoodEmptyGpuId.json")
        config = hardware_config.HardwareConfig(file)
        self.assertEqual(config.num_cpus, 2)
        self.assertEqual(config._gpu_ids, [])

    def testLoadsFromLargerConfigFile(self):
        file = filePath("testdata/hardwareconfig_GoodCompleteConfig.json")
        config = hardware_config.HardwareConfig(file)
        self.assertEqual(config.num_cpus, 4)
        self.assertEqual(config._cpu_ids, [0, 1, 2, 3])
        self.assertEqual(config._gpu_ids, [0, 1])

    @patch('gromax.hardware_config.fatal_error')
    def testFailCases(self, mock_fatal_error):

        bad_examples = [
            "testdata/hardwareconfig_BadNoCpuInfo.json",
            "testdata/hardwareconfig_BadNumCpusNotInt.json",
            "testdata/hardwareconfig_BadNumCpusIsZero.json",
            "testdata/hardwareconfig_BadNumCpusIsNegative.json",
            "testdata/hardwareconfig_BadCpuIdsNotList.json",
            "testdata/hardwareconfig_BadCpuIdsNotInt.json",
            "testdata/hardwareconfig_BadCpuIdsIsNegative.json",
            "testdata/hardwareconfig_BadGpuIdsNotList.json",
            "testdata/hardwareconfig_BadGpuIdsNotInt.json",
            "testdata/hardwareconfig_BadGpuIdsIsNegative.json",
            "testdata/hardwareconfig_BadCannotOpenFile.json",
        ]

        for test_case in bad_examples:
            hardware_config.HardwareConfig(test_case)
            if not mock_fatal_error.called:
                print("Failed to raise exception for test case:\n{}".format(test_case))
                self.fail()

    def testBadJson(self):
        # TODO
        pass
