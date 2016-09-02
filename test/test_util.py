from textwrap import dedent

from bs4 import BeautifulSoup
from hq.output import result_object_to_text
from hq.soup_util import make_soup
from hq.xpath.query_xpath import query_xpath


def process_xpath_query(html_body, xpath, wrap_body=True):
    soup = soup_with_body(html_body) if wrap_body else make_soup(html_body)
    raw_result = query_xpath(soup, xpath)
    return result_object_to_text(raw_result).strip()


def soup_with_body(contents):
    return make_soup('<html><body>{0}</body></html>'.format(contents))


def expected_result(contents):
    return dedent(contents.lstrip('\n'))
