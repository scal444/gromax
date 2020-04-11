import unittest
from unittest import mock
from gromax.file_io import parseDirectoryStructure
from typing import List


def fakeListDir(input_path: str, dirs: List[str]):
    """
        Used to fake an os.walk call.
    """

    sub_path: str
    contents: List[str] = []
    # Account for possibility of input path like "/path/to/subdir/" which should still be valid.
    path: str = input_path
    if not path.endswith("/"):
        path += "/"
    for sub_path in dirs:
        # ignore all non subdirectory/subfile entries.
        if not sub_path.startswith(path):
            continue
        trimmed_path: str = sub_path[len(path):]
        # We only want what's directly in this directory. We can do this because of the "/" handing earlier.
        if not "/" in trimmed_path:
            contents.append(sub_path)
    return contents


_GOOD_DIRS = [
    "/path/group_1",
    "/path/group_1/trial_1",
    "/path/group_1/trial_1/test_component_1.log",
    "/path/group_1/trial_1/test_component_2.log",
    "/path/group_1/trial_2",
    "/path/group_1/trial_2/test_component_1.log",
    "/path/group_1/trial_2/test_component_2.log",
    "/path/group_2",
    "/path/group_2/trial_14",
    "/path/group_2/trial_14/component_86.log"
]

_GOOD_RESULT = {
    0: {
        0: {
            0: "/path/group_1/trial_1/test_component_1.log",
            1: "/path/group_1/trial_1/test_component_2.log"
        },
        1: {
            0: "/path/group_1/trial_2/test_component_1.log",
            1: "/path/group_1/trial_2/test_component_2.log"
        }
    },
    1: {
        13: {
            85: "/path/group_2/trial_14/component_86.log"
        }
    }
}


@mock.patch("gromax.file_io.os.listdir")
class ParseDirectoryStructureTest(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

    def testGoodDirectory(self, mock_listdir):

        def mock_os_wrapper(directory):
            return fakeListDir(directory, _GOOD_DIRS)

        mock_listdir.side_effect = mock_os_wrapper

        result = parseDirectoryStructure("/path")
        self.assertDictEqual(_GOOD_RESULT, result)

    def testEmptyDirectory(self, mock_listdir):
        def mock_os_wrapper(directory):
            return fakeListDir(directory, [])
        mock_listdir.side_effect = mock_os_wrapper
        self.assertDictEqual(parseDirectoryStructure("/path"), {})

    def testBadPath(self, mock_listdir):
        pass

    def testSomeEmptyGroups(self, mock_listdir):
        dirs = [
            "/path/group_1",
            "/path/group_1/trial_1",
            "/path/group_1/trial_1/test_component_1.log",
            "/path/group_2"
        ]

        def mock_os_wrapper(directory):
            return fakeListDir(directory, dirs)
        mock_listdir.side_effect = mock_os_wrapper
        result = parseDirectoryStructure("/path")

        expected = {
            0: {
                0: {
                    0: "/path/group_1/trial_1/test_component_1.log",
                }
            },
            1: {}
        }
        self.assertDictEqual(expected, result)

    def testIgnoresOtherFoldersAndFiles(self, mock_listdir):
        def mock_os_wrapper(directory):
            return fakeListDir(directory, _GOOD_DIRS + ["/some/other/path/group_1"])
        mock_listdir.side_effect = mock_os_wrapper

        result = parseDirectoryStructure("/path")
        self.assertDictEqual(_GOOD_RESULT, result)

    def testIgnoresBadFormat(self, mock_listdir):
        dirs = [
            "/path/group_1",
            "/path/group_1/trial_1",
            "/path/group_1/trial_1/test_component_1.log",
            # double group in path
            "/path/group_2_group_2",
            "/path/group_2_group_2/trial_1",
            # valid group
            "/path/group_3",
            # invalid int for trial
            "/path/group_3/trial_dkfjd",
            # valid group and trial
            "/path/group_4",
            "/path/group_4/trial_1",
            # double component
            "/path/group_4/trial_1/test_component_2_component_4.log"
        ]

        def mock_os_wrapper(directory):
            return fakeListDir(directory, dirs)
        mock_listdir.side_effect = mock_os_wrapper
        result = parseDirectoryStructure("/path")

        expected = {
            0: {
                0: {
                    0: "/path/group_1/trial_1/test_component_1.log",
                }
            },
            2: {},
            3: {
                0: {}
            }
        }
        self.assertDictEqual(expected, result)
