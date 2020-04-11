import unittest
from unittest import mock
from gromax.output import _serializeParams, _serializeConcurrentGroup, _incrementLines, _wrapInLoop, ParamsToString
from gromax.output import _injectTpr, _injectFileNaming, _ProcessSingleGroup, _addDirectoryHandling, _ProcessAllGroups


class SerializeParamsTest(unittest.TestCase):
    def testEmpty(self):
        self.assertEqual(_serializeParams(dict()), "")

    def testKeyValAllString(self):
        params = {"pme": "gpu", "bonded": "cpu"}
        self.assertEqual(_serializeParams(params), "-bonded cpu -pme gpu")

    def testKeyValStringBoolTrue(self):
        params = {"pme": "gpu", "notunepme": True}
        self.assertEqual(_serializeParams(params), "-notunepme -pme gpu")

    def testKeyValStringBoolFalse(self):
        params = {"pme": "gpu", "notunepme": False}
        self.assertEqual(_serializeParams(params), "-pme gpu")

    def testKeyValStringNone(self):
        params = {"pme": "gpu", "notunepme": None}
        self.assertEqual(_serializeParams(params), "-notunepme -pme gpu")

    def testKeyValStringInt(self):
        params = {"pme": "gpu", "nstlist": 80}
        self.assertEqual(_serializeParams(params), "-nstlist 80 -pme gpu")

    def testKeyValStringFloat(self):
        params = {"pme": "gpu", "maxh": 3.5}
        self.assertEqual(_serializeParams(params), "-maxh 3.5 -pme gpu")

    def testPrependGmx(self):
        params = {"pme": "gpu", "maxh": 3.5}
        self.assertEqual(_serializeParams(params, prepend="gmx_mpi"), "gmx_mpi -maxh 3.5 -pme gpu")


class SerializeConcurrentGroupTest(unittest.TestCase):
    param_group = [
        {
            "nt": 4,
            "pinoffset": 0
        },
        {
            "nt": 4,
            "pinoffset": 4
        },
        {
            "nt": 4,
            "pinoffset": 8
        }
    ]

    def testEmptyGroup(self):
        self.assertEqual("", _serializeConcurrentGroup([]))

    def testMultiGroup(self):
        expected: str = "-nt 4 -pinoffset 0 &\n-nt 4 -pinoffset 4 &\n-nt 4 -pinoffset 8"
        self.assertEqual(_serializeConcurrentGroup(self.param_group), expected)

    def testPrependGmx(self):
        expected: str = "gmx_mpi -nt 4 -pinoffset 0 &\ngmx_mpi -nt 4 -pinoffset 4 &\ngmx_mpi -nt 4 -pinoffset 8"
        self.assertEqual(_serializeConcurrentGroup(self.param_group, prepend="gmx_mpi"), expected)


class InjectionTest(unittest.TestCase):

    def setUp(self):
        self.base = [{"param1": "val1"}, {"param1": "val1"}]

    def testInjectTprWorks(self):
        _injectTpr(self.base)
        expected = [{"param1": "val1", "s": "${tpr}"}, {"param1": "val1", "s": "${tpr}"}]
        self.assertCountEqual(self.base, expected)

    def testInjectTprCustomNaming(self):
        _injectTpr(self.base, placeholder="${placeholder}")
        expected = [{"param1": "val1", "s": "${placeholder}"}, {"param1": "val1", "s": "${placeholder}"}]
        self.assertCountEqual(self.base, expected)

    def testInjectFileNamingWorks(self):
        _injectFileNaming(self.base)
        expected = [
            {"param1": "val1", "deffnm": "group_${group}_trial_${i}_component_1"},
            {"param1": "val1", "deffnm": "group_${group}_trial_${i}_component_2"}
        ]
        self.assertCountEqual(self.base, expected)

    def testInjectFileCustomName(self):
        _injectFileNaming(self.base, group_placeholder="alt", trial_placeholder="${j}")
        expected = [
            {"param1": "val1", "deffnm": "group_alt_trial_${j}_component_1"},
            {"param1": "val1", "deffnm": "group_alt_trial_${j}_component_2"}
        ]
        self.assertCountEqual(self.base, expected)

    def testInjectEmptyFileName(self):
        empty = []
        _injectFileNaming(empty)
        self.assertEqual([], empty)


class IncrementLinesTest(unittest.TestCase):
    def testNoInput(self):
        self.assertEqual(_incrementLines("", 1), "")

    def testZeroPadding(self):
        single_line: str = "some string"
        self.assertEqual(_incrementLines(single_line, 0), single_line)

    def testInvalid(self):
        with self.assertRaises(ValueError):
            _incrementLines("some string", -5)

    def testPadsMultipleLines(self):
        multi_lines = "some string\nanother string\na third string"
        expected: str = "   some string\n   another string\n   a third string"
        self.assertEqual(expected, _incrementLines(multi_lines, 3))

    def testKeepsOriginalSpacing(self):
        multi_lines = "some string\n  already incremented"
        expected: str = "   some string\n     already incremented"
        self.assertEqual(expected, _incrementLines(multi_lines, 3))


class AddDirectoryHandlingTest(unittest.TestCase):
    def setUp(self):
        self.base = "some string\nother string"

    def testAddDirectoriesBasic(self):
        result = _addDirectoryHandling(self.base)
        expected = "trialdir=${groupdir}/trial_${i}\nmkdir $trialdir\ncd $trialdir\nsome string\nother string\ncd ${" \
                   "groupdir}"
        self.assertEqual(result, expected)

    def testAddDirectoriesCustom(self):
        result = _addDirectoryHandling(self.base, workdir="${placeholder}", trial_placeholder="${j}")
        expected = "trialdir=${placeholder}/trial_${j}\nmkdir $trialdir\ncd $trialdir\nsome string\nother string\n" \
                   "cd ${placeholder}"
        self.assertEqual(result, expected)


class WrapInLoopTest(unittest.TestCase):
    def testWrapEmptyLoop(self):
        self.assertEqual(_wrapInLoop("", "i", 5), "for i in {1..5}; do\n\ndone")

    def testWrapsLines(self):
        lines: str = "line 1\n  line 2 incremented"
        expected: str = "for var in {1..$trials}; do\n   line 1\n     line 2 incremented\ndone"
        self.assertEqual(expected, _wrapInLoop(lines, "var", "$trials", tab_increment=3))


class ProcessSingleGroupTest(unittest.TestCase):
    def setUp(self):
        self.params = [{"p1": "v1", "p2": "v2"}, {"p3": True, "p4": None}]

    def testProcessSingleGroup(self):
        self.maxDiff = None
        result = _ProcessSingleGroup(self.params, "gmx mdrun", "i", 3, resetstep="${resetstep}", nsteps="${nsteps}",
                                     tab_increment=2)
        expected: str = (
            "for i in {1..3}; do\n"
            "  trialdir=${groupdir}/trial_${i}\n"
            "  mkdir $trialdir\n"
            "  cd $trialdir\n"
            "  gmx mdrun -deffnm group_${group}_trial_${i}_component_1 -nsteps ${nsteps} " 
            "-p1 v1 -p2 v2 -resetstep ${resetstep} -s ${tpr} &\n"
            "  gmx mdrun -deffnm group_${group}_trial_${i}_component_2 -nsteps ${nsteps} " 
            "-p3 -p4 -resetstep ${resetstep} -s ${tpr}\n"
            "  wait\n"
            "  cd ${groupdir}\n"
            "done"
        )
        self.assertEqual(result, expected)


class ProcessAllGroupsTest(unittest.TestCase):
    @mock.patch("gromax.output._ProcessSingleGroup")
    def testProcessAllGroups(self, mock_process):
        groups = [[], [], []]
        mock_process.return_value = "placeholder loop text"
        result = _ProcessAllGroups(groups, "i", "gmx mdrun", 5)
        expected = (
            "group=1\n"
            "groupdir=$workdir/group_1\n"
            "mkdir $groupdir\ncd $groupdir\n"
            "placeholder loop text\n\n\n"
            "group=2\n"
            "groupdir=$workdir/group_2\n"
            "mkdir $groupdir\ncd $groupdir\n"            
            "placeholder loop text\n\n\n"
            "group=3\n"
            "groupdir=$workdir/group_3\n"
            "mkdir $groupdir\ncd $groupdir\n"            
            "placeholder loop text\n\n\n"
        )
        self.assertEqual(result, expected)


class ParamsToStringTest(unittest.TestCase):
    @mock.patch("gromax.output._ProcessAllGroups")
    def testParamsToString(self, mock_process):
        mock_process.return_value = "mock body"
        result = ParamsToString([[], []], "mytpr.tpr", "gmx mdrun", 3, "i", 15000, 10000)
        expected = "#!/bin/bash\n\ngmx='gmx mdrun'\ntpr=mytpr.tpr\nnsteps=15000\nresetstep=10000\nworkdir=`pwd`\n\n" + \
                   "#" * 80 + "\n\nmock body\n\nexit\n"
        self.assertEqual(result, expected)
