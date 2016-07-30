from textwrap import dedent

from bs4 import BeautifulSoup


def soup_with_body(contents):
    return BeautifulSoup('<html><body>{0}</body></html>'.format(contents), 'html.parser')


def expected_html(contents):
    return dedent(contents.lstrip('\n'))
