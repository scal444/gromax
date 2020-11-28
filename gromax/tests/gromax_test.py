import argparse
import logging
import unittest
import gromax.main as gmx


class SelectWorkflowTest(unittest.TestCase):
    def setUp(self):
        self.args = argparse.Namespace()

    def testGenerateMode(self):
        self.args.mode = "generate"
        workflow = gmx._selectWorkflow(self.args)
        self.assertEqual(workflow, gmx._executeGenerateWorkflow)

    def testExecuteMode(self):
        self.args.mode = "execute"
        workflow = gmx._selectWorkflow(self.args)
        self.assertEqual(workflow, gmx._executeExecuteWorkflow)

    def testAnalyzeMode(self):
        self.args.mode = "analyze"
        workflow = gmx._selectWorkflow(self.args)
        self.assertEqual(workflow, gmx._executeAnalyzeWorkflow)

    def testUnsupported(self):
        self.args.mode = "some_mode"
        with self.assertRaises(ValueError):
            gmx._selectWorkflow(self.args)


class SetLogLevelTest(unittest.TestCase):
    def setUp(self):
        self.logger = logging.getLogger("gromax")

    def testPassModes(self):
        gmx._setLoggingLevel(self.logger, "debug")
        gmx._setLoggingLevel(self.logger, "info")
        gmx._setLoggingLevel(self.logger, "silent")

    def testFailCase(self):
        with self.assertRaises(ValueError):
            gmx._setLoggingLevel(self.logger, "funky")
