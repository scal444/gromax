[![Build Status](https://travis-ci.org/scal444/gromax.svg?branch=master)](https://travis-ci.org/scal444/gromax)
[![codecov](https://codecov.io/gh/scal444/gromax/branch/master/graph/badge.svg)](https://codecov.io/gh/scal444/gromax)

# Gromax
Gromax is a tool to help optimize GROMACS performance on any hardware, particuarly useful for working with GPUs.


---------------------------

Today's molecular simulation engines are complicated. To get the most performance out of Gromacs and other packages,
there are a large number of simulation parameters that need to be considered and tweaked. With the incorporation of
GPUs this problem becomes even more complicated, and differing flags and options between yearly releases of Gromacs adds
yet another layer of complexity. Gromax is here to help.

## Installation
### Via pip
To install the most recent release:
```
pip install git+https://github.com/scal444/gromax@v0.1.0
```

To install the current master version:

```
pip install git+https://github.com/scal444/gromax
```

### Requirements
- python 3.6 or greater

## Capabilities
- Given a Gromacs TPR file and a description of the hardware (CPU count and GPU IDs), generate a series of Gromacs run
  commands to explore which parameters provide the best performance for the hardware.
- Supports Gromacs major versions 2016, 2018, 2019, and 2020.
- Break down the available hardware into subcomponents to assess maximum throughput on a single node.
- Generates a simple bash script to execute
- Analyzes results and reports best paramater combinations.

See the [future work doc](docs/future_work.md) for planned features.

## Usage
You can find some details via the help text(```gromax --help```). See the various possible usages 
in [the examples doc](docs/examples.md)!

## Notes
- Gromax is designed for single node optimization and works best with non-MPI gromacs (think gmx binary rather than 
  gmx_mpi). It may work with an MPI-compiled Gromacs, but no guarantees. Non-MPI Gromacs does have a limit of 64
  threads, which should be sufficient for most purposes.
- Some simulation features (free energy, thermostats) affect which runtime optimizations can be used. Gromax currently
  does not take these into account, so a few simulation combinations may fail with valid errors. Send me an email
  or open up a bug report if you're unsure if this is the case with your failures.

## Contributing
- Feel free to file an issue bug/feature request, or create a PR. There is a 
  [known issues doc](docs/known_issues.md) for problems that are known but can't yet be addressed. 

## Other awesome resources
- Want to see how well your system scales to various clusters? Check out
 [MDBenchmark](https://github.com/bio-phys/mdbenchmark)!
 
