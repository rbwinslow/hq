import os
import sys

sys.path.insert(0, os.path.abspath('..'))

from hq.verbosity import set_verbosity


def pytest_addoption(parser):
    parser.addoption("--gabby",
                     action="store_true",
                     help="Print verbose (debug) information to stderr")


def pytest_configure(config):
    set_verbosity(bool(config.getvalue('--gabby')))
    pass
