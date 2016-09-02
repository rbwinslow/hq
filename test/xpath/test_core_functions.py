import os
import sys

sys.path.insert(0, os.path.abspath('../..'))

from ..test_util import expected_result, query_html_doc


def test_boolean_function_converts_numbers_according_to_w3c_rules():
    assert query_html_doc('', 'boolean(0)') == expected_result('false')
    assert query_html_doc('', 'boolean(-0)') == expected_result('false')
    assert query_html_doc('', 'boolean(1)') == expected_result('true')
    assert query_html_doc('', 'boolean(-1)') == expected_result('true')
    assert query_html_doc('', 'false() = boolean(false())') == expected_result('true')
    # Restore when division is implemented:
    # assert process_xpath_query('', 'boolean(0/0)') == expected_result('false')


def test_boolean_function_converts_node_sets_according_to_w3c_rules():
    assert query_html_doc('<div></div>', 'boolean(//div)') == expected_result('true')
    assert query_html_doc('<div></div>', 'boolean(//p)') == expected_result('false')


def test_boolean_function_converts_strings_according_to_w3c_rules():
    assert query_html_doc('', 'boolean("")') == expected_result('false')
    assert query_html_doc('', 'boolean(" ")') == expected_result('true')


def test_number_function_converts_string_to_number():
    actual = query_html_doc('', 'number("43") + number("-1")')
    assert actual == expected_result('42.0')


def test_true_and_false_functions_return_expected_values():
    assert query_html_doc('', 'false()') == expected_result('false')
    assert query_html_doc('', 'true()') == expected_result('true')
    assert query_html_doc('', 'true() = false()') == expected_result('false')
    assert query_html_doc('', 'true() != false()') == expected_result('true')
