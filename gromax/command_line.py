import argparse
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

    return parser


# TODO type this
def _checkArgs():
    pass


def parseArgs(args: List[str]):
    parser: argparse.ArgumentParser = _buildParser()
    return parser.parse_args(args)
