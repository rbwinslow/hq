from textwrap import dedent

from bs4 import BeautifulSoup
from hq.output import result_object_to_text
from hq.soup_util import make_soup, is_any_node, root_tag_from_soup
from hq.xpath.query_xpath import query_xpath


def query_html_doc(html_body, xpath, wrap_body=True):
    soup = soup_with_body(html_body) if wrap_body else make_soup(html_body)
    raw_result = query_xpath(soup, xpath)
    return _eliminate_blank_lines(result_object_to_text(raw_result).strip())


def query_context_node(node_or_source, xpath):
    if not is_any_node(node_or_source):
        node = root_tag_from_soup(make_soup(node_or_source))
    raw_result = query_xpath(node, xpath)
    return _eliminate_blank_lines(result_object_to_text(raw_result).strip())


def soup_with_body(contents):
    return make_soup('<html><body>{0}</body></html>'.format(contents))


def expected_result(contents):
    return dedent(contents.lstrip('\n'))


def _eliminate_blank_lines(s):
    return '\n'.join([line for line in s.split('\n') if line.strip() != ''])
