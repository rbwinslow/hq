import os
import sys

sys.path.insert(0, os.path.abspath('../..'))

from ..common_test_util import expected_result
from test.hquery.hquery_test_util import query_html_doc


def test_the_sum_of_decimals_is_a_decimal():
    assert query_html_doc('', '90+8.6') == expected_result('98.6')
    assert query_html_doc('', '-0.2 + 0.1') == expected_result('-0.1')


def test_the_sum_of_integers_is_an_integer():
    assert query_html_doc('', '40+2') == expected_result('42')
    assert query_html_doc('', '-1 + 1') == expected_result('0')


def test_integer_result_of_adding_decimals_is_an_integer():
    assert query_html_doc('', '41.5 + 0.5') == expected_result('42')


def test_subtraction_operator():
    assert query_html_doc('', '43.5 - 1.5') == expected_result('42')


def test_multiplication_operator():
    assert query_html_doc('', '3 * 3.1') == expected_result('9.3')


def test_div_operator():
    assert query_html_doc('', '6div2') == expected_result('3')


def test_mod_operator():
    assert query_html_doc('', '11 mod 5') == expected_result('1')


def test_interpretation_of_div_and_mod_and_other_arithmetic_operators_as_operators_vs_node_tests():
    div = """
    <div>
    </div>"""
    mod = """
    <mod>
    </mod>"""

    assert query_html_doc(div, 'div', wrap_body=False) == expected_result(div)
    assert query_html_doc(mod, '/ mod', wrap_body=False) == expected_result(mod)
    assert query_html_doc(div, 'boolean(div)', wrap_body=False) == 'true'
    assert query_html_doc(mod, 'boolean(div)', wrap_body=False) == 'false'

    div_with_text = '<div>bar</div>'
    query_with_div_after_comma = 'starts-with(concat("foo ", div), "foo ba")'
    assert query_html_doc(div_with_text, query_with_div_after_comma, wrap_body=False) == 'true'

    assert query_html_doc(div, 'number("84")div2') == '42'
    assert query_html_doc(div, 'let $x := 4 return $x div 2') == '2'

    rect = '<rect id="foo" height="2" width="10"/>'
    assert query_html_doc(rect, 'let $r := //rect return $r/@height * $r/@width') == '20'

    num_in_text = """
    <span>not selected</span>
    <span id="foo">42</span>"""
    assert query_html_doc(num_in_text, '//span[@id="foo"] mod 10') == '2'
