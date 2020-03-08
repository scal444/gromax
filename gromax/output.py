from gromax.combination_generator import ParameterSet
from typing import Any


def _serializeParams(params: ParameterSet) -> str:
    """
        Turn dictionary of parameters into a string. Orders based on internal python sorting of keys.

        Note that this is specifically for gromacs parameters, and will append single dashes to keywords, so
        {"ntomp": 80} as input will yield a string '-ntomp 80'
    """
    kvs = []
    for key in sorted(params):
        val: Any = params[key]
        if val is not False:
            kvs.append("-" + key)
        # Have to be careful about types here - 0 can be a value we want to pass. Append if the value exists and
        # is not boolean.
        if val is not None and not isinstance(val, bool):
            kvs.append(str(val))

    return " ".join(kvs)
