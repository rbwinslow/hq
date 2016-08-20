import os
import sys

sys.path.insert(0, os.path.abspath('../..'))

from pytest import skip

from ..test_util import expected_result, process_xpath_query


def test_node_set_equality_is_based_on_text_contents():
    html_body = """
    <p>foo</p>
    <div>foo</div>"""
    actual = process_xpath_query(html_body, '//p = //div')
    assert actual == expected_result('true')


def test_node_sets_are_equal_if_string_value_of_any_one_node_matches_string_value_of_any_from_other_set():
    html_body = """
    <div>
        <span>one</span>
        <span>two</span>
    </div>
    <p>
        <span>two</span>
        <span>three</span>
    </p>"""
    actual = process_xpath_query(html_body, '//div/span = //p/span')
    assert actual == expected_result('true')


@skip()
def test_equals_operator_compares_text_node_contents_with_string():
    html_body = """
    <div>
        <p>one</p>
    </div>
    <div>
        <p>two</p>
    </div>"""
    actual = process_xpath_query(html_body, '/html/body/div[p/text() = "two"]')
    assert actual == expected_html("""
    <div>
     <p>
      two
     </p>
    </div>""")
