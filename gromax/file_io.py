import os
import logging
from typing import Dict

# Typing definitons
# component index to log file path
trialContent = Dict[int, str]
# trial index to trial content
groupContent = Dict[int, trialContent]
# group index to group content
allDirectoryContent = Dict[int, groupContent]


# Extraction methods to get index of a folder or file.
def _splitAndGrabSuffix(path: str, splitter: str):
    """
        Splits a string and takes the suffix remainder.
    """
    split_path = path.split(splitter)
    if len(split_path) != 2:
        raise ValueError("Ambiguous split of path {} with splitter {}".format(path, splitter))
    return split_path[-1]


def _getGroupIndex(group: str) -> int:
    """
        Returns the 0-based index of a group ID. Input needs to be of the form /some/path/prefix/group_{num},
        where num is a 1-based group number.
    """
    return int(_splitAndGrabSuffix(group, "group_")) - 1


def _getTrialIndex(trial: str) -> int:
    """
        Returns the 0-based index of a trial ID. Input needs to be of the form /some/path/prefix/trial_{num},
        where num is a 1-based trial number.
    """
    return int(_splitAndGrabSuffix(trial, "trial_")) - 1


def _getComponentIndex(component: str) -> int:
    """
        Returns the 0-based index of a component ID. Input needs to be of the form /some/path/prefix/component_{num},
        where num is a 1-based component number.
    """
    return int(_splitAndGrabSuffix(component, "component_").split(".log")[0]) - 1


def _getGroupFoldersWithIndices(directory: str) -> Dict[int, str]:
    result: Dict[int, str] = {}
    folder_path: str
    for folder_path in os.listdir(directory):
        if "group_" not in folder_path:
            logging.getLogger("gromax").debug("Skipping folder {} - not a group folder".format(
                os.path.join(directory, folder_path)))
            continue
        try:
            result[_getGroupIndex(folder_path)] = os.path.join(directory, folder_path)
        except (TypeError, ValueError) as e:
            logging.getLogger("gromax").warning("Failed to parse {}: {}".format(directory + '/' + folder_path, e))

    return result


def _getTrialFoldersWithIndices(directory: str) -> Dict[int, str]:
    result: Dict[int, str] = {}
    folder_path: str
    for folder_path in os.listdir(directory):
        if "trial_" not in folder_path:
            logging.getLogger("gromax").debug("Skipping folder {} - not a trial folder".format(
                os.path.join(directory, folder_path)))
            continue
        try:
            result[_getTrialIndex(folder_path)] = os.path.join(directory, folder_path)
        except (TypeError, ValueError) as e:
            logging.getLogger("gromax").warning("Failed to parse {}: {}".format(directory + '/' + folder_path, e))
    return result


def _getComponentFoldersWithIndices(directory: str) -> Dict[int, str]:
    result: Dict[int, str] = {}
    file_path: str
    for file_path in os.listdir(directory):
        if not file_path.endswith(".log"):
            logging.getLogger("gromax").debug("Skipping file {} - not a log file".format(
                os.path.join(directory, file_path)))
            continue
        # Treat each subdirectory as a group directory, but some might not be so it's ok to fail.
        try:
            result[_getComponentIndex(file_path)] = os.path.join(directory, file_path)
        except (TypeError, ValueError) as e:
            logging.getLogger("gromax").warning("Failed to parse {}: {}".format(directory + '/' + file_path, e))
    return result


def parseDirectoryStructure(directory: str) -> allDirectoryContent:
    """
        Walks a directory tree and lists the log files within the structure as a nested dict, with the keys being
        0-based indices into the group, trial, or component, and the leaf values being component log file paths.
        TODO figure out how best to handle errors
        Expected dir structure is
            group_1
            group_1/trial_1
            group_1/trial_1/*component_1.log
            group_1/trial_1/*component_2.log
            group_1/trial_2/*component_1.log
            group_1/trial_2/*component_2.log
            group_2
            ...
         Resulting structure is:
         {
            // group
            0: {
                // trial
                0 : {
                    0: component_1_file_path
                    1: component_2_file_path
                }
                // trial
                1: {
                    ....
                }
            },
            // group
            1: {
                ....
            },
         }
    """
    result: allDirectoryContent = {}
    group_index: int
    group_dir: str
    for group_index, group_dir in _getGroupFoldersWithIndices(directory).items():
        group_result: groupContent = {}
        trial_index: int
        trial_dir: str
        for trial_index, trial_dir in _getTrialFoldersWithIndices(group_dir).items():
            group_result[trial_index] = {key: val for key, val in _getComponentFoldersWithIndices(trial_dir).items()}
        result[group_index] = group_result
    return result


def _maxItems(content: Dict):
    """
        Given a nested dictionary, determine the max number of items in the first subdictionary. So given,
        {
            1: {1,2,3},
            2: {3,4},
            3: {1}
        }
        this function will retun 3, as the first subdictionary had 3 items. Does not recursively nest, even if the
        items of the subdictionary are dictionaries themselves.
    """
    max_trials = 0
    for trials in content.values():
        if len(trials) > max_trials:
            max_trials = len(trials)
    return max_trials


def SanitizeDirectoryStructure(content: allDirectoryContent):
    """
        Logs missing trials, and purges trials with missing components.
    """
    max_trials = _maxItems(content)
    for group_idx, group in content.items():
        if len(group) < max_trials:
            logging.getLogger("gromax").warning(
                "Group {} has only {} trials, other groups have up to {}".format(group_idx, len(group), max_trials))
        max_components = _maxItems(group)
        # Can't use items() since we're dynamically changing the size of the dict on error cases.
        for trial_idx, trial in zip(list(group.keys()), list(group.values())):
            if len(trial) < max_components:
                logging.getLogger("gromax").warning(
                    "Group {} trial {} has only {} components, other trials have up to {}, discarding trial".format(
                        group_idx, trial_idx, len(trial), max_components))
                del group[trial_idx]
