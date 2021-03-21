import os
import sys
import gromax.testutils as testutils
import unittest
import gromax.utils as utils
from gromax.testutils import get_relative_path
from unittest import mock


class FatalErrorTests(unittest.TestCase):

    def setUp(self):
        self.stderr = testutils.StdChecker()
        self.stored_stderr = sys.stderr
        sys.stderr = self.stderr

    def tearDown(self):
        sys.stderr = self.stored_stderr

    def testWritesMessage(self):
        with self.assertRaises(SystemExit):
            utils.fatalError("message")

    def testExitsCleanly(self):
        with self.assertRaises(SystemExit) as cm:
            utils.fatalError("message")
        self.assertEqual(cm.exception.code, 1)


class OpenOrDieTests(unittest.TestCase):
    def setUp(self):
        self.stderr = testutils.StdChecker()
        self.stored_stderr = sys.stderr
        sys.stderr = self.stderr

    def tearDown(self):
        sys.stderr = self.stored_stderr

    def testReadGoodFile(self):
        file = get_relative_path("testdata/existing_file.txt")
        mode = "rt"
        self.assertIsNotNone(utils.openOrDie(file, mode))

    def testWriteGoodFile(self):
        file = get_relative_path("testdata/new_file.txt")
        mode = "xt"
        try:
            self.assertIsNotNone(utils.openOrDie(file, mode))
        finally:
            os.remove(file)

    def testFileExistsError(self):
        file = get_relative_path("testdata/existing_file.txt")
        mode = "xt"
        with self.assertRaises(SystemExit):
            utils.openOrDie(file, mode)

    def testFileNotFoundError(self):
        file = get_relative_path("testdata/nonexistentfile.txt")
        mode = "rt"
        with self.assertRaises(SystemExit):
            utils.openOrDie(file, mode)

    def testIsADirectoryError(self):
        file = get_relative_path("testdata")
        mode = "rt"
        with self.assertRaises(SystemExit):
            utils.openOrDie(file, mode)

    def testPermissionErrorRead(self):
        file = get_relative_path("testdata/existing_file.txt")
        mode = "rt"
        with mock.patch("builtins.open", mock.mock_open()) as mock_file:
            mock_file.side_effect = PermissionError()
            with self.assertRaises(SystemExit):
                utils.openOrDie(file, mode)

    def testPermissionErrorWrite(self):
        file = get_relative_path("testdata/existing_file.txt")
        mode = "wt"
        with mock.patch("builtins.open", mock.mock_open()) as mock_file:
            mock_file.side_effect = PermissionError()
            with self.assertRaises(SystemExit):
                utils.openOrDie(file, mode)
