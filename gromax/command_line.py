import argparse
import logging
from typing import List, Iterable

# File constants.
_DESCRIPTION = "Gromax is a tool to build benchmarking scripts for Gromax and analyze the results. \n" \
               "Generate scripts with the 'gromax generate' command, and analyze results with 'gromax analyze'."
_EPILOG = "For more details on parameters and usage, visit https://github.com/scal444/gromax/docs\n"


def parseIDString(ids: str) -> List[int]:
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
    except (TypeError, ValueError):
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


def _buildParser() -> argparse.ArgumentParser:
    """
        Constructs and returns the argument parser for gromax.
    """
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description=_DESCRIPTION, epilog=_EPILOG)
    parser.add_argument('mode', type=str, help='The gromax operation to run. "generate", "execute", or "analyze"')

    generate_group = parser.add_argument_group("generate", "arguments for 'gromax generate'")
    generate_group.add_argument('--gmx_version', type=str, metavar="",
                                help='Gromacs version - "2016", "2018", "2019", or "2020"', )
    generate_group.add_argument("--run_file", type=str, help="Path to bash benchmark script to create.",
                                default="benchmark.sh", metavar="")
    generate_group.add_argument("--gmx_executable", type=str, default="gmx", metavar="", help=(
        "gmx or gmx_mpi executable path. Defaults to 'gmx', which works if the executable is in your path."
    ))
    generate_group.add_argument("--trials_per_group", type=int, default=3, metavar="",
                                help="Number of times to run each parameter set.")
    generate_group.add_argument("--tpr", type=str, help="Path to the tpr file to benchmark.", metavar="")
    generate_group.add_argument("--cpu_ids", type=str, help="CPUs to be run on.", metavar="", default="")
    generate_group.add_argument("--gpu_ids", type=str, help="GPUs to be run on.", metavar="", default="")
    generate_group.add_argument("--num_cpus", type=int, metavar="",
                                help="Number of CPUs to run on, indexed from 0. Use this option OR --cpu_ids (if not "
                                     "using all CPUs on the node), but not both.", default=0)
    generate_group.add_argument("--num_gpus", type=int, metavar="",
                                help="Number of GPUs to run on, indexed from 0. Use this option OR --gpu_ids (if not "
                                     "using all GPUs on the node), but not both.", default=0)
    generate_group.add_argument("--single_sim_only", action="store_true",
                                help="If set, do not divide the hardware among multiple concurrent simulations")
    analyze_group = parser.add_argument_group("analyze", "arguments for 'gromax analyze'")
    analyze_group.add_argument("--directory", type=str, help="Path to execution/analysis directory.", metavar="")
    parser.add_argument("--version", action="version", version="alpha")
    parser.add_argument("--log_level", type=str, default="info", metavar="",
                        help="Set logging verbosity - 'silent', 'info'(default), or 'debug'")
    return parser


def _failWithError(err: str):
    logging.getLogger("gromax").error(err)
    raise SystemExit(1)


def _checkGenerateArgs(args: argparse.Namespace) -> None:
    good_versions: Iterable[str] = ("2016", "2018", "2019", "2020")
    if args.gmx_version not in good_versions:
        _failWithError("Invalid gmx version {}, must be one of {}".format(args.gmx_version, good_versions))
    if not args.cpu_ids and not args.num_cpus:
        _failWithError("One of --cpu_ids or --num_cpus is required")
    if args.num_cpus:
        if args.cpu_ids:
            _failWithError("Cannot specify both --cpu_ids and --num_cpus")
        args.cpu_ids = ",".join([str(identifier) for identifier in range(args.num_cpus)])
    if not args.gpu_ids and not args.num_gpus:
        _failWithError("One of --gpu_ids or --num_gpus is required")
    if args.num_gpus:
        if args.gpu_ids:
            _failWithError("Cannot specify both --gpu_ids and --num_gpus")
        args.gpu_ids = ",".join([str(identifier) for identifier in range(args.num_gpus)])


def checkArgs(args: argparse.Namespace) -> None:
    good_modes: Iterable[str] = ("generate", "execute", "analyze")
    if args.mode not in good_modes:
        _failWithError("'mode' is a required positional argument - options are 'generate', 'execute', 'analyze'")

    if args.mode == "generate":
        _checkGenerateArgs(args)


def parseArgs(args: List[str]) -> argparse.Namespace:
    parser: argparse.ArgumentParser = _buildParser()
    parsed_args: argparse.Namespace = parser.parse_args(args)
    return parsed_args
