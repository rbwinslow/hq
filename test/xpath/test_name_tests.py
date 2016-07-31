
import os
import sys

from bs4 import BeautifulSoup
from hq.output import soup_objects_to_text
from hq.xpath.query_xpath import query_xpath

sys.path.insert(0, os.path.abspath('../..'))

from ..test_util import expected_html, process_xpath_query


def test_name_test_is_case_insensitive():
    html_body = """
    <SPAN>one</SPAN>
    <sPaN>two</sPaN>
    <span>three</span>"""
    actual = process_xpath_query(html_body, '/html/body/SpAn')
    assert actual == expected_html("""
    <span>
     one
    </span>
    <span>
     two
    </span>
    <span>
     three
    </span>""")

def test_name_test_at_root_ignores_all_but_root_element():
    html = """
    <!DOCTYPE html>
    <!-- html -->
    <html id="root">
    </html>"""
    raw_result = query_xpath(BeautifulSoup(html, 'html.parser'), '/html')
    actual = soup_objects_to_text(raw_result)
    assert actual == expected_html("""
    <html id="root">
    </html>""")
