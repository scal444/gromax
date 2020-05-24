import argparse
import logging
from typing import List, Iterable

# File constants.
_DESCRIPTION = "Some program description"
_EPILOG = "Some program epilogue"


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
    parser.add_argument('--gmx_version', type=str, help='Gromacs version - "2016", "2018", or "2019"')
    parser.add_argument("--run_file", type=str, help="path to bash benchmark script to create.")
    parser.add_argument("--directory", type=str, help="path to execution/analysis directory.")
    parser.add_argument("--version", action="version", version="alpha")
    parser.add_argument("--gmx_executable", type=str, default="gmx", help=(
        "gmx or gmx_mpi executable path. Defaults to 'gmx', which works if the executable is in your path."
    ))
    parser.add_argument("--trials_per_group", type=int, default=3, help="Number of times to run each parameter set.")
    parser.add_argument("--tpr", type=str, help="path to tpr file to benchmark.")
    # TODO add examples/documentation
    parser.add_argument("--cpu_ids", type=str, help="CPUs to be run on.")
    parser.add_argument("--gpu_ids", type=str, help="GPUs to be run on.")

    return parser


def _failWithError(err: str):
    logging.error(err)
    raise SystemExit(1)


def _checkArgs(args: argparse.Namespace) -> None:
    # TODO - some of these should only be required with certain modes
    good_modes: Iterable[str] = ("generate", "execute", "analyze")
    if args.mode not in good_modes:
        _failWithError("'mode' is a required positional argument - options are 'generate', 'execute', 'analyze'")
    good_versions: Iterable[str] = ("2016", "2018", "2019")
    if args.gmx_version not in good_versions:
        _failWithError("Invalid gmx version {}, must be one of {}".format(args.gmx_version, good_versions))
    if not args.cpu_ids:
        _failWithError("--cpu_ids is required")
    if not args.gpu_ids:
        _failWithError("--gpu_ids is required")
    if not args.run_file:
        _failWithError("--run_file argument is required")


def parseArgs(args: List[str]) -> argparse.Namespace:
    logging.info("Parsing args")
    parser: argparse.ArgumentParser = _buildParser()
    parsed_args: argparse.Namespace = parser.parse_args(args)
    _checkArgs(parsed_args)
    return parsed_args
