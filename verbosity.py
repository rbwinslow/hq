
import sys

import config


indent_level = 0


def set_verbosity(verbose):
    setattr(config, 'VERBOSE', verbose)


def push_indent():
    global indent_level
    indent_level += 2

def pop_indent():
    global indent_level
    indent_level -= 2


def verbose_print(text, indent_after=False, outdent_before=False):
    if outdent_before:
        pop_indent()
    if getattr(config, 'VERBOSE'):
        print('{0}{1}'.format(' ' * indent_level, text), file=sys.stderr)
    if indent_after:
        push_indent()
