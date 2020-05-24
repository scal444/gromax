import logging
import math
import re
# import pandas as pd
from gromax.file_io import allDirectoryContent
from gromax.log_parser import BasicParser
from typing import Dict, List, Union, Optional, Any, Callable
from copy import deepcopy

# Possible data types.
dataPoint = Union[int, float, str, bool]

# The base unit of results is a dictionary. This dict holds parameters for an individual run,
# as well as simulation performance. This level is flat, in that there is no more nesting.
# Parameters are strings.
singleRunData = Dict[str, dataPoint]

# Per-component results of a trial
singleTrialData = Dict[int, singleRunData]

# Per-trial results of a group
singleGroupData = Dict[int, singleTrialData]

# Comprehensive data set
allData = Dict[int, singleGroupData]

# Compiled statistics and run commands for a group result
groupStats = Dict[str, Any]


def standardError(vals: List[float]):
    """
        Calculates the standard error of the mean of a data set.
    """
    if not vals or len(vals) < 2:
        return 0
    mean = sum(vals) / len(vals)
    squared_error = 0
    for val in vals:
        squared_error += (mean - val) ** 2
    standard_deviation = math.sqrt(squared_error / (len(vals) - 1))
    return standard_deviation / math.sqrt(len(vals))


def _shareKeyVal(key: str, a: Dict, b: Dict) -> bool:
    """
        Returns true if both dictionaries have the same key:val pair
    """
    try:
        return a[key] == b[key]
    except KeyError:
        return False


def _commonKeyVals(a: Dict, b: Dict) -> Dict:
    # Return the intersect of two dictionaries.
    return {key: val for key, val in a.items() if _shareKeyVal(key, a, b)}


def _collect():
    pass


def _differingKeys(a: Dict, b: Dict) -> Dict[List, Any]:
    """
        Given two dictionaries, returns a list of keys that are different between them.

        Assumes that keys are identical between dicts.
    """

    result: Dict[List[Any]] = {}
    for key, val in a.items():
        pass
    return result


def _getGroupRunString(group: singleGroupData) -> str:
    lines: List[str] = []
    for key in sorted(group[0].keys()):
        component: singleRunData = group[0][key]
        lines.append(component["full_command_line"])
    return " &\n".join(lines)


def _calculateTrialPerformance(trial: singleTrialData) -> float:
    components_sum: float = 0
    for _, component_content in trial.items():
        assert "performance" in component_content.keys()
        component_perf: float = component_content["performance"]
        assert isinstance(component_perf, float)
        components_sum += component_perf
    return components_sum


def _analyzeGroupData(group: singleGroupData) -> groupStats:
    trial_performances: List[float] = [_calculateTrialPerformance(trial) for trial in group.values()]
    return {
        "command_string": _getGroupRunString(group),
        "performance":  sum(trial_performances) / float(len(trial_performances)),
        # take number of sims per trial from first trial.
        "concurrent_sims": len(group[0])
    }


class GromaxData(object):
    def __init__(self, data: Optional[allData] = None):
        self._data: allData = {}
        if data:
            self._data = data

    def insertDataPoint(self, group: int, trial: int, component: int, key: str, data_point: dataPoint):
        if group not in self._data:
            self._data[group]: singleGroupData = {}
        if trial not in self._data[group]:
            self._data[group][trial]: singleTrialData = {}
        if component not in self._data[group][trial]:
            self._data[group][trial][component]: singleTrialData = {}
        self._data[group][trial][component][key]: dataPoint = data_point

    @property
    def data(self) -> allData:
        """
            Returns a copy of the internal data format.
        """
        return deepcopy(self._data)

    @data.setter
    def data(self, data) -> None:
        self._data = data

    # def asDataFrame(self, detail_level: str = "per_group") -> pd.DataFrame:
    #     pass

    def groupStatistics(self) -> Dict[int, groupStats]:
        results: Dict[int, groupStats] = {}
        for group_index, group_content in self._data.items():
            results[group_index] = _analyzeGroupData(group_content)
        return results


def constructGromaxData(directory_structure: allDirectoryContent) -> GromaxData:
    data: GromaxData = GromaxData()
    parser: BasicParser = BasicParser()
    for group_index, group_content in directory_structure.items():
        for trial_index, trial_content in group_content.items():
            for component_index, component_file in trial_content.items():
                try:
                    with open(component_file, 'r') as fin:
                        contents: str = fin.read()
                except IOError as e:
                    logging.warning("Unable to open log file {}: {}".format(component_file, e))
                    continue
                extracted_elements: Dict[str, dataPoint] = parser.parse(contents)
                for key, val in extracted_elements.items():
                    data.insertDataPoint(group_index, trial_index, component_index, key, val)
    return data


def _defaultConstraint(_: groupStats) -> bool:
    return True


def _singleSimConstraint(data: groupStats) -> bool:
    return data["concurrent_sims"] == 1


def _bestWithConstraint(data: Dict[int, groupStats],
                        constraint: Callable[[groupStats], bool] = _defaultConstraint) -> groupStats:
    best: groupStats = {"performance": 0.0}
    for group in data.values():
        if constraint(group) and group["performance"] >= best["performance"]:
            best = group
    assert best["performance"] > 0.0
    return best


def _formatHeader(header: str) -> str:
    return "\n".join(["-" * len(header), header, "-" * len(header)])


def _sanitizeCommand(commands: str) -> str:
    """
        Strips out unneeded info from command string, including:

        -nsteps
        -resetstep
        -group_trial_ prefixes for deffnm
        -tpr name changed to $tpr
        -noconfout
    """
    commands = re.sub(r'group_[0-9]+_trial_[0-9]+_component_', 'replicate_', commands)
    commands = re.sub(r'-resetstep [0-9]+ ', '', commands)
    commands = re.sub(r'-nsteps [0-9]+ ', '', commands)
    commands = re.sub(r'-s .*\b', '-s $tpr', commands)
    commands = re.sub(r'-noconfout ', '', commands)
    return commands


def _reportGrouping(stat: groupStats) -> str:
    combined_result: str = "Aggregate performance: {:.2f} ns/day\nCommand line:\n{:s}".format(stat["performance"],
                                                                                              stat["command_string"])
    combined_result = _sanitizeCommand(combined_result)
    # Add indentation
    return "  " + "\n  ".join(combined_result.split("\n"))


def reportStatistics(stats: Dict[int, Dict[str, Any]]) -> str:
    total_best: groupStats = _bestWithConstraint(stats)
    best_single_sim: groupStats = _bestWithConstraint(stats, constraint=_singleSimConstraint)
    return "\n".join([
        _formatHeader("Highest throughput combination"),
        _reportGrouping(total_best),
        _formatHeader("Best single simulation"),
        _reportGrouping(best_single_sim)
    ])
