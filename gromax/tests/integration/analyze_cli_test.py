"""
    Tests for gromax analyze.
"""
import contextlib
import os
import unittest
from io import StringIO
from unittest import mock
from gromax.main import gromax as gmxentry


class AnalyzeTestFailures(unittest.TestCase):

    def _run_and_get_rc(self) -> int:
        with mock.patch("sys.argv", self.args):
            with self.assertRaises(SystemExit) as sysexit:
                gmxentry()
            return sysexit.exception.code

    def setUp(self):
        self.args = ["gromax", "analyze"]

    def testNoSuchDirectory(self):
        empty_dir: str = os.path.join(os.path.dirname(__file__), "testdata/nonexistent_folder")
        self.args.extend(["--directory", empty_dir])
        self.assertGreater(self._run_and_get_rc(), 0)

    def testNoGroupsInDirectory(self):
        empty_dir: str = os.path.join(os.path.dirname(__file__), "testdata/empty_run_dir")
        self.args.extend(["--directory", empty_dir])
        self.assertGreater(self._run_and_get_rc(), 0)


FULL_RUN_EXPECTED_OUTPUT: str = """------------------------------
Highest throughput combination
------------------------------
  Aggregate performance: 78.83 ns/day
  Command line:
    gmx mdrun -deffnm replicate_1 -gputasks 00 -nb gpu -nstlist 80 -nt 1 -ntmpi 1 -ntomp 1 -pin on -pinoffset 0 -pinstride 1 -pme gpu -s $tpr &
    gmx mdrun -deffnm replicate_2 -gputasks 00 -nb gpu -nstlist 80 -nt 1 -ntmpi 1 -ntomp 1 -pin on -pinoffset 1 -pinstride 1 -pme gpu -s $tpr &
    gmx mdrun -deffnm replicate_3 -gputasks 00 -nb gpu -nstlist 80 -nt 1 -ntmpi 1 -ntomp 1 -pin on -pinoffset 2 -pinstride 1 -pme gpu -s $tpr &
    gmx mdrun -deffnm replicate_4 -gputasks 00 -nb gpu -nstlist 80 -nt 1 -ntmpi 1 -ntomp 1 -pin on -pinoffset 3 -pinstride 1 -pme gpu -s $tpr &
    gmx mdrun -deffnm replicate_5 -gputasks 00 -nb gpu -nstlist 80 -nt 1 -ntmpi 1 -ntomp 1 -pin on -pinoffset 4 -pinstride 1 -pme gpu -s $tpr &
    gmx mdrun -deffnm replicate_6 -gputasks 00 -nb gpu -nstlist 80 -nt 1 -ntmpi 1 -ntomp 1 -pin on -pinoffset 5 -pinstride 1 -pme gpu -s $tpr &
    gmx mdrun -deffnm replicate_7 -gputasks 00 -nb gpu -nstlist 80 -nt 1 -ntmpi 1 -ntomp 1 -pin on -pinoffset 6 -pinstride 1 -pme gpu -s $tpr &
    gmx mdrun -deffnm replicate_8 -gputasks 00 -nb gpu -nstlist 80 -nt 1 -ntmpi 1 -ntomp 1 -pin on -pinoffset 7 -pinstride 1 -pme gpu -s $tpr
----------------------
Best single simulation
----------------------
  Aggregate performance: 59.94 ns/day
  Command line:
    gmx mdrun -deffnm replicate_1 -gputasks 00 -nb gpu -nstlist 80 -nt 8 -ntmpi 1 -ntomp 8 -pin on -pinoffset 0 -pinstride 1 -pme gpu -s $tpr\n"""

MISSING_GROUP_2_TRIAL_3_OUTPUT = FULL_RUN_EXPECTED_OUTPUT.replace("59.94", "59.97")


class AnalyzeTestSuccess(unittest.TestCase):
    def _run_and_capture_output(self) -> int:
        with mock.patch("sys.argv", self.args):
            with self.assertRaises(SystemExit) as sysexit:
                gmxentry()
            return sysexit.exception.code

    def setUp(self):
        self.maxDiff = None
        self.args = ["gromax", "analyze"]

    def testFullRunSuccess(self):
        reference_folder_path = os.path.join(os.path.dirname(__file__), "testdata", "sample_run_dir")
        self.args.extend(["--directory", reference_folder_path])
        stdout = StringIO()
        with contextlib.redirect_stdout(stdout):
            rc = self._run_and_capture_output()
        self.assertEqual(rc, 0)
        self.assertEqual(stdout.getvalue(), FULL_RUN_EXPECTED_OUTPUT)

    def testFullRunFromCwd(self):
        cwd = os.getcwd()
        reference_folder_path = os.path.join(os.path.dirname(__file__), "testdata", "sample_run_dir")
        os.chdir(reference_folder_path)
        stdout = StringIO()
        with contextlib.redirect_stdout(stdout):
            rc = self._run_and_capture_output()
        os.chdir(cwd)
        self.assertEqual(rc, 0)
        self.assertEqual(stdout.getvalue(), FULL_RUN_EXPECTED_OUTPUT)


    def testWarnsOnMismatchedTrials(self):
        reference_folder_path = os.path.join(os.path.dirname(__file__), "testdata", "sample_run_dir_missing_trial")
        self.args.extend(["--directory", reference_folder_path])
        stdout = StringIO()
        with contextlib.redirect_stdout(stdout):
            rc = self._run_and_capture_output()
        self.assertEqual(rc, 0)
        self.assertEqual(stdout.getvalue(), MISSING_GROUP_2_TRIAL_3_OUTPUT)

    def testTossesUnreadableFile(self):
        reference_folder_path = os.path.join(os.path.dirname(__file__), "testdata", "sample_run_dir")
        self.args.extend(["--directory", reference_folder_path])
        stdout = StringIO()
        with contextlib.redirect_stdout(stdout):
            file_path = os.path.join(reference_folder_path, "group_2/trial_3/group_2_trial_3_component_1.log")
            stat = os.stat(file_path)
            os.chmod(file_path, 0o000)
            rc = self._run_and_capture_output()
            os.chmod(file_path, stat.st_mode)
        self.assertEqual(rc, 0)
        self.assertEqual(stdout.getvalue(), MISSING_GROUP_2_TRIAL_3_OUTPUT)

    def testTossesUnevenComponents(self):
        reference_folder_path = os.path.join(os.path.dirname(__file__), "testdata", "sample_run_dir_missing_component")
        self.args.extend(["--directory", reference_folder_path])
        stdout = StringIO()
        with contextlib.redirect_stdout(stdout):
            rc = self._run_and_capture_output()
        self.assertEqual(rc, 0)
        self.assertEqual(stdout.getvalue(), FULL_RUN_EXPECTED_OUTPUT)

    def testTossesParseErrorNoPerformance(self):
        reference_folder_path = os.path.join(os.path.dirname(__file__), "testdata", "sample_run_dir_missing_perf")
        self.args.extend(["--directory", reference_folder_path])
        stdout = StringIO()
        with contextlib.redirect_stdout(stdout):
            rc = self._run_and_capture_output()
        self.assertEqual(rc, 0)
        self.assertEqual(stdout.getvalue(), MISSING_GROUP_2_TRIAL_3_OUTPUT)

    def testTossesParseErrorNoCommandLine(self):
        reference_folder_path = os.path.join(os.path.dirname(__file__), "testdata", "sample_run_dir_missing_cli")
        self.args.extend(["--directory", reference_folder_path])
        stdout = StringIO()
        with contextlib.redirect_stdout(stdout):
            rc = self._run_and_capture_output()
        self.assertEqual(rc, 0)
        self.assertEqual(stdout.getvalue(), MISSING_GROUP_2_TRIAL_3_OUTPUT)