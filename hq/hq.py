#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""hq - Beautiful HTML querying, filtering, slicing and dicing!

Usage:
  hq.py [-x] [-n] <expression>
  hq.py --version
  hq.py (-h | --help)

Options:
  -n            Print HTML output non-prettily (no extra whitespace).
  -x            Interpret the expression as an XPath.
  -v            Be verbose.
  --version     Display the installed HQ version.

HTML is read from stdin.

"""

from sys import stdin

from bs4 import BeautifulSoup
from docopt import docopt

from .config import settings
from .css.query_css import query_css
from .xpath.query_xpath import query_xpath


__version__ = '0.0.1'


def main():
    CSS, XPATH = range(2)
    args = docopt(__doc__, version='HQ {0}'.format(__version__))
    print(args)
    language = XPATH if '-x' in args else CSS
    setattr(settings, 'VERBOSE', bool('-v' in args))

    source = stdin.read()
    soup = BeautifulSoup(source, 'html.parser')

    expression = args['<expression>']
    if len(expression) > 0:
        if (language == CSS):
            results = query_css(soup, expression)
        else:
            results = query_xpath(soup, expression)
    else:
        results = [soup]

    for tag in results:
        print(str(tag) if args['-n'] else tag.prettify().rstrip(' \t\n'))


if __name__ == '__main__':
    main()
