import inspect
import os
import string
import random


class StdChecker(object):
    """
        class that stdout or stderr is redirected to for testing purposes. Modified from
        http://pragmaticpython.com/2017/03/23/unittesting-print-statements/
    """

    def __init__(self):
        self.data = []

    def write(self, txt):
        self.data.append(txt)

    def clear(self):
        self.data = []

    def __str__(self):
        return "".join(self.data)

    def flush(self):
        pass


def get_relative_path(*paths):
    """
        Amends a path to be relative to the directory of the calling script.
        Taken from Rob Buckley
        https: // stackoverflow.com/questions/28021472/get-relative-path-of-caller-in-python
        who took it from
        https: // stackoverflow.com/questions/1095543/get-name-of-calling-functions-module-in-python
    """
    frm = inspect.stack()[1]
    mod = inspect.getmodule(frm[0])
    return os.path.join(os.path.dirname(mod.__file__), *paths)


def randomString(length):
    all_letters_numbers = string.ascii_letters + string.digits
    return ''.join(random.choice(all_letters_numbers) for _ in range(length))


def mockResultString(result_val: float = None):
    pre_string = randomString(random.randint(10, 20))
    post_string = randomString(random.randint(10, 20))
    perf = ""
    if result_val is not None:
        perf = "Performance: {:f}".format(result_val)
    return pre_string + perf + post_string
