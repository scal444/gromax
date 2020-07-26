#!/usr/bin/python
import argparse
import logging
import os
import sys
from gromax.analysis import GromaxData, constructGromaxData, reportStatistics
from gromax.file_io import parseDirectoryStructure, allDirectoryContent
from gromax.combination_generator import createRunOptionsForConfigGroup
from gromax.command_line import parseArgs, parseIDString
from gromax.hardware_config import HardwareConfig, generateConfigSplitOptions
from gromax.output import ParamsToString, WriteRunScript
from typing import Callable, List, Dict
"""
    Command line entry point.
"""


def _executeGenerateWorkflow(args: argparse.Namespace) -> None:
    logging.info("Generating run options.")
    # Assign hardware config
    cpu_ids: List[int] = parseIDString(args.cpu_ids)
    logging.info("CPU IDs: {}".format(cpu_ids))
    gpu_ids: List[int] = parseIDString(args.gpu_ids)
    logging.info("GPU IDs: {}".format(gpu_ids))
    hw_config: HardwareConfig = HardwareConfig(cpu_ids=cpu_ids, gpu_ids=gpu_ids)
    # generate options
    config_splits: List[List[HardwareConfig]] = generateConfigSplitOptions(hw_config)
    logging.debug("Generated {} hardware config breakdowns".format(len(config_splits)))
    run_opts: List[List[Dict]] = []
    for config_split in config_splits:
        run_opts.extend(createRunOptionsForConfigGroup(config_split, args.gmx_version))
    # Serialize options.
    out_file: str = args.run_file
    # TODO Make this configurable and robust
    gmx: str = args.gmx_executable + " mdrun"
    tpr: str = args.tpr
    num_trials: int = args.trials_per_group
    WriteRunScript(out_file, ParamsToString(run_opts, tpr, gmx, num_trials))


def _executeAnalyzeWorkflow(args: argparse.Namespace) -> None:
    folder: str = args.directory
    if folder is None:
        logging.info("No directory specified using --directory, using current directory.")
        folder = os.getcwd()
    if not os.path.isdir(folder):
        logging.error("Analysis path {} is not a directory".format(folder))
        sys.exit(1)
    logging.info("Analyzing gromax run results in directory {}.".format(folder))
    directory_content: allDirectoryContent = parseDirectoryStructure(folder)
    result_data: GromaxData = constructGromaxData(directory_content)
    sys.stdout.write(reportStatistics(result_data.groupStatistics()))


def _executeExecuteWorkflow(args: argparse.Namespace) -> None:
    raise NotImplementedError("Direct execution not yet supported.")


def _selectWorkflow(args: argparse.Namespace) -> Callable[[argparse.Namespace], None]:
    mode: str = args.mode
    if mode == "generate":
        return _executeGenerateWorkflow
    if mode == "execute":
        return _executeExecuteWorkflow
    if mode == "analyze":
        return _executeAnalyzeWorkflow
    raise ValueError("Workflow '{}' does not exist".format(mode))


def gromax():
    # logging.basicConfig(level=logging.INFO)
    # debug logging
    logging.basicConfig(level=logging.DEBUG, format='%(levelname)-8s [%(filename)s:%(lineno)d] %(message)s')

    logging.info("Executing gromax.")
    parsed_args: argparse.Namespace = parseArgs(sys.argv[1:])
    workflow: Callable[[argparse.Namespace], None] = _selectWorkflow(parsed_args)
    workflow(parsed_args)
    sys.exit(0)


if __name__ == "__main__":
    gromax()
