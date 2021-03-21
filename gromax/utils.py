import logging
import os
import sys


def fatalError(message):
    logging.getLogger("gromax").error(message)
    raise SystemExit(1)


def openOrDie(file, mode):
    """
        To be used in place of open in with open(file, mode) as fin/fout:

        Performs specific additional checks on failure to open in correct mode
    """
    try:
        fin = open(file, mode)
        return fin
    except FileExistsError:
        fatalError("File {} already exists, will not overwrite".format(os.path.abspath(file)))
    except FileNotFoundError:
        fatalError("File not found - could not find {}".format(os.path.abspath(file)))
    except IsADirectoryError:
        fatalError("Path specified is a directory, not a file. Path in question: {}".format(os.path.abspath(file)))
    except PermissionError:
        if "w" in mode:
            attempt = "write"
        else:
            attempt = "read"
        fatalError("You lack {} permissions for file {}".format(attempt, os.path.abspath(file)))
