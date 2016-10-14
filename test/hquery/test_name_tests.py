import os
import sys

from hq.output import convert_results_to_output_text
from hq.soup_util import make_soup
from hq.hquery.hquery_processor import HqueryProcessor

sys.path.insert(0, os.path.abspath('../..'))

from ..common_test_util import expected_result
from test.hquery.hquery_test_util import query_html_doc


def test_name_test_is_case_insensitive():
    html_body = """
    <SPAN>one</SPAN>
    <sPaN>two</sPaN>
    <span>three</span>"""
    actual = query_html_doc(html_body, '/html/body/SpAn')
    assert actual == expected_result("""
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
    raw_result = HqueryProcessor('/html').query(make_soup(html))
    actual = convert_results_to_output_text(raw_result)
    assert actual == expected_result("""
    <html id="root">
    </html>""")


def test_name_test_tolerates_hyphens_in_element_names():
    html_body = "<special-name></special-name>"
    assert query_html_doc(html_body, '//special-name') == expected_result("""
    <special-name>
    </special-name>""")


def test_name_test_tolerates_hyphens_in_attribute_names():
    html_body = "<div special-name='special-value'></div>"
    assert query_html_doc(html_body, '//div/@special-name') == expected_result('special-name="special-value"')
