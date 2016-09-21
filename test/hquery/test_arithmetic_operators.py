import os
import sys

sys.path.insert(0, os.path.abspath('../..'))

from ..common_test_util import expected_result
from test.hquery.hquery_test_util import query_html_doc


def test_addition_operator():
    assert query_html_doc('', '40+2') == expected_result('42.0')
    assert query_html_doc('', '-0.1 + 0.1') == expected_result('0.0')


def test_subtraction_operator():
    assert query_html_doc('', '43.5 - 1.5') == expected_result('42.0')


def test_multiplication_operator():
    assert query_html_doc('', '3 * 3.1') == expected_result('9.3')


def test_div_operator():
    assert query_html_doc('', '6div2') == expected_result('3.0')


def test_mod_operator():
    assert query_html_doc('', '11 mod 5') == expected_result('1.0')


def test_interpretation_of_div_and_mod_as_operators_or_name_tests():
    div = """
    <div>
    </div>"""
    mod = """
    <mod>
    </mod>"""

    assert query_html_doc(div, 'div', wrap_body=False) == expected_result(div)
    assert query_html_doc(mod, '/ mod', wrap_body=False) == expected_result(mod)
    assert query_html_doc(div, 'boolean(div)', wrap_body=False) == expected_result('true')
    assert query_html_doc(mod, 'boolean(div)', wrap_body=False) == expected_result('false')

    div_with_text = '<div>bar</div>'
    query_with_div_after_comma = 'starts-with(concat("foo ", div), "foo ba")'
    assert query_html_doc(div_with_text, query_with_div_after_comma, wrap_body=False) == expected_result('true')

    assert query_html_doc(div, 'number("84")div2') == expected_result('42.0')
