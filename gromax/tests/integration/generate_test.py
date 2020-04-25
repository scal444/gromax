import unittest
from unittest import mock
from gromax.main import gromax as gmxentry
from typing import List

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


class GenerateSuccessTests(unittest.TestCase):

    def testWithDefaultOptions(self):
        pass

    def testCustomExecutableGmx(self):
        pass

    def testCustomTrialsPerGroup(self):
        pass

    def testCustomDirectory(self):
        pass

    def testGmx2016(self):
        pass

    def testGmx2018(self):
        pass

    def testGmx2019(self):
        pass

    def testGmx2020(self):
        pass
