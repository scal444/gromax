This doc includes details on some desired features.

### A test run executor
Right now Gromax can create a bash script for benchmarking and analyze results, but can't directly execute the
benchmarks. An execution framework ("gromax execute") would remove the need for a separate bash script, and would
allow cool features like randomization of execution order to reduce hardware bias.

### Automatic hardware detection
If gromax is installed on a computer that will be benchmarked, it would be cool to have Gromax autodetect the
hardware rather than have manual input.

### Support for CPU core striding. 
Gromacs can stride CPU cores - such as skipping every second logical core, which can have effects in some hyperthreaded
CPU layouts. Gromax has experimental support for this but hasn't been validated properly. 

### Expansion to other simulation suites.
This is a stretch goal.