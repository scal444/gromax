import re

from typing import List, Callable, Dict, Iterable, Optional, Union, Type
"""
    Gromacs log parsing functionality.

    TODO: add
        -gromacs version and binary info
        -non-specified parameters
        -subcounters
"""

# Input/output format for a regex op. Regex ops return a dictionary of found values, or None if the op fails
# to match.
regexOp = Callable[[str], Optional[Dict]]

# Possible data types for a command line parameter
valueType = Union[float, str, bool, int]

# regex for gromacs log full command line argument.
_COMMAND_LINE_RE = r"^Command line:(.)*\n(.)+\n"

def _getCommandLine(contents: str) -> Optional[str]:
    """
        Parses text for the line with reported CLI input.
    """
    search = re.search(_COMMAND_LINE_RE, contents, flags=re.MULTILINE)
    if search is None:
        return search
    return search.group().split("\n")[1]

def _typeOfParam(param: str) -> Type:
    """
        Returns the expected type of the corresponding value or a parameter key.

        Examples:
            _typeOfParam(ntomp) -> int
            _typeOfParam(mahx) ->  float

        Raises:
            ValueError, for unknown key
    """
    types: Dict = {
        "ntmpi": int,
        "ntomp": int,
        "nsteps": int,
        "nstlist": int,
        "nt": int,
        "resetstep": int,

        "bonded": str,
        "deffnm": str,
        "g": str,
        "gputasks": str,
        "nb": str,
        "pin": str,
        "pinoffset": str,
        "pinstride": str,
        "pme": str,
        "s": str,
        "update": str,

        "maxh": float,

        "noconfout": bool,
        "resethway": bool,
        "v": bool

    }
    try:
        return types[param]
    except KeyError:
        raise ValueError("Invalid gromacs paramter: {}".format(param))


def _convert(val: str, val_type: Type) -> valueType:
    """
        Processes raw string value into desired type.
    """
    if val_type == str:
        return val
    if val_type == int:
        return int(val)
    if val_type == float:
        return float(val)
    # Presence of the key indicates that this flag is turned on.
    if val_type == bool:
        return True
    raise ValueError("Unexpected type input {} for value".format(val_type, val))


def _commandInputRegexOp(contents: str) -> Optional[Dict]:
    """
        Searches for and parses the explicit command line options used to invoke gromacs. This occurs near
        the top of the log file and has the form

        Command line:
        gmx mdrun ........

        Returns a dictionary of key-vals with appropriate data types for the values. Returns None if the command
        line regex is not found.

        Raises ValueError for an unexpected key or malformed value.
    """

    line: Optional[str] = _getCommandLine(contents)
    if line is None:
        return line

    result: Dict = {}

    # Trim off the first part of the string containing gmx/gmx_mpi mdrun
    # Note that if there are no -dash parameters this will be empty and we return an empty dict.
    split: List[str] = line.split("-")[1:]
    for item in split:
        # Some parameters have values, others don't
        try:
            key, val = item.strip().split(" ")
        except ValueError:
            key, val = item.strip(), None

        val_type: Type = _typeOfParam(key)
        result[key] = _convert(val, val_type)
    return result


def _fullCommandRegexOp(contents: str) -> Optional[Dict[str, str]]:
    line: Optional[str] = _getCommandLine(contents)
    if line is None:
        return line
    return {"full_command_line": line}


def _performanceRegexOp(contents: str) -> Optional[Dict]:
    search = re.search(r"Performance:\s+\d+\.\d+", contents)
    if search is not None:
        return {"performance": float(search.group().split()[1])}
    return None


class LogParser(object):
    """
        An object with a list of regex operations to perform on any input string.
        TODO add a failure handler with configurable severity level
    """
    def __init__(self, ops: Iterable[regexOp] = ()):
        """
            Can specify ops in the constructor or with addOp.
        """
        self._operations: List[regexOp] = []
        for op in ops:
            self._operations.append(op)

    def addOp(self, op: regexOp):
        """
            Append an operation to the list.
        """
        self._operations.append(op)

    def parse(self, contents: str) -> Dict:
        """
            Apply all regex ops registered to the string, return in dict format.
        """
        result: Dict = {}
        for op in self._operations:
            op_match: Optional[Dict] = op(contents)
            if op_match is None:
                self._handleFailure()
            else:
                result.update(op_match)
        return result

    def _handleFailure(self):
        pass


def BasicParser() -> LogParser:
    parser: LogParser = LogParser(ops=(_commandInputRegexOp, _performanceRegexOp, _fullCommandRegexOp))
    return parser
