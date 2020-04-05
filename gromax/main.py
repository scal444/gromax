#!/usr/bin/python
import argparse
import logging
import sys
from gromax.combination_generator import createRunOptionsForConfigGroup
from gromax.command_line import parseArgs
from gromax.hardware_config import HardwareConfig, generateConfigSplitOptions
from gromax.output import ParamsToString, WriteRunScript
from typing import Callable, List, Dict
"""
    Command line entry point.
"""


def _parseIDString(ids: str) -> List[int]:
    """
        Parses a string to determine CPU or GPU IDs. Handles the following formats:

        Comma separated integers
            0,1,2,3
        Colon or dashed range
            0:31
            0-31
        Colon range with stride
            0:2:31 == 0,2,4,....,30
    """
    try:
        return [int(ids)]
    except ValueError:
        pass

    if ',' in ids:
        return [int(i) for i in ids.split(',')]
    elif '-' in ids:
        split: List[str] = ids.split("-")
        if len(split) == 2:
            return list(range(int(split[0]), int(split[1]) + 1))
    elif ':' in ids:
        split: List[str] = ids.split(":")
        stride: int = 1
        if len(split) == 3:
            stride = int(split[1])
        if len(split) == 2 or len(split) == 3:
            # This takes the first and last part of the split, handling size 2 and 3.
            return list(range(int(split[0]), int(split[-1]) + 1, stride))
    raise ValueError("Invalid ID string '{}'".format(ids))


def _executeGenerateWorkflow(args: argparse.Namespace) -> None:
    logging.info("Generating run options.")
    # Assign hardware config
    hw_config: HardwareConfig = HardwareConfig(cpu_ids=_parseIDString(args.cpu_ids),
                                               gpu_ids=_parseIDString(args.gpu_ids))
    # generate options
    config_splits: List[List[HardwareConfig]] = generateConfigSplitOptions(hw_config)
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
    raise NotImplementedError("Analysis not yet supported")


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
    logging.basicConfig(level=logging.INFO)
    logging.info("Executing gromax.")
    parsed_args: argparse.Namespace = parseArgs(sys.argv[1:])
    workflow: Callable[[argparse.Namespace], None] = _selectWorkflow(parsed_args)
    workflow(parsed_args)
    sys.exit(0)


if __name__ == "__main__":
    gromax()
