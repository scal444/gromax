#!/usr/bin/python
import argparse
import logging
import os
import sys
from gromax.analysis import GromaxData, constructGromaxData, reportStatistics
from gromax.file_io import parseDirectoryStructure, allDirectoryContent, SanitizeDirectoryStructure
from gromax.combination_generator import createRunOptionsForConfigGroup, GenerateOptions
from gromax.command_line import checkArgs, parseArgs, parseIDString
from gromax.hardware_config import HardwareConfig, generateConfigSplitOptions
from gromax.output import ParamsToString, WriteRunScript
from typing import Callable, List, Dict
"""
    Command line entry point.
"""


def _populateGenerateOptions(args: argparse.Namespace) -> GenerateOptions:
    max_sims_per_gpu: int = 4 if args.generate_exhaustive_combinations else 2
    return GenerateOptions(max_sims_per_gpu=max_sims_per_gpu,
                           generate_exhaustive_options=args.generate_exhaustive_combinations)


def _executeGenerateWorkflow(args: argparse.Namespace) -> None:
    logger: logging.Logger = logging.getLogger("gromax")
    logger.info("Generating run options.")
    # Assign hardware config
    cpu_ids: List[int] = parseIDString(args.cpu_ids)
    logger.info("CPU IDs: {}".format(cpu_ids))
    num_cpus: int = len(cpu_ids)
    if num_cpus % 2 == 1:
        logger.warning("Detected an odd number of CPU IDs ({}), this is atypical.".format(num_cpus))
    gpu_ids: List[int] = parseIDString(args.gpu_ids)
    logger.info("GPU IDs: {}".format(gpu_ids))
    num_gpus: int = len(gpu_ids)
    modval: int = num_cpus % num_gpus
    if modval != 0:
        logger.warning("Number of CPUs({}) is not divisible by the number of GPUs({}), will only use {} CPUs.".format(
            num_cpus, num_gpus, num_cpus - modval))
        cpu_ids = cpu_ids[:-modval]
    hw_config: HardwareConfig = HardwareConfig(cpu_ids=cpu_ids, gpu_ids=gpu_ids)

    generate_options: GenerateOptions = _populateGenerateOptions(args)
    if args.single_sim_only:
        config_splits: List[List[HardwareConfig]] = [[hw_config]]
    else:
        config_splits: List[List[HardwareConfig]] = generateConfigSplitOptions(
            hw_config, max_sims_per_gpu=generate_options.max_sims_per_gpu)
    logger.debug("Generated {} hardware config breakdowns".format(len(config_splits)))
    run_opts: List[List[Dict]] = []
    for config_split in config_splits:
        run_opts.extend(createRunOptionsForConfigGroup(config_split, args.gmx_version, generate_options))
    # Serialize options.
    out_file: str = args.run_file
    # TODO Make this configurable and robust
    gmx: str = args.gmx_executable + " mdrun"
    tpr: str = args.tpr
    num_trials: int = args.trials_per_group
    WriteRunScript(out_file, ParamsToString(run_opts, tpr, gmx, num_trials))


def _executeAnalyzeWorkflow(args: argparse.Namespace) -> None:
    logger: logging.Logger = logging.getLogger("gromax")
    folder: str = args.directory
    if folder is None:
        logger.info("No directory specified using --directory, using current directory.")
        folder = os.getcwd()
    if not os.path.isdir(folder):
        logger.error("Analysis path {} is not a directory".format(folder))
        sys.exit(1)
    logger.info("Analyzing gromax run results in directory {}.".format(folder))
    directory_content: allDirectoryContent = parseDirectoryStructure(folder)
    if len(directory_content) == 0:
        logger.error("Analysis path {} contains no results in gromax format, exiting.".format(folder))
        sys.exit(1)
    SanitizeDirectoryStructure(directory_content)
    result_data: GromaxData = constructGromaxData(directory_content)
    sys.stdout.write(reportStatistics(result_data.groupStatistics()))


def _executeExecuteWorkflow(_: argparse.Namespace) -> None:
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


def _setLoggingLevel(logger: logging.Logger, log_level: str):
    fmt: str = '%(levelname)-8s%(message)s'
    if log_level == "info":
        logger.setLevel(logging.INFO)
    elif log_level == "debug":
        logger.setLevel(logging.DEBUG)
        fmt = '%(levelname)-8s [%(filename)s:%(lineno)d] %(message)s'
    # We don't use fatal, so this should not log anything.
    elif log_level == "silent":
        logger.setLevel(logging.FATAL)
    else:
        raise ValueError("Log level {} does not exist.".format(log_level))
    formatter = logging.Formatter(fmt)
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)


def gromax():
    logger: logging.Logger = logging.getLogger("gromax")
    parsed_args: argparse.Namespace = parseArgs(sys.argv[1:])
    _setLoggingLevel(logger, parsed_args.log_level)
    checkArgs(parsed_args)
    logger.info("Executing gromax.")
    workflow: Callable[[argparse.Namespace], None] = _selectWorkflow(parsed_args)
    workflow(parsed_args)
    sys.exit(0)


if __name__ == "__main__":
    gromax()
