import gromax.utils as utils
from copy import deepcopy


class HardwareConfig(object):
    """
        Attributes
            _cpu_ids  - integer IDs, evenly strided. Most will start at 0 and have stride 1
            _gpu_ids  - integer IDs. These have no restrictions besides being real numbers

            The CPU attributes need either one or the other. If num_cpus is assigned without cpu_ids, the
            the cpu_ids will be set starting from zero

            GPU IDs are not required, but if present require either num_cpus or cpu_ids

            # TODO update this all - config file should be able to specify num_cpus, cpu_offset, cpu_stride,
            # OR have cpu_ids, but the data structure should just have cpu_ids
    """

    def __init__(self, cpu_ids=None, gpu_ids=None):
        if cpu_ids:
            self.cpu_ids = cpu_ids
        else:
            self.cpu_ids = []
        if gpu_ids:
            self.gpu_ids = gpu_ids
        else:
            self.gpu_ids = []

    @property
    def num_cpus(self):
        return len(self._cpu_ids)

    @property
    def num_gpus(self):
        return len(self._gpu_ids)

    @property
    def cpu_ids(self):
        return deepcopy(self._cpu_ids)

    @cpu_ids.setter
    def cpu_ids(self, cpu_ids):
        checkProcessorIDContent(cpu_ids)
        self._cpu_ids = cpu_ids

    @property
    def gpu_ids(self):
        return deepcopy(self._gpu_ids)

    @gpu_ids.setter
    def gpu_ids(self, gpu_ids):
        try:
            for item in gpu_ids:
                if not isinstance(item, int):
                    utils.fatal_error("All gpu ids must be integers: {} is not an int".format(item))
                if item < 0:
                    utils.fatal_error("Cannot have a negative GPU ID")
            self._gpu_ids = gpu_ids
        except TypeError:
            utils.fatal_error("gpu_ids paramater must be iterable")

    def __str__(self):
        return "\nHardware config:\n\tcpu IDs : {}\n\tgpu IDs : {}".format(self._cpu_ids, self._gpu_ids)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if not isinstance(other, HardwareConfig):
            return False
        return self.cpu_ids == other.cpu_ids and self.gpu_ids == other.gpu_ids

    def __ne__(self, other):
        return not self.__eq__(other)


def checkProcessorIDContent(cpu_ids):
    """
        Given an assigned value for cpu_ids, assure that
        1. It is a list
        2. The list contains all integers
        3. The stride between integers is consistent
    """
    if not isinstance(cpu_ids, list):
        utils.fatal_error("Expected a list for parameter 'cpu_ids'")

    if not all([isinstance(i, int) and i >= 0 for i in cpu_ids]):
        utils.fatal_error("Not all values in 'cpu_ids' are ints")

    # case of empty list
    if not cpu_ids:
        return

    if len(cpu_ids) > 1:
        diff = cpu_ids[1] - cpu_ids[0]

        for i, val in enumerate(cpu_ids[:-1]):
            if (cpu_ids[i+1] - val) != diff:
                utils.fatal_error("Inconsistent stride between cpu ids")
    return True
