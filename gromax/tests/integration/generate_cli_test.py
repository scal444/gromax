import os
import tempfile
import unittest
from unittest import mock
from gromax.main import gromax as gmxentry

"""
    Integration test for gromax generate.
"""


class GenerateFailBadArgsTests(unittest.TestCase):

    def _run_and_get_rc(self) -> int:
        with mock.patch("sys.argv", self.cmds):
            with self.assertRaises(SystemExit) as sysexit:
                gmxentry()
            return sysexit.exception.code

    def setUp(self):
        self.cmds = ["gromax", "generate"]

    def testNoGmxVersion(self):
        self.cmds.extend(["--cpu_ids", "0-4", "--gpu_ids", "0-1", "--run_file", "test.sh"])
        self.assertGreater(self._run_and_get_rc(), 0)

    def testInvalidGmxVersion(self):
        self.cmds.extend(["--cpu_ids", "0-4", "--gpu_ids", "0-1", "--run_file", "test.sh", "--gmx_version", "2015"])
        self.assertGreater(self._run_and_get_rc(), 0)

    def testNoRunFile(self):
        self.cmds.extend(["--cpu_ids", "0-4", "--gpu_ids", "0-1", "--gmx_version", "2016"])
        self.assertGreater(self._run_and_get_rc(), 0)

    def testNoCpuIds(self):
        self.cmds.extend(["--gmx_version", "2019", "--gpu_ids", "0-1", "--run_file", "test.sh"])
        self.assertGreater(self._run_and_get_rc(), 0)

    def testNoGpuIds(self):
        self.cmds.extend(["--gmx_version", "2019", "--cpu_ids", "0,1,2", "--run_file", "test.sh"])
        self.assertGreater(self._run_and_get_rc(), 0)

    def testGmx2020(self):
        self.cmds.extend(["--gmx_version", "2020", "--cpu_ids", "0,1,2", "--run_file", "test.sh"])
        self.assertGreater(self._run_and_get_rc(), 0)


class GenerateSuccessTests(unittest.TestCase):
    def _run_and_get_rc(self) -> int:
        with mock.patch("sys.argv", self.args):
            with self.assertRaises(SystemExit) as sysexit:
                gmxentry()
            return sysexit.exception.code

    def _combineArgs(self):
        for key, val in self.kvs.items():
            self.args.append(key)
            self.args.append(val)

    def _runAndCompareOutput(self, reference_file: str):
        """
            Executes the program, checks for correct execution, compares output file to reference.
        """
        self._combineArgs()
        print("args: " + " ".join(self.args))
        self.assertEqual(self._run_and_get_rc(), 0)
        with open(self.kvs["--run_file"], 'r') as test_output_file:
            test_output: str = test_output_file.read()

        reference_file_path = os.path.join(os.path.dirname(__file__), "testdata", reference_file)
        with open(reference_file_path) as reference_output_file:
            reference_output: str = reference_output_file.read()
        self.assertMultiLineEqual(test_output, reference_output)

    def setUp(self):
        self.maxDiff = None
        self.kvs = {
            "--cpu_ids": "0-3",
            "--gpu_ids": "0,1",
            "--gmx_version": "2016",
            "--run_file": tempfile.mkstemp()[1],
        }
        self.args = ["gromax", "generate"]

    def tearDown(self):
        os.remove(self.kvs["--run_file"])

    def testGmx2016Basic(self):
        self._runAndCompareOutput("generate_test_default_2016.sh")

    def testGmx2018Basic(self):
        self.kvs["--gmx_version"] = "2018"
        self._runAndCompareOutput("generate_test_default_2018.sh")

    def testGmx2019Basic(self):
        self.kvs["--gmx_version"] = "2019"
        self._runAndCompareOutput("generate_test_default_2019.sh")

    def testCustomExecutableGmx(self):
        self.kvs["--gmx_executable"] = "/path/to/gmx_mpi"
        self._runAndCompareOutput("generate_test_custom_exe.sh")

    def testCustomTrialsPerGroup(self):
        self.kvs["--trials_per_group"] = "18"
        self._runAndCompareOutput("generate_test_custom_ntrials.sh")

    def testCustomDirectoryHasNoEffect(self):
        self.kvs["--directory"] = "/path/to/nowhere"
        self._runAndCompareOutput("generate_test_default_2016.sh")

    def testCustomTpr(self):
        self.kvs["--tpr"] = "custom_tpr.tpr"
        self._runAndCompareOutput("generate_test_custom_tpr.sh")

    def testWeirdCount(self):
        self.kvs["--cpu_ids"] = "0-6"
        self._runAndCompareOutput("generate_test_odd_cpu_count.sh")
