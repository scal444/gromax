
from gromax.hardware_config import HardwareConfig
from typing import List, Dict

# Convenience definitions
# A grouping of GPU ids.
GpuIds = List[int]
# Dictionary representing the options for a single gromacs command line run.
ParameterSet = Dict
# List of dictionaries representing a set of Gromacs commands to be run concurrently.
ParameterSetGroup = List[ParameterSet]
# A breakdown of hardware configs (presumably adding to the full config) for gromacs runs to run on concurrently.
HardwareConfigBreakdown = List[HardwareConfig]


def genNtmpiOptions(total_procs: int, num_gpus: int = 1) -> List[int]:
    if total_procs <= 0:
        raise ValueError("Numbers need to be positive, total_procs = {}".format(total_procs))
    curroption: int = num_gpus
    options: List[int] = []
    while curroption <= total_procs:
        if total_procs % curroption == 0 and curroption % num_gpus == 0:
            options.append(curroption)
        curroption += 1
    return options


def determineGpuTasks(ntmpi: int, gpu_ids: GpuIds, pme_on_gpu: bool = True) -> str:
    if ntmpi == 1 and pme_on_gpu:
        return 2 * str(gpu_ids[0])
    assert ntmpi % len(gpu_ids) == 0

    factor: int = int(ntmpi / len(gpu_ids))

    return "".join([factor * str(gpu_id) for gpu_id in gpu_ids])
