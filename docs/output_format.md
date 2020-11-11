This document describes the directory structure that scripts built with
*gromax generate* try to create at runtime, and the format that *gromax analyze*
expects. 

Given a top level directory foo, and run script foo/benchmark.sh, the first
level of subdirectories is the "group" level. A group is a set of (one or more) 
simulations to be run as a concurrent benchmark, where the hardware is split among 
the elements of the group.

The next subdirectory level is for trials. Each group has one or more trials, for which
results will be averaged.

Inside each trial is the result of a concurrent set of simulations. Each simulation in a
group is assigned a "component" ID. Putting it all together, a directory setup
might look like this:

```
# In this example, group_1 is a set of 2 concurrent simulations, group_2 is
# a single simulation (presumably taking up all of the hardware), with 3 trials of each.
# Non-log files are omitted for clarity but can exist in the lowest subdirectory
# next to the logs.
foo/
foo/benchmark.sh
foo/group_1/
foo/group_1/trial_1/
foo/group_1/trial_1/component_1.log
foo/group_1/trial_1/component_2.log
foo/group_1/trial_2/
foo/group_1/trial_2/component_1.log
foo/group_1/trial_2/component_2.log
foo/group_1/trial_3/
foo/group_1/trial_3/component_1.log
foo/group_1/trial_3/component_2.log
foo/group_2/
foo/group_2/trial_1/
foo/group_2/trial_1/component_1.log
foo/group_2/trial_2/
foo/group_2/trial_2/component_1.log
foo/group_2/trial_3/
foo/group_2/trial_3/component_1.log
```

