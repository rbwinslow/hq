import os
import sys

sys.path.insert(0, os.path.abspath('../..'))

from ..test_util import expected_result, query_html_doc


def test_relational_comparison_of_numbers():
    assert query_html_doc('', '1.01>1') == expected_result('true')
    assert query_html_doc('', '1 > 2') == expected_result('false')
    assert query_html_doc('', '2>2') == expected_result('false')

    assert query_html_doc('', '1 < 2') == expected_result('true')
    assert query_html_doc('', '2<1.9999') == expected_result('false')
    assert query_html_doc('', '42 <42') == expected_result('false')

    assert query_html_doc('', '3>=3') == expected_result('true')
    assert query_html_doc('', '3>= 3.01') == expected_result('false')

    assert query_html_doc('', '2 <=2') == expected_result('true')
    assert query_html_doc('', '1.999<= 2') == expected_result('true')
    assert query_html_doc('', '2.001 <= 2') == expected_result('false')


def test_relational_comparison_of_non_numeric_primitives_with_numbers():
    assert query_html_doc('', 'true() <= 0') == expected_result('false')
    assert query_html_doc('', '1 > false()') == expected_result('true')

    assert query_html_doc('', '"5" < 4') == expected_result('false')
    assert query_html_doc('', '5 > "4"') == expected_result('true')


def test_relational_comparison_of_non_numeric_primitives_with_one_another():
    assert query_html_doc('', 'true() <= false()') == expected_result('false')
    assert query_html_doc('', 'true() > "0.9"') == expected_result('true')
    assert query_html_doc('', '"0.9" < true()') == expected_result('true')
    assert query_html_doc('', '"1.0" >= "1.1"') == expected_result('false')


def test_relational_comparison_involving_two_node_sets():
    html_body = """
    <p>9</p>
    <p>10</p>
    <div>10</div>
    <div>11</div>"""

    assert query_html_doc(html_body, '//p > //div') == expected_result('false')
    assert query_html_doc(html_body, '//p >= //div') == expected_result('true')
    assert query_html_doc(html_body, '//div[position()=1] <= //p') == expected_result('true')


def test_relational_comparison_between_a_node_set_and_a_number():
    html_body = """
    <div>9.9</div>
    <div>10.1</div>"""
    assert query_html_doc(html_body, '//div > 10') == expected_result('true')
    assert query_html_doc(html_body, '10.1 < //div') == expected_result('false')
    assert query_html_doc(html_body, '//div <= 9.9') == expected_result('true')


def test_relational_comparison_between_a_node_set_and_a_string():
    html_body = """
    <div>9.9</div>
    <div>10.1</div>"""
    assert query_html_doc(html_body, '//div > "10"') == expected_result('true')
    assert query_html_doc(html_body, '"10.1" < //div') == expected_result('false')
    assert query_html_doc(html_body, '//div <= "9.9"') == expected_result('true')


def test_relational_comparison_between_a_node_set_and_a_boolean_value():
    html_body = """
    <div>2</div>
    <div>1</div>"""
    assert query_html_doc(html_body, '//div <= false()') == expected_result('false')
    assert query_html_doc(html_body, 'true() >= //div') == expected_result('true')
