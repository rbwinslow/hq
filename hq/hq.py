#!/usr/bin/env python

"""hq - Beautiful HTML querying, filtering, slicing and dicing!

Usage:
  hq.py [options] <expression>
  hq.py --version
  hq.py (-h | --help)

Options:
  --preserve    Preserve extra whitespace in string values derived from HTML contents. The default behavior is to
                automatically apply normalize-string to all string values derived from HTML elements and attributes.
  -u, --ugly    Do not pretty-print HTML markup on output.
  -v            Print verbose query parsing and evaluation information to stderr.
  --version     Display the installed HQ version.

HTML is read from stdin.

"""

from __future__ import print_function

from docopt import docopt

from .hquery.hquery_processor import HqueryEvaluationError, HqueryProcessor, HquerySyntaxError
from .output import result_object_to_text
from .soup_util import make_soup
from .verbosity import verbose_print, set_verbosity

__version__ = '0.0.1'


def main():
    from sys import stderr, stdin   # So py.tests have a chance to hook stdout & stderr

    args = docopt(__doc__, version='HQ {0}'.format(__version__))
    set_verbosity(bool(args['-v']))

    try:
        source = stdin.read()
        verbose_print('Read {0} characters of input'.format(len(source)))
        soup = make_soup(source)

        expression = args['<expression>']
        if len(expression) > 0:
            result = HqueryProcessor(expression, bool(args['--preserve'])).query(soup)
        else:
            result = [soup]

        print(result_object_to_text(result, pretty=(not (args['-u'] or args['--ugly']))))

    except HquerySyntaxError as error:
        print('\nSYNTAX ERROR: {0}\n'.format(str(error)), file=stderr)
    except HqueryEvaluationError as error:
        print('\nQUERY ERROR: {0}\n'.format(str(error)), file=stderr)


if __name__ == '__main__':
    main()
