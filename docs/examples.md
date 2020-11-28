## gromax generate examples
These examples generate bash scripts that can be used to benchmark Gromacs on your hardware.
#### With default options
```shell script
# cpu_ids, gpu_ids, run_file and gmx_version are mandatory. Options such as the number of trials and tpr to
# benchmark are easily configurable at the top of the output script.
# TODO Update when runfile is no longer mandatory.
# For Gromacs 2019: 
gromax generate --num_cpus=4 --num_gpus=2 --gmx_version=2019 --run_file=benchmark_gmx2019.sh
# For Gromacs 2018:
gromax generate --num_cpus=4 --num_gpus=2  --gmx_version=2018 --run_file=benchmark_gmx2018.sh
```

#### Different ways to specify hardware components.
The simplest use is to specify the number of CPUs and GPUs to be tested (see above example). This works great if the 
CPUs and GPUs you want to test on are indexed from 0 and don't skip. There are several alternative ways to customize
hardware usage: 
```shell script
# It's easy to specify ranges of CPUs or GPUs. This example is for a 40 CPU system with 5 GPUs, with logical
# IDs starting from 0.
gromax generate --gmx_version=2020 --cpu_ids=0-39 --gpu_ids=0-4
# Colon-range syntax works as well.
gromax generate --gmx_version=2020 --cpu_ids=0:39 --gpu_ids=0:4
# Both of the above are equivalent to --num_cpus=40 --num_gpus=5.

# Comma separated values work as well, as long as they are evenly strided.
gromax generate --gmx_version=2018 --cpu_ids=0,1,2,3 --gpu_ids=0

# Use only GPUs 1 and 2 (e.g. if GPU 0 is dedicated to graphics)
gromax generate --gmx_version=2020, --num_cpus=8 --gpu_ids=1,2

# CPUs can be strided, if e.g. one has a hyperthreaded system and wants 1 thread per physical core.
# This will benchmark on cores 0,2,4,and 6.
# NOTE: This is experimental and not yet well tested.
gromax generate --gmx_version=2020 --cpu_ids=0:2:7 --gpu_ids=0
```
#### Customizing how gromax will explore your hardware.
```shell script
# If your workflows absolutely require a single long simulation, and you can't parallelize at all, you can have gromax
# ignore all the various possible hardware breakdowns for multiple concurrent simulations. Using this parameter will
# have gromax generate ONLY benchmarks for single simulations that use all of the given hardware.
gromax generate --gmx_version=2020 --cpu_ids=0:7 --gpu_ids=0 --single_sim_only
```

#### Some configuration options for the run script.
*NOTE: Each of these options can also easily be set in the first few lines of the benchmark script.* 
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