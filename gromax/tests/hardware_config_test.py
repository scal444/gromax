import math
import os
import unittest
import gromax.testutils as testutils
from gromax.hardware_config import checkProcessorIDContent, HardwareConfig
from gromax.hardware_config import generateConfigSplitOptions, distributeGpuIdsToTasks
from unittest.mock import patch


# noinspection PyTypeChecker
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


class GenerateConfigSplitOptionsTest(unittest.TestCase):
    def setUp(self):
        self.config = HardwareConfig()
        self.expected_base = [[self.config]]

    def testNoGpu(self):
        self.config.cpu_ids = [0, 1, 2, 3]
        self.config.gpu_ids = []

        result = generateConfigSplitOptions(self.config)
        self.assertEqual(self.expected_base, result)

    def testOnlyPrimeDivision(self):
        self.config.cpu_ids = [0, 1, 2]
        self.config.gpu_ids = [0]

        options = [HardwareConfig(cpu_ids=[i], gpu_ids=[0]) for i in range(3)]
        self.expected_base.append(options)
        result = generateConfigSplitOptions(self.config)
        self.assertEqual(self.expected_base, result)

    def testNoGoodDecompositionForMultipleGpus(self):
        # with 2 gpus and 3 cpus, the only decomposition is the original
        self.config.cpu_ids = [0, 1, 2]
        self.config.gpu_ids = [0, 1]

        result = generateConfigSplitOptions(self.config)
        self.assertEqual(self.expected_base, result)

    def testMultipleDecompositionWithOneGpu(self):
        self.config.cpu_ids = [0, 1, 2, 3]
        self.config.gpu_ids = [0]

        single_cpu_option = [HardwareConfig(cpu_ids=[i], gpu_ids=[0]) for i in range(4)]
        double_cpu_option = [HardwareConfig(cpu_ids=[i, i + 1], gpu_ids=[0]) for i in (0, 2)]
        self.expected_base.append(single_cpu_option)
        self.expected_base.append(double_cpu_option)
        result = generateConfigSplitOptions(self.config)
        self.assertEqual(self.expected_base, result)

    def testMultipleDecompositionWithMultipleGpus(self):
        # with 6 cpus and 2 gpus, the 3x option should not exist
        self.config.cpu_ids = [0, 1, 2, 3, 4, 5]
        self.config.gpu_ids = [0, 1]

        single_cpu_option = [HardwareConfig(cpu_ids=[i], gpu_ids=[math.floor(i / 3)]) for i in range(6)]
        three_cpu_option = [HardwareConfig(cpu_ids=[i, i+1, i+2], gpu_ids=[gpu_id]) for gpu_id, i in enumerate((0, 3))]
        self.expected_base.append(single_cpu_option)
        self.expected_base.append(three_cpu_option)
        result = generateConfigSplitOptions(self.config)
        self.assertEqual(self.expected_base, result)

    def testMultipleDecompositionWithOddRankOption(self):
        # with 6 cpus and 3 gpus, the 3x option exists but not the 2x
        self.config.cpu_ids = [0, 1, 2, 3, 4, 5]
        self.config.gpu_ids = [0, 1, 2]
        single_cpu_option = [HardwareConfig(cpu_ids=[i], gpu_ids=[math.floor(i / 2)]) for i in range(6)]
        two_cpu_option = [HardwareConfig(cpu_ids=[i, i+1], gpu_ids=[gpu_id]) for gpu_id, i in enumerate((0, 2, 4))]
        self.expected_base.append(single_cpu_option)
        self.expected_base.append(two_cpu_option)
        result = generateConfigSplitOptions(self.config)
        self.assertEqual(self.expected_base, result)


class DistributeGpuIdsToTasksTest(unittest.TestCase):

    # noinspection PyTypeChecker
    def testFailsWithBadInput(self):
        with self.assertRaises(ValueError):
            distributeGpuIdsToTasks([1, 2, 3], 5)
        with self.assertRaises(ValueError):
            distributeGpuIdsToTasks([1, 2, 3], 2)
        with self.assertRaises(TypeError):
            distributeGpuIdsToTasks(1, 5)

    def testSingleTaskSingleGpu(self):
        self.assertEqual(distributeGpuIdsToTasks([0], 1), [[0]])

    def testSingleTaskMultipleGpu(self):
        self.assertEqual(distributeGpuIdsToTasks([0, 1, 2], 1), [[0, 1, 2]])

    def testMultiTaskSingleGpu(self):
        self.assertEqual(distributeGpuIdsToTasks([0], 3), [[0], [0], [0]])

    def testMultiTaskMultiGpu(self):
        # more GPUs than tasks
        self.assertEqual(distributeGpuIdsToTasks([0, 1, 2, 3], 2), [[0, 1], [2, 3]])
        # more tasks than GPUs
        self.assertEqual(distributeGpuIdsToTasks([0, 1], 6), [[0], [0], [0], [1], [1], [1]])

    def testHandlesNonZeroStartingIDs(self):
        self.assertEqual(distributeGpuIdsToTasks([5, 18], 1), [[5, 18]])
