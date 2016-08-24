import os
import sys

sys.path.insert(0, os.path.abspath('../..'))

from ..test_util import expected_result, process_xpath_query


def test_boolean_function_converts_numbers_according_to_w3c_rules():
    assert process_xpath_query('', 'boolean(0)') == expected_result('false')
    assert process_xpath_query('', 'boolean(-0)') == expected_result('false')
    assert process_xpath_query('', 'boolean(1)') == expected_result('true')
    assert process_xpath_query('', 'boolean(-1)') == expected_result('true')
    # Restore when division is implemented:
    # assert process_xpath_query('', 'boolean(0/0)') == expected_result('false')


def test_boolean_function_converts_node_sets_according_to_w3c_rules():
    assert process_xpath_query('<div></div>', 'boolean(//div)') == expected_result('true')
    assert process_xpath_query('<div></div>', 'boolean(//p)') == expected_result('false')


def test_boolean_function_converts_strings_according_to_w3c_rules():
    assert process_xpath_query('', 'boolean("")') == expected_result('false')
    assert process_xpath_query('', 'boolean(" ")') == expected_result('true')


def test_number_function_converts_string_to_number():
    actual = process_xpath_query('', 'number("43") + number("-1")')
    assert actual == expected_result('42.0')
