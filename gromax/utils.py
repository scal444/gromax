import os
import sys


def fatal_error(message):
    # TODO log when we have logging support
    sys.stderr.write(message)
    sys.exit(1)


def openOrDie(file, mode):
    """
        To be used in place of open in with open(file, mode) as fin/fout:

        Performs specific additional checks on failure to open in correct mode
    """
    try:
        fin = open(file, mode)
        return fin
    except FileExistsError:
        fatal_error("File {} already exists, will not overwrite".format(os.path.abspath(file)))
    except FileNotFoundError:
        fatal_error("File not found - could not find {}".format(os.path.abspath(file)))
    except IsADirectoryError:
        fatal_error("Path specified is a directory, not a file. Path in question: {}".format(os.path.abspath(file)))
    except PermissionError:
        if "w" in mode:
            attempt = "write"
        else:
            attempt = "read"
        fatal_error("You lack {} permissions for file {}".format(attempt, os.path.abspath(file)))
