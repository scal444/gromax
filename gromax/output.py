import logging
import os
from copy import deepcopy
from gromax.combination_generator import ParameterSet, ParameterSetGroup
from typing import Any, List

# TODO make ntrials a top-level parameter
# TODO turn group_1, group_2... to group_${group}


def _serializeParams(params: ParameterSet, prepend: str = None) -> str:
    """
        Turn dictionary of parameters into a string. Orders based on internal python sorting of keys. If the gmx
        parameter is specified, will prepend the contents.

        Note that this is specifically for gromacs parameters, and will append single dashes to keywords, so
        {"ntomp": 80} as input will yield a string '-ntomp 80'
    """
    kvs: List[str] = []
    if prepend:
        kvs.append(prepend)
    for key in sorted(params):
        val: Any = params[key]
        if val is not False:
            kvs.append("-" + key)
        # Have to be careful about types here - 0 can be a value we want to pass. Append if the value exists and
        # is not boolean.
        if val is not None and not isinstance(val, bool):
            kvs.append(str(val))

    return " ".join(kvs)


def _serializeConcurrentGroup(param_group: ParameterSetGroup, prepend: str = None) -> str:
    """
        Turn a concurrent group of parameters into a line separated bash string, with ampersands to send the initial
        processes to background for concurrent execution.

        Optionally will prepend/append contents of prepend/append variables to each line.
    """
    param_lines: List[str] = []
    for params in param_group:
        param_lines.append(_serializeParams(params, prepend))
    return " &\n".join(param_lines)


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


def _injectFileNaming(param_group: ParameterSetGroup, group_placeholder: str = "${group}",
                      trial_placeholder: str = "${i}"):
    for component_ID, param in enumerate(param_group):
        param["deffnm"] = "group_{}_trial_{}_component_{}".format(group_placeholder, trial_placeholder,
                                                                  1 + component_ID)


def _injectTpr(param_group: ParameterSetGroup, placeholder: str = "${tpr}"):
    for params in param_group:
        params["s"] = placeholder


def _injectTiming(param_group: ParameterSetGroup, nsteps: str, resetstep: str):
    for params in param_group:
        params["nsteps"] = nsteps
        params["resetstep"] = resetstep


def _addDirectoryHandling(params: str, workdir: str = "${groupdir}", trial_placeholder: str = "${i}") -> str:
    return "\n".join([
        "trialdir={}/trial_{}\nmkdir $trialdir\ncd $trialdir".format(workdir, trial_placeholder),
        params,
        "cd {}".format(workdir)
    ])


def _wrapInLoop(serialized_group: str, loop_variable: str, tab_increment=2) -> str:
    """
        Creates a bash for loop around a string, with the format

        for <loop_variable> in $( seq 1 <count>); do
          <tab_increment amount> line1
          <tab_increment amount> line2
         done

         Note that 'count' can be a variable.
    """
    base: str = "for {:s} in $(seq 1 ${{ntrials}}); do".format(loop_variable)
    tabbed_lines: str = _incrementLines(serialized_group, tab_increment)
    return "\n".join((base, tabbed_lines, "done"))


def _ProcessSingleGroup(param_group: ParameterSetGroup, gmx: str, loop_var: str,
                        resetstep: str, nsteps: str, tab_increment: int) -> str:
    param_group_copy: ParameterSetGroup = deepcopy(param_group)
    _injectTpr(param_group_copy)
    _injectFileNaming(param_group_copy)
    _injectTiming(param_group_copy, nsteps, resetstep)
    serialized: str = _serializeConcurrentGroup(param_group_copy, prepend=gmx) + "\nwait"
    serialized_with_dir_handling: str = _addDirectoryHandling(serialized, )
    return _wrapInLoop(serialized_with_dir_handling, loop_var, tab_increment=tab_increment)


def _ProcessAllGroups(groups: List[ParameterSetGroup], loop_variable: str, gmx: str,
                      nsteps: str = "${nsteps}", resetstep: str = "${resetstep}", tab_increment: int = 2) -> str:
    """
        Creates the body of a bash script to run groups of concurrent gromacs simulations. Each group is wrapped in
        a loop.
    """
    result: str = ""
    for i, group in enumerate(groups):
        group_num: int = i + 1
        result += "group={}\n".format(group_num)
        result += "groupdir=$workdir/group_${group}\n"
        result += "mkdir $groupdir\n"
        result += "cd $groupdir\n"
        result += _ProcessSingleGroup(group, gmx, loop_variable, nsteps=nsteps, resetstep=resetstep,
                                      tab_increment=tab_increment)
        result += "\n\n\n"
    return result


def _addHeader(gmx: str, tpr: str, nsteps: int, num_trials: int, resetstep: int) -> str:
    return "#!/bin/bash\n\ngmx='{}'\ntpr={}\nnsteps={}\nresetstep={}\nntrials={}\nworkdir=`pwd`".format(
        gmx, tpr, nsteps, num_trials, resetstep)


def ParamsToString(groups: List[ParameterSetGroup], tpr: str, gmx: str, num_trials: int,
                   loop_var: str = "i", nsteps: int = 15000, resetstep: int = 10000, tab_increment: int = 2) -> str:
    result: str = _addHeader(gmx, tpr, nsteps, resetstep, num_trials)
    result += "\n\n" + "#" * 80 + "\n\n"
    result += _ProcessAllGroups(groups, loop_var, "$gmx", tab_increment=tab_increment)
    result += "\n\nexit\n"
    return result


def WriteRunScript(file: str, content: str):
    """
        Writes out the script to execute gromacs.
    """
    logger: logging.Logger = logging.getLogger()
    path: str = os.path.abspath(file)
    try:
        with open(path, 'wt') as fout:
            logger.info("Writing run run script to {}".format(path))
            fout.write(content)
    except IOError as e:
        logger.error("Unable to open file for writing: {}".format(e))
        raise SystemExit(1)
