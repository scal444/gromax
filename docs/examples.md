## gromax generate examples
These examples generate bash scripts that can be used to benchmark Gromacs on your hardware.
#### With default options
```shell script
# cpu_ids, gpu_ids, run_file and gmx_version are mandatory. Options such as the number of trials and tpr to
# benchmark are easily configurable at the top of the output script.
# TODO Update when runfile is no longer mandatory.
# For Gromacs 2019: 
gromax generate --cpu_ids=0,1,2,3 --gpus_ids=0,1 --gmx_version=2019 --run_file=benchmark_gmx2019.sh
# For Gromacs 2018:
gromax generate --cpu_ids=0,1,2,3 --gpus_ids=0,1 --gmx_version=2019 --run_file=benchmark_gmx2018.sh
```

#### Different ways to specify hardware components.
```shell script
# It's easy to specify ranges of CPUs or GPUs. This example is for a 40 CPU system with 5 GPUs, with logical
# IDs starting from 0.
gromax generate --gmx_version=2020 --cpu_ids=0-39 --gpu_ids=0-4
# Colon-range syntax works as well.
gromax generate --gmx_version=2020 --cpu_ids=0:39 --gpu_ids=0:4

# CPUs can be strided, if e.g. one has a hyperthreaded system and wants 1 thread per physical core.
# This will benchmark on cores 0,2,4,and 6.
gromax generate --gmx_version=2020 --cpu_ids=0:2:7 --gpu_ids=0
```

#### Some configuration options for the run script.
**NOTE: Each of these options can also easily be set in the first few lines of the benchmark script.** 
```shell script
# Specify a gmx binary that isn't in your shell's PATH.
gromax generate --gmx_version=2020 --cpu_ids=0-39 --gpu_ids=0-4 --gmx_executable="/path/to/gmx"
# Use gmx_mpi rather than gmx - no guarantees that it'll work nicely with MPI.
gromax generate --gmx_version=2020 --cpu_ids=0-39 --gpu_ids=0-4 --gmx_executable="/path/to/gmx"
# Specify the number of trials to run per simulation group (defaults to 3).
gromax generate --gmx_version=2020 --cpu_ids=0-39 --gpu_ids=0-4 --trials_per_group=15
# Specify the tpr file that will be benchmarked (no default, so if not set you'll have to set in the benchmark script).
gromax generate --gmx_version=2020 --cpu_ids=0-39 --gpu_ids=0-4 --tpr=benchmark.tpr
```

## gromax analyze examples
#### Execute from current directory.
```shell script
# Equivalent to --directory=`pwd`, will only succeed if benchmark groups are directly under this folder.
gromax analyze
```

### from specific folder
```shell script
# Group results should be in /path/to/results.
gromax analyze --directory=/path/to/results
```