import os
import sys

sys.path.insert(0, os.path.abspath('../..'))

from ..test_util import expected_result, process_xpath_query


def test_addition_operator():
    assert process_xpath_query('', '40+2') == expected_result('42.0')
    assert process_xpath_query('', '-0.1 + 0.1') == expected_result('0.0')


def test_subtraction_operator():
    assert process_xpath_query('', '43.5 - 1.5') == expected_result('42.0')


def test_multiplication_operator():
    assert process_xpath_query('', '3 * 3.1') == expected_result('9.3')


def test_div_operator():
    assert process_xpath_query('', '6div2') == expected_result('3.0')


def test_mod_operator():
    assert process_xpath_query('', '11 mod 5') == expected_result('1.0')


def test_interpretation_of_div_and_mod_as_operators_or_name_tests():
    div = """
    <div>
    </div>"""
    mod = """
    <mod>
    </mod>"""

    assert process_xpath_query(div, 'div', wrap_body=False) == expected_result(div)
    assert process_xpath_query(mod, '/ mod', wrap_body=False) == expected_result(mod)
    assert process_xpath_query(div, 'boolean(div)', wrap_body=False) == expected_result('true')
    assert process_xpath_query(mod, 'boolean(div)', wrap_body=False) == expected_result('false')

    div_with_text = '<div>bar</div>'
    query_with_div_after_comma = 'starts-with(concat("foo ", div), "foo ba")'
    assert process_xpath_query(div_with_text, query_with_div_after_comma, wrap_body=False) == expected_result('true')

    assert process_xpath_query(div, 'number("84")div2') == expected_result('42.0')
