import json
from gromax.utils import fatal_error
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
    pass

    def __init__(self, file=None, cpu_ids=None, gpu_ids=None):
        if file:
            if cpu_ids or gpu_ids:
                fatal_error("Cannot provide configuration file AND manual specification of properties")
            self.loadFromConfigFile(file)
            return
        if cpu_ids:
            self.cpu_ids = cpu_ids
        else:
            self.cpu_ids = []
        if gpu_ids:
            self.gpu_ids = gpu_ids
        else:
            self.gpu_ids = []

    # FIXME Figure out json load vs loads and what we want
    def loadFromConfigFile(self, file):
        # TODO handle failure to load json
        # TODO add note if ids and num_cpus clash, but work from info from ids
        try:
            with open(file, 'rt') as fin:
                try:
                    raw_config = json.load(fin)
                except Exception:
                    # TODO more specific error, catch correct exception
                    fatal_error("Failed to parse json file")

                # can load hardware config from file, or entire run specification. If the latter, search for hardware
                # config and discard the rest
                # TODO if we load from config this leads to multiple openings of the file
                if "hardware_config" in raw_config.keys():
                    raw_config = raw_config["hardware_config"]

                self.cpu_ids = raw_config.get("cpu_ids", [])
                if not self.cpu_ids:
                    try:
                        # without a specific cpu_ids input, we start them from 0
                        # Note that this modifies the state of the configuration, in that savetofile(loadfromfile())
                        # will not yield the original file
                        self.cpu_ids = list(range(raw_config["num_processors"]))
                    except KeyError:
                        fatal_error("Configuration file did not provide either a list of processor ids (with key "
                                    "'cpu_ids'), or a number of processors (with key 'num_processors')")

                assert len(self.cpu_ids) == self.num_cpus, "num cpus: {}, len(cpu_ids): {}".format(
                    self.num_cpus, len(self.cpu_ids))

                self.gpu_ids = raw_config.get("gpu_ids", [])
        except Exception:
            # TODO be specific
            fatal_error("Failed to open config file {}".format(file))

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
        if not isinstance(gpu_ids, list):
            fatal_error("gpu_ids paramater must be a list")
        for item in gpu_ids:
            if not isinstance(item, int):
                fatal_error("All gpu ids must be integers - {} is not an integer".format(item))
            if item < 0:
                fatal_error("Cannot have a negative GPU ID")
        self._gpu_ids = gpu_ids

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
        fatal_error("Expected a list for parameter 'cpu_ids'")

    if not all([isinstance(i, int) and i >= 0 for i in cpu_ids]):
        fatal_error("Not all values in 'cpu_ids' are ints")

    # case of empty list
    if not cpu_ids:
        return

    if len(cpu_ids) > 1:
        diff = cpu_ids[1] - cpu_ids[0]

        for i, val in enumerate(cpu_ids[:-1]):
            if (cpu_ids[i+1] - val) != diff:
                fatal_error("Inconsistent stride between cpu ids")
    return True
