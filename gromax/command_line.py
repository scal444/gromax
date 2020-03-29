import argparse
import logging
from typing import List

# File constants.
_DESCRIPTION = "Some program description"
_EPILOG = "Some program epilogue"


def _buildParser() -> argparse.ArgumentParser:
    """
        Constructs and returns the argument parser for gromax.
    """
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description=_DESCRIPTION, epilog=_EPILOG)
    parser.add_argument('mode', type=str, help='The gromax operation to run. "generate", "execute", or "analyze"',
                        choices=("generate", "execute", "analyze"))
    parser.add_argument('--gmx_version', type=str, help='Gromacs version - "2016", "2017", "2018", or "2019"',
                        choices=("2016", "2018", "2019", "2020"))
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


# TODO type this
def _checkArgs(args: argparse.Namespace) -> None:
    pass


def parseArgs(args: List[str]) -> argparse.Namespace:
    logging.info("Parsing args")
    parser: argparse.ArgumentParser = _buildParser()
    parsed_args: argparse.Namespace = parser.parse_args(args)
    _checkArgs(parsed_args)
    return parsed_args
