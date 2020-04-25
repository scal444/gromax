from gromax.main import gromax as gmxentry
import unittest
from unittest import mock


class FailureTests(unittest.TestCase):
    def testNoMode(self):
        with mock.patch("sys.argv", ["gromax"]):
            with self.assertRaises(SystemExit) as sysexit:
                gmxentry()
            self.assertGreater(sysexit.exception.code, 0)


class NonExecutingTests(unittest.TestCase):
    def testVersionWorks(self):
        with mock.patch("sys.argv", ["gromax", "--version"]):
            with self.assertRaises(SystemExit) as sysexit:
                gmxentry()
            self.assertEqual(sysexit.exception.code, 0)

    def testHelpWorks(self):
        with mock.patch("sys.argv", ["gromax", "--help"]):
            with self.assertRaises(SystemExit) as sysexit:
                gmxentry()
            self.assertEqual(sysexit.exception.code, 0)
