import os
import unittest
import gromax.testutils as testutils
from gromax.hardware_config import checkProcessorIDContent, HardwareConfig
from unittest.mock import patch


class ProcessorIDContentTests(unittest.TestCase):

    def testGoodSingleProcessor(self):
        cpu_ids = [0]
        self.assertTrue(checkProcessorIDContent(cpu_ids))

    def testGoodOffsetFromZero(self):
        cpu_ids = [1]
        self.assertTrue(checkProcessorIDContent(cpu_ids))

    def testGoodMultipleProcessors(self):
        cpu_ids = [1, 2]
        self.assertTrue(checkProcessorIDContent(cpu_ids))

    def testGoodLongStride(self):
        cpu_ids = [1, 4, 7]
        self.assertTrue(checkProcessorIDContent(cpu_ids))

    @patch('gromax.utils.fatal_error')
    def testFailIfNotList(self, mock_fatal_error):
        cpu_ids = 1
        # TODO this is ugly, but mocking out fatal_error causes the function to continue
        with self.assertRaises(TypeError):
            checkProcessorIDContent(cpu_ids)
        self.assertTrue(mock_fatal_error.called)

    @patch('gromax.utils.fatal_error')
    def testFailIfContentsString(self, mock_fatal_error):
        cpu_ids = ["1"]
        checkProcessorIDContent(cpu_ids)
        self.assertTrue(mock_fatal_error.called)

    @patch('gromax.utils.fatal_error')
    def testFailIfContentsFloat(self, mock_fatal_error):
        cpu_ids = [1.5]
        checkProcessorIDContent(cpu_ids)
        self.assertTrue(mock_fatal_error.called)

    @patch('gromax.utils.fatal_error')
    def testFailIfAnElementIsNonInt(self, mock_fatal_error):
        cpu_ids = [1, 2, 3.5, 4, 5]
        checkProcessorIDContent(cpu_ids)
        self.assertTrue(mock_fatal_error.called)

    @patch('gromax.utils.fatal_error')
    def testFailIfNegativeIDs(self, mock_fatal_error):
        cpu_ids = [-1, 3]
        checkProcessorIDContent(cpu_ids)
        self.assertTrue(mock_fatal_error.called)

    @patch('gromax.utils.fatal_error')
    def testFailIfInconsistentStride(self, mock_fatal_error):
        cpu_ids = [1, 3, 5, 8]
        checkProcessorIDContent(cpu_ids)
        self.assertTrue(mock_fatal_error.called)


def filePath(file_name):
    # TODO consider wrapping around this in testutils (like LoadTestFile or TestFilePath)
    return os.path.abspath(testutils.get_relative_path(file_name))


class HardwareConfigBasicTests(unittest.TestCase):

    def testEmpty(self):
        hw_config = HardwareConfig()
        self.assertEqual(hw_config.num_cpus, 0)
        self.assertEqual(hw_config.num_gpus, 0)
        self.assertFalse(len(hw_config.cpu_ids))
        self.assertFalse(len(hw_config.gpu_ids))

    def testGetAndSet(self):
        cpu = [1, 2, 3]
        gpu = [4, 5]
        hw_config = HardwareConfig(cpu_ids=cpu, gpu_ids=gpu)
        self.assertEqual(hw_config.num_cpus, 3)
        self.assertEqual(hw_config.num_gpus, 2)
        self.assertEqual(hw_config.cpu_ids, [1, 2, 3])
        self.assertEqual(hw_config.gpu_ids, [4, 5])

    def testRepr(self):
        config = HardwareConfig(cpu_ids=[1, 2], gpu_ids=[5])
        self.assertEqual(config.__repr__(), "\nHardware config:\n\tcpu IDs : [1, 2]\n\tgpu IDs : [5]")

    @patch('gromax.utils.fatal_error')
    def testGpuIDFailureNotAList(self, mock_fatal):
        hw_config = HardwareConfig()
        hw_config.gpu_ids = 5
        mock_fatal.assert_called_with("gpu_ids paramater must be iterable")

    @patch('gromax.utils.fatal_error')
    def testGpuIDFailureNotAnInt(self, mock_fatal):
        hw_config = HardwareConfig()
        hw_config.gpu_ids = [1, 1.7584, 3]
        mock_fatal.assert_called_with("All gpu ids must be integers: {} is not an int".format(1.7584))

    @patch('gromax.utils.fatal_error')
    def testGpuIDFailureNotPositive(self, mock_fatal):
        hw_config = HardwareConfig()
        hw_config.gpu_ids = [1, 3, -1]
        mock_fatal.assert_called_with("Cannot have a negative GPU ID")


class HardwareConfigEqualityTest(unittest.TestCase):
    def setUp(self):
        self.config1 = HardwareConfig()
        self.config1.cpu_ids = [0, 2, 4]
        self.config1.gpu_ids = [0]
        self.config2 = HardwareConfig()
        self.config2.cpu_ids = [0, 2, 4]
        self.config2.gpu_ids = [0]

    def testEmpty(self):
        self.assertEqual(HardwareConfig(), HardwareConfig())

    def testEqual(self):
        self.assertEqual(self.config1, self.config2)

    def testNotEqual(self):
        self.config1.cpu_ids = [0, 2]
        self.assertNotEqual(self.config1, self.config2)

    def testNonSensical(self):
        self.assertNotEqual(self.config1, [])
        self.assertNotEqual(self.config1, None)
        self.assertNotEqual(self.config1, "what?")