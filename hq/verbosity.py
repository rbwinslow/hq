from __future__ import print_function

import sys

from .config import settings


indent_level = 0


def set_verbosity(verbose):
    setattr(settings, 'VERBOSE', verbose)


def push_indent():
    global indent_level
    indent_level += 2

def pop_indent():
    global indent_level
    indent_level -= 2


def verbose_print(text, indent_after=False, outdent_before=False):
    if settings.VERBOSE:
        if outdent_before:
            pop_indent()
        if getattr(settings, 'VERBOSE'):
            print(u'{0}{1}'.format(' ' * indent_level, text), file=sys.stderr)
        if indent_after:
            push_indent()
