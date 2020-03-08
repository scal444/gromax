from gromax.combination_generator import ParameterSet, ParameterSetGroup
from typing import Any, List


def _serializeParams(params: ParameterSet, gmx: str = None) -> str:
    """
        Turn dictionary of parameters into a string. Orders based on internal python sorting of keys. If the gmx
        parameter is specified, will prepend the contents.

        Note that this is specifically for gromacs parameters, and will append single dashes to keywords, so
        {"ntomp": 80} as input will yield a string '-ntomp 80'
    """
    kvs: List[str] = []
    if gmx:
        kvs.append(gmx)
    for key in sorted(params):
        val: Any = params[key]
        if val is not False:
            kvs.append("-" + key)
        # Have to be careful about types here - 0 can be a value we want to pass. Append if the value exists and
        # is not boolean.
        if val is not None and not isinstance(val, bool):
            kvs.append(str(val))

    return " ".join(kvs)


def _serializeConcurrentGroup(param_group: ParameterSetGroup, gmx: str = None) -> str:
    """
        Turn a concurrent group of parameters into a line separated bash string, with ampersands to send the initial
        processes to background for concurrent execution.

        Optionally will prepend contents of gmx to each line.
    """
    param_lines: List[str] = []
    for params in param_group:
        param_lines.append(_serializeParams(params, gmx))
    return "&\n".join(param_lines)


def _incrementLines(lines: str, amount: int) -> str:
    """
        Takes a string and pads each line with 'amount' additional spaces.
        If input is empty, returns empty string.

        Raises ValueError if negative input.
    """
    if amount < 0:
        raise ValueError("Cannot pad with a negative number of spaces - amount requested={}".format(amount))
    if not len(lines):
        return ""

    joiner: str = "\n" + " " * amount
    padded_lines: str = joiner.join(lines.split("\n"))
    # Need to handle first line separately
    return " " * amount + padded_lines


def _wrapInLoop(serialized_group: str, loop_variable: str, count: Any, tab_increment=2) -> str:
    """
        Creates a bash for loop around a string, with the format

        for <loop_variable> in {1...<count}; do
          <tab_increment amount> line1
          <tab_increment amount> line2
         done

         Note that 'count' can be a variable.
    """
    base: str = "for {:s} in {{1..{}}}; do".format(loop_variable, count)
    tabbed_lines: str = _incrementLines(serialized_group, tab_increment)
    return "\n".join((base, tabbed_lines, "done"))


def _SerializeAllGroups(groups: List[ParameterSetGroup]) -> str:
    pass
