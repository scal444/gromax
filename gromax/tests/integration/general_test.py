from gromax.main import gromax as gmxentry
import unittest
from unittest import mock


class FailureTests(unittest.TestCase):
    def testNoMode(self):
        with mock.patch("sys.argv", ["gromax"]):
            print("\n\n\ngot here \n\n\n\n\n")
            with self.assertRaises(SystemExit) as sysexit:
                gmxentry()
            self.assertGreater(sysexit.exception.code, 0)


class VersionTest(unittest.TestCase):
    def testVersionWorks(self):
        with mock.patch("sys.argv", ["gromax", "--version"]):
            print("\n\n\ngot here \n\n\n\n\n")
            with self.assertRaises(SystemExit) as sysexit:
                gmxentry()
            self.assertEqual(sysexit.exception.code, 0)
