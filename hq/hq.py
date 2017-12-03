#!/usr/bin/env python

"""hq - Powerful HTML querying, filtering, slicing and dicing!

Usage:
  hq.py [options] <expression>
  hq.py [options] -p <file>
  hq.py --version
  hq.py (-h | --help)

Options:
  -f, --file <file>     Read HTML input from a file rather than stdin.
  --preserve            Preserve extra whitespace in string values derived
                        from HTML contents. The default behavior is to
                        automatically apply normalize-string to all string
                        values derived from HTML elements and attributes, and
                        to convert non-breaking spaces into plain spaces.
  -p, --program <file>  Read HQuery expression from a file instead of the
                        command line.
  -u, --ugly            Do not pretty-print HTML markup on output.
  -v, --verbose         Print verbose query parsing and evaluation information
                        to stderr.
  --version             Display the installed HQ version.

HTML is read from stdin.

"""

from __future__ import print_function

from docopt import docopt

from .hquery.evaluation_error import HqueryEvaluationError
from .hquery.hquery_processor import HqueryProcessor, HquerySyntaxError
from .output import convert_results_to_output_text
from .soup_util import make_soup
from .verbosity import verbose_print, set_verbosity

__version__ = '0.0.4'


def main():
    from sys import stderr, stdin   # So py.tests have a chance to hook stdout & stderr

    args = docopt(__doc__, version='HQ {0}'.format(__version__))
    preserve_space = bool(args['--preserve'])
    set_verbosity(bool(args['--verbose']))

    try:
        if args['--file']:
            with open(args['--file']) as file:
                source = file.read()
        else:
            source = stdin.read()
        verbose_print('Read {0} characters of input'.format(len(source)))
        soup = make_soup(source)

        if args['--program']:
            with open(args['--program']) as file:
                expression = file.read()
        else:
            expression = args['<expression>']
        if len(expression) > 0:
            result = HqueryProcessor(expression, preserve_space).query(soup)
        else:
            result = [soup]

        print(convert_results_to_output_text(result, pretty=(not args['--ugly']), preserve_space=preserve_space))

    except HquerySyntaxError as error:
        print('\nSYNTAX ERROR: {0}\n'.format(str(error)), file=stderr)
    except HqueryEvaluationError as error:
        print('\nQUERY ERROR: {0}\n'.format(str(error)), file=stderr)


if __name__ == '__main__':
    main()
