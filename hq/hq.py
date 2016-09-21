#!/usr/bin/env python

"""hq - Beautiful HTML querying, filtering, slicing and dicing!

Usage:
  hq.py [-v] [-c] [-n] <expression>
  hq.py --version
  hq.py (-h | --help)

Options:
  -c            Interpret the expression as a CSS selector (otherwise HQuery, the default).
  -n            Print HTML output non-prettily (no extra whitespace).
  -v            Be verbose.
  --version     Display the installed HQ version.

HTML is read from stdin.

"""

from __future__ import print_function

from sys import stderr, stdin

from docopt import docopt

from .output import result_object_to_text
from .soup_util import make_soup
from .verbosity import verbose_print, set_verbosity
from .hquery.hquery_processor import HqueryEvaluationError, HqueryProcessor

__version__ = '0.0.1'


def main():
    CSS, HQUERY = range(2)
    args = docopt(__doc__, version='HQ {0}'.format(__version__))
    language = HQUERY if args['-x'] else CSS
    set_verbosity(bool(args['-v']))

    try:
        source = stdin.read()
        verbose_print('Read {0} characters of input'.format(len(source)))
        soup = make_soup(source)

        expression = args['<expression>']
        if len(expression) > 0:
            if language == CSS:
                result = soup.select(expression)
            else:
                result = HqueryProcessor(expression).query(soup)
        else:
            result = [soup]

        print(result_object_to_text(result, pretty=(not args['-n'])))
    except HqueryEvaluationError as error:
        print('\nERROR! {0}\n'.format(str(error)), file=stderr)


if __name__ == '__main__':
    main()
