import os
import sys

sys.path.insert(0, os.path.abspath('../..'))

from ..common_test_util import expected_result
from test.hquery.hquery_test_util import query_html_doc


def test_node_set_equality_is_based_on_text_contents():
    html_body = """
    <p>foo</p>
    <div>foo</div>"""
    actual = query_html_doc(html_body, '//p = //div')
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
    actual = query_html_doc(html_body, '//div/span = //p/span')
    assert actual == expected_result('true')


def test_equals_operator_compares_numbers():
    actual = query_html_doc('', '2.0 != 2.1')
    assert actual == expected_result('true')


def test_equals_operator_interprets_integer_and_fractional_numbers_correctly():
    actual = query_html_doc('', '101.0 != 101')
    assert actual == expected_result('false')


def test_equals_operator_compares_string_value_of_node_converted_to_number_with_number():
    actual = query_html_doc('<p>042.0</p>', '//p = 42')
    assert actual == expected_result('true')


def test_equals_operator_compares_boolean_coercion_of_node_set_with_boolean():
    html_body = '<p></p>'
    actual = query_html_doc(html_body, '//p = false()')
    assert actual == expected_result('false')


def test_equals_operator_compares_text_node_contents_with_string():
    html_body = """
    <div>
        <p>one</p>
    </div>
    <div>
        <p>two</p>
    </div>"""
    actual = query_html_doc(html_body, '/html/body/div[p/text() = "two"]')
    assert actual == expected_result("""
    <div>
     <p>
      two
     </p>
    </div>""")


def test_equals_operator_converts_non_node_sets_to_boolean_when_comparing_to_a_boolean():
    assert query_html_doc('', '1 = true()') == expected_result('true')
    assert query_html_doc('', '0 != false()') == expected_result('false')
    assert query_html_doc('', '"" = false()') == expected_result('true')
    assert query_html_doc('', '" " = true()') == expected_result('true')


def test_equals_operator_converts_non_node_sets_to_number_when_comparing_to_a_number():
    assert query_html_doc('', '0.1 = "0"') == expected_result('false')
    assert query_html_doc('', '"42" = 42.0') == expected_result('true')
    assert query_html_doc('', '"foo" = 0') == expected_result('false')  # It's NaN, not zero.


def test_equals_operator_works_with_node_sets_containing_attributes():
    html_body = """
    <div id="one"></div>
    <div id="two"></div>"""
    assert query_html_doc(html_body, '//div/attribute::id = "two"') == expected_result('true')
