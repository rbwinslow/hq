#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""hq - Beautiful HTML querying, filtering, slicing and dicing!

Usage:
  hq.py [-v] [-x] [-n] <expression>
  hq.py --version
  hq.py (-h | --help)

Options:
  -n            Print HTML output non-prettily (no extra whitespace).
  -x            Interpret the expression as an XPath.
  -v            Be verbose.
  --version     Display the installed HQ version.

HTML is read from stdin.

"""

from __future__ import print_function

from sys import stderr, stdin

from docopt import docopt

from .config import settings
from .css.query_css import query_css
from .output import result_object_to_text
from .soup_util import make_soup
from .verbosity import verbose_print, set_verbosity
from .xpath.query_xpath import query_xpath, XpathQueryError

__version__ = '0.0.1'


def main():
    CSS, XPATH = range(2)
    args = docopt(__doc__, version='HQ {0}'.format(__version__))
    print(args)
    language = XPATH if args['-x'] else CSS
    set_verbosity(bool(args['-v']))

    try:
        source = stdin.read()
        verbose_print('Read {0} characters of input'.format(len(source)))
        soup = make_soup(source)

        expression = args['<expression>']
        if len(expression) > 0:
            if (language == CSS):
                result = query_css(soup, expression)
            else:
                result = query_xpath(soup, expression)
        else:
            result = [soup]

        print(result_object_to_text(result, pretty=(not args['-n'])))
    except XpathQueryError as error:
        print('\nERROR! {0}\n'.format(str(error)), file=stderr)


if __name__ == '__main__':
    main()
