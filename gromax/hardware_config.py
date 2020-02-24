import gromax.utils as utils
import math
from copy import deepcopy
from typing import List

# Convenience Definitions
GpuIDs = List[int]


class HardwareConfig(object):
    """
        Representation of the available hardware. This may represent all or part of a system.

        Attributes:
            cpu_ids: List of integers of CPU IDs
            gpu_ids: List of integers of GPU IDs

        Properties:
            num_cpus: number of CPUs
            num_gpus: number of GPUs
    """

    def __init__(self, cpu_ids: List[int] = None, gpu_ids: List[int] = None):
        if cpu_ids:
            self.cpu_ids: List[int] = cpu_ids
        else:
            self.cpu_ids: List[int] = []
        if gpu_ids:
            self.gpu_ids: List[int] = gpu_ids
        else:
            self.gpu_ids: List[int] = []

    @property
    def num_cpus(self) -> int:
        return len(self._cpu_ids)

    @property
    def num_gpus(self) -> int:
        return len(self._gpu_ids)

    @property
    def cpu_ids(self) -> List[int]:
        return deepcopy(self._cpu_ids)

    @cpu_ids.setter
    def cpu_ids(self, cpu_ids):
        checkProcessorIDContent(cpu_ids)
        self._cpu_ids = cpu_ids

    @property
    def gpu_ids(self) -> List[int]:
        return deepcopy(self._gpu_ids)

    @gpu_ids.setter
    def gpu_ids(self, gpu_ids: List[int]):
        try:
            for item in gpu_ids:
                if not isinstance(item, int):
                    utils.fatal_error("All gpu ids must be integers: {} is not an int".format(item))
                if item < 0:
                    utils.fatal_error("Cannot have a negative GPU ID")
            self._gpu_ids = gpu_ids
        except TypeError:
            utils.fatal_error("gpu_ids paramater must be iterable")

    def __str__(self) -> str:
        return "\nHardware config:\n\tcpu IDs : {}\n\tgpu IDs : {}".format(self._cpu_ids, self._gpu_ids)

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, other) -> bool:
        if not isinstance(other, HardwareConfig):
            return False
        return self.cpu_ids == other.cpu_ids and self.gpu_ids == other.gpu_ids

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)


def distributeGpuIdsToTasks(gpu_ids: GpuIDs, ntasks: int) -> List[GpuIDs]:
    """
        Creates a list of lists of [[task 0 gpu ids],[task 1 gpu ids]]

        There can be multiple gpu_ids assigned to a task, or the same GPU can be assigned
        to multiple tasks, depending on the workload.
    """
    if not isinstance(gpu_ids, list):
        raise TypeError("Gpu IDs must be a list - is {}".format(gpu_ids))

    n_gpu_ids: int = len(gpu_ids)
    if n_gpu_ids % ntasks != 0 and ntasks % n_gpu_ids != 0:
        raise ValueError("The number of tasks ({}) needs to be divisible by the number of GPU ids ".format(ntasks) +
                         "({}), or vice versa".format(n_gpu_ids))

    result: List[GpuIDs] = []
    current_index: int = 0
    for i, task in enumerate(range(ntasks)):
        task_ids: GpuIDs = []
        if n_gpu_ids > ntasks:
            ratio: int = int(n_gpu_ids / ntasks)
            for r in range(ratio):
                task_ids.append(gpu_ids[current_index])
                current_index += 1
        else:
            ratio: int = int(ntasks / n_gpu_ids)
            task_ids.append(gpu_ids[math.floor(i / ratio)])

        result.append(task_ids)
    return result


def generateConfigSplitOptions(hw_config: HardwareConfig) -> List[List[HardwareConfig]]:
    """
        Hardware configs can be split for simultaneous simulations with the following constraints:

        - Each split config must have the same number of cores
        - All cores must be used (could relax this in the future)
        - Num_sims / num_GPus must be an integer. Note that in the case of 1 GPU, all combinations satisfy this
          constraint.

        Returns a list of lists of [ [configsplit1] [configsplit2] ... ]
        where configsplit1 is a list of one or more hardware configs. The hardware parts in the components of
        configsplit1 should add up to the entire config.

    """
    num_total_cpus: int = hw_config.num_cpus
    num_total_gpus: int = hw_config.num_gpus

    # The whole config is always an option
    config_possibilities: List[List[HardwareConfig]] = [[hw_config]]

    # No splitting if no GPUs - is never good performance for Gromacs
    if num_total_gpus == 0:
        return config_possibilities

    # Search division options, between 1 cpu per sim and half of the cpus per sim. Note that the all CPUs
    # per sim option is already accounted for above.
    cpu_per_sim_options: List[int] = [i for i in range(1, int(num_total_cpus / 2) + 1)
                                      if num_total_cpus % i == 0 and int(num_total_cpus / i) % num_total_gpus == 0]
    for cpus_per_sim in cpu_per_sim_options:
        sims_in_set: int = int(num_total_cpus / cpus_per_sim)

        config_set: List[HardwareConfig] = []
        gpu_id_assignments: List[List[int]] = distributeGpuIdsToTasks(hw_config.gpu_ids, sims_in_set)
        for i, gpu_assignment in enumerate(gpu_id_assignments):
            config: HardwareConfig = HardwareConfig()
            config.cpu_ids = hw_config.cpu_ids[i * cpus_per_sim: (i + 1) * cpus_per_sim]
            config.gpu_ids = gpu_assignment
            config_set.append(config)
        config_possibilities.append(config_set)
    return config_possibilities


def checkProcessorIDContent(cpu_ids: List[int]):
    """
        Given an assigned value for cpu_ids, assure that
        1. It is a list
        2. The list contains all integers
        3. The stride between integers is consistent.

        Exits the program if a condition is not met.
    """
    if not isinstance(cpu_ids, list):
        utils.fatal_error("Expected a list for parameter 'cpu_ids'")

    if not all([isinstance(i, int) and i >= 0 for i in cpu_ids]):
        utils.fatal_error("Not all values in 'cpu_ids' are ints")

    # case of empty list
    if not cpu_ids:
        return

    if len(cpu_ids) > 1:
        diff: int = cpu_ids[1] - cpu_ids[0]

        for i, val in enumerate(cpu_ids[:-1]):
            if (cpu_ids[i+1] - val) != diff:
                utils.fatal_error("Inconsistent stride between cpu ids")
