[![Build Status](https://travis-ci.org/scal444/gromax.svg?branch=master)](https://travis-ci.org/scal444/gromax)
[![codecov](https://codecov.io/gh/scal444/gromax/branch/master/graph/badge.svg)](https://codecov.io/gh/scal444/gromax)

# Gromax
Gromax is a tool to help optimize GROMACS performance on any hardware, particuarly useful for working with GPUs.


---------------------------

Today's molecular simulation engines are complicated. To get the most performance out of Gromacs and other packages,
there are a large number of simulation parameters that need to be considered and tweaked. With the incorporation of
GPUs this problem becomes even more complicated. Gromax is here to help.

## Installation
### Via pip
To install the current master version:

```
pip install git+https://github.com/scal444/gromax
```

TODO: Add branches as they come online

### Requirements
- python 3.6 or greater

## Current Capabilities
- Given a Gromacs TPR file and a description of the hardware (CPU count and GPU IDs), generate a series of Gromacs run
  commands to explore which parameters provide the best performance for the hardware.
- Supports Gromacs major versions 2016, 2018, 2019, and 2020 (not including experimental P2P GPU implementations yet)
- Break down the available hardware into subcomponents to assess maximum throughput on a single node.
- Generate a simple bash script to execute
- See the examples section in the documentation

## Future additions
- A run executor to automate the benchmarking process.

## Long-term directions
- Support for other simulation suites


## Other awesome resources
- Want to see how well your system scales to various clusters? Check out
 [MDBenchmark](https://github.com/bio-phys/mdbenchmark)!
 
