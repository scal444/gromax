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
