from textwrap import dedent

from hq.soup_util import make_soup


def eliminate_blank_lines(s):
    return '\n'.join([line for line in s.split('\n') if line.strip() != ''])


def expected_result(contents):
    return dedent(contents.lstrip('\n'))


def soup_with_body(contents):
    return make_soup(wrap_html_body(contents))


def wrap_html_body(contents):
    return '<html><body>{0}</body></html>'.format(contents)
