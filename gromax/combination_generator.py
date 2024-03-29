import math

from dataclasses import dataclass

from gromax.constants import _SUPPORTED_GMX_VERSIONS
from gromax.hardware_config import HardwareConfig
from copy import deepcopy
from typing import List, Dict, Any, Callable

# Convenience definitions
# A grouping of GPU ids.
GpuIds = List[int]
# Dictionary representing the options for a single gromacs command line run.
ParameterSet = Dict
# List of dictionaries representing a set of Gromacs commands to be run concurrently.
ParameterSetGroup = List[ParameterSet]
# A breakdown of hardware configs (presumably adding to the full config) for gromacs runs to run on concurrently.
HardwareConfigBreakdown = List[HardwareConfig]


@dataclass
class GenerateOptions:
    """
        Consolidated options for parameter combination generation.
    """
    max_sims_per_gpu: int = 4
    max_ranks_for_pme_gpu: int = 8
    generate_exhaustive_options: bool = True


def genNtmpiOptions(total_procs: int, num_gpus: int, max_ranks_per_gpu: int = 4) -> List[int]:
    """
        Breaks down the possible combinations of ntmpi for the given number of GPUs. For example, with
        2 GPUs and 6 CPUs, the combinations are:
            ntmpi = 2, ntomp = 3, with the 1st GPU assigned to the first rank, and 2nd to the 2nd rank
            ntmpi = 6, ntomp = 1, with the first GPU split among the first 3 ranks and so on.

            Note that in this example ntmpi=3 does not work, because you can't eveny split 2 GPUs among
            3 ranks.

        If passed with no GPUs, returns a size one list with the number of processors, as non-GPU simulations
        should maximize thread counts.
    """
    if total_procs <= 0:
        raise ValueError("Numbers need to be positive, total_procs = {}".format(total_procs))
    if num_gpus <= 0:
        return [total_procs]
    curroption: int = num_gpus
    options: List[int] = []
    while curroption <= total_procs and math.ceil(curroption / num_gpus) <= max_ranks_per_gpu:
        if total_procs % curroption == 0 and curroption % num_gpus == 0:
            options.append(curroption)
        curroption += 1
    return options


def determineGpuTasks(ntmpi: int, gpu_ids: GpuIds, pme_on_gpu: bool = True) -> str:
    """
        Given a known number of ranks and GPU IDs, allocate the GPU IDs to each rank.

        Handles the special case of 1 rank, where two GPU tasks are required. Otherwise each rank gets a task.

        Returns the GPUtasks in Gromacs command line string form, such as '0011' for a 4 rank run over 2 GPUs.
    """
    if ntmpi == 1 and pme_on_gpu:
        return 2 * str(gpu_ids[0])
    assert ntmpi % len(gpu_ids) == 0

    factor: int = int(ntmpi / len(gpu_ids))

    return "".join([factor * str(gpu_id) for gpu_id in gpu_ids])


def _createBaseOptions() -> ParameterSet:
    """
        Populate and return a dictionary containing Gromacs command line parameters that are common to
        all possible mdrun commands. Note that some of these commands can be overwritten.

    """
    return {
        "nsteps": 5000,
        "resetstep": 2500,
        "pin": "on",
        "noconfout": True,
        "nstlist": 80
    }


def addConfigDependentOptions(base_options: ParameterSet, hw_config: HardwareConfig):
    """
        Modify the command line arguments dictionary for options that are immutable once the hardware config
        is known.
    """
    base_options["nt"] = hw_config.num_cpus
    pinstride: int = 1
    if hw_config.num_cpus > 1:
        pinstride = hw_config.cpu_ids[1] - hw_config.cpu_ids[0]
    base_options["pinstride"] = pinstride
    base_options["pinoffset"] = hw_config.cpu_ids[0]
    # GPU NB offload is always better
    if hw_config.num_gpus > 0:
        base_options["nb"] = "gpu"
    else:
        base_options["nb"] = "cpu"


def applyOptionToAll(parameters: List[ParameterSet], key: str, possible_values: List) -> List[ParameterSet]:
    """
        Duplicates a group of parameter sets with each possibility in possible_values. So, given an original
        parameter set of 5 combinations, and a key "other_option" with possible values 1, 2, and 3, a group
        of 15 combinations will be returned, 5 with the original set and "other_option":1, 5 with "other_option": 2,
        and so on.
    """
    new_parameters: List[ParameterSet] = []
    for param_set in parameters:
        for possible_value in possible_values:
            new_parameters.append(deepcopy(param_set))
            new_parameters[-1][key] = possible_value
    return new_parameters


def applyOptionIf(parameters: List[ParameterSet], key: str, value: Any,
                  predicate: Callable[[ParameterSet], bool]) -> List[ParameterSet]:
    """
        Loops over all option groups, and adds the key:val pair to a parameter set if the predicate is satisfied.
        Returns a modified copy of the original group of parameter sets.
    """
    new_parameters: List[ParameterSet] = []
    for param_set in parameters:
        new_parameters.append(deepcopy(param_set))
        if predicate(param_set):
            new_parameters[-1][key] = value
    return new_parameters


def pruneOptionIf(parameters: List[ParameterSet], predicate: Callable[[ParameterSet], bool]) -> List[ParameterSet]:
    """
        Removes a parameterset from the possibilities if it meets the predicate conditions
    """
    return [option for option in parameters if not predicate(option)]


def _pruneUnlikelyCombinations(parameters: List[ParameterSet]) -> List[ParameterSet]:
    """
        Removes combinations where PME != bonded != update - such as:

        * PME GPU with bonded or update CPU
        * PME CPU with bonded or update GPU
    """
    def removalPredicate(params: ParameterSet) -> bool:
        pme = params["pme"]
        # For earlier versions without these options (eg. 2016),
        # set the other options to PME so the inequality isn't triggered.
        update = params.get("update", pme)
        bonded = params.get("bonded", pme)
        return pme != update or pme != bonded
    return pruneOptionIf(parameters, removalPredicate)


def _createVersionedOptions(base_opts: ParameterSet, hw_config: HardwareConfig, gmx_version: str,
                            generate_options: GenerateOptions) -> ParameterSetGroup:
    """
        Given a partial base parameter set, a hardware config, and a target Gromacs version, creates all of the
        parameter combination possibilities.
    """
    options: List[ParameterSet] = [base_opts]

    # Add thread information
    ntmpi_possibilities: List[int] = genNtmpiOptions(hw_config.num_cpus, hw_config.num_gpus)
    options = applyOptionToAll(options, "ntmpi", ntmpi_possibilities)
    # Once ntmpi is set, ntomp is unambiguous.
    for opt in options:
        nt: int = opt["nt"]
        ntmpi: int = opt["ntmpi"]
        # These should be guaranteed to be divisible from genNtmpiOptions
        assert nt % ntmpi == 0
        opt["ntomp"] = int(nt / ntmpi)

    if not hw_config.num_gpus > 0:
        return options

    if gmx_version >= "2018":
        options = applyOptionToAll(options, "pme", ["cpu", "gpu"])

        # Cap max ranks for PME GPU
        def excessRanksPredicate(params: ParameterSet) -> bool:
            return params["pme"] == "gpu" and params["ntmpi"] > generate_options.max_ranks_for_pme_gpu
        options = pruneOptionIf(options, excessRanksPredicate)

        # set npme if more than one rank.
        def nPmePredicate(params: ParameterSet) -> bool:
            return params["pme"] == "gpu" and params["ntmpi"] > 1
        options = applyOptionIf(options, "npme", 1, nPmePredicate)
    if gmx_version >= "2019":
        # Note that this is valid even if PME=CPU, it's just nb=GPU that's mandatory, which is guaranteed here.
        options = applyOptionToAll(options, "bonded", ["cpu", "gpu"])
    if gmx_version >= "2020":
        # Similarly to bonded, update=GPU only needs nb=gpu and any combination of pme, bonded, and update is allowed
        options = applyOptionToAll(options, "update", ["cpu", "gpu"])

        # PME = cpu, update = GPU only works on single rank simulations
        def multiRankPredicate(params: ParameterSet):
            return params["pme"] == "cpu" and params["update"] == "gpu" and params["ntmpi"] > 1
        options = pruneOptionIf(options, multiRankPredicate)
    if not generate_options.generate_exhaustive_options:
        options = _pruneUnlikelyCombinations(options)
    # Add gputasks
    for opt in options:
        if opt.get("nb") == "gpu":
            using_pme_on_gpu: bool = opt.get("pme", "cpu") == "gpu"
            opt["gputasks"] = determineGpuTasks(opt["ntmpi"], hw_config.gpu_ids, using_pme_on_gpu)
    return options


def _versionIsValid(version: str):
    return version in _SUPPORTED_GMX_VERSIONS


def createRunOptionsForSingleConfig(hw_config: HardwareConfig, gmx_version: str,
                                    generate_options: GenerateOptions) -> ParameterSetGroup:
    """
        Generate the set of possible run options for a specific hardware config.

        Note that this must be deterministic in order for a given number of CPUs and GPUs
        (though the ordering can be arbitrary).

    """
    base_options: ParameterSet = _createBaseOptions()
    addConfigDependentOptions(base_options, hw_config)
    return _createVersionedOptions(base_options, hw_config, gmx_version, generate_options)


def createRunOptionsForConfigGroup(configs: HardwareConfigBreakdown, gmx_version: str,
                                   generate_options: GenerateOptions) -> List[ParameterSetGroup]:
    """
        Generate all the parameter combinations for a given subconfiguration of the hardware.

        Returns a list with structure:
        [concurrent grouping 1, concurrent_grouping 2...],
        where each concurrent grouping is a list of Gromacs parameter sets to be executed concurrently. In other words,
        each top level element of the returned list is the set of one or more concurrent Gromacs commands to fully
        exercise the hardware.
    """
    if len(configs) == 0:
        return []

    if not _versionIsValid(gmx_version):
        raise ValueError("Invalid Gromacs version: {}. Supported options are {}".format(gmx_version,
                                                                                        _SUPPORTED_GMX_VERSIONS))

    # This gets us all the combinations we want, but with the wrong structure. The top level is for each partial
    # hardware config, and the second level is over the options within each subconfig.
    breakdowns_per_config: List[ParameterSetGroup] = [createRunOptionsForSingleConfig(config, gmx_version,
                                                                                      generate_options)
                                                      for config in configs]
    # Now we reorder, inverting the organization such that
    #   [[subconfig1_option1, subconfig1_option2], [subconfig2_option1, subconfig2_option2]]
    # becomes
    #   [[subconfig1_option1, subconfig2_option1], [subconfig1_option2, subconfig2_option2]].
    # Since the single-config parameter generator is deterministic, combining subconfig1_option1 with subconfig2_option1
    # and so on will match the proper combination of parameters for each option set.
    params: List[ParameterSetGroup] = []
    num_options_per_partial_config: int = len(breakdowns_per_config[0])
    for i in range(num_options_per_partial_config):
        params.append([config_grouping[i] for config_grouping in breakdowns_per_config])
    return params
