import os
import sys

sys.path.insert(0, os.path.abspath('../..'))

from ..common_test_util import expected_result
from test.hquery.hquery_test_util import query_html_doc


def test_relational_comparison_of_numbers():
    assert query_html_doc('', '1.01>1') == 'true'
    assert query_html_doc('', '1 > 2') == 'false'
    assert query_html_doc('', '2>2') == 'false'

    assert query_html_doc('', '1 < 2') == 'true'
    assert query_html_doc('', '2<1.9999') == 'false'
    assert query_html_doc('', '42 <42') == 'false'

    assert query_html_doc('', '3>=3') == 'true'
    assert query_html_doc('', '3>= 3.01') == 'false'

    assert query_html_doc('', '2 <=2') == 'true'
    assert query_html_doc('', '1.999<= 2') == 'true'
    assert query_html_doc('', '2.001 <= 2') == 'false'


def test_relational_comparison_of_booleans_with_one_another_and_with_other_non_node_set_primitives():
    assert query_html_doc('', 'true() <= false()') == 'false'
    assert query_html_doc('', 'true() <= 0') == 'false'
    assert query_html_doc('', '1 > false()') == 'true'
    assert query_html_doc('', 'true() >= 25') == 'true'
    assert query_html_doc('', 'true() > "0"') == 'false'


def test_relational_comparison_of_numbers_with_non_boolean_non_numeric_primitives_aka_strings():
    assert query_html_doc('', '"5" < 4') == 'false'
    assert query_html_doc('', '5 > "4"') == 'true'
    assert query_html_doc('', '"foo" >= 1') == 'false'


def test_relational_comparison_of_non_boolean_non_numeric_primitives_aka_strings_with_one_another():
    assert query_html_doc('', '"low" > "high"') == 'true'
    assert query_html_doc('', '"1.0" >= "1.1"') == 'false'
    assert query_html_doc('', '"1.1" >= "1.1"') == 'true'


def test_relational_comparison_involving_two_node_sets():
    html_body = """
    <p>9</p>
    <p>10</p>
    <div>10</div>
    <div>11</div>"""

    assert query_html_doc(html_body, '//p > //div') == 'false'
    assert query_html_doc(html_body, '//p >= //div') == 'true'
    assert query_html_doc(html_body, '//div[position()=1] <= //p') == 'true'


def test_relational_comparison_between_a_node_set_and_a_number():
    html_body = """
    <div>9.9</div>
    <div>10.1</div>"""
    assert query_html_doc(html_body, '//div > 10') == 'true'
    assert query_html_doc(html_body, '10.1 < //div') == 'false'
    assert query_html_doc(html_body, '//div <= 9.9') == 'true'


def test_relational_comparison_between_a_node_set_and_a_string():
    html_body = """
    <div>9.9</div>
    <div>10.1</div>"""
    assert query_html_doc(html_body, '//div > "10"') == 'true'
    assert query_html_doc(html_body, '"10.1" < //div') == 'false'
    assert query_html_doc(html_body, '//div <= "9.9"') == 'true'


def test_relational_comparison_between_a_node_set_and_a_boolean_value():
    html_body = """
    <div>2</div>
    <div>1</div>"""
    assert query_html_doc(html_body, '//div <= false()') == 'false'
    assert query_html_doc(html_body, 'true() >= //div') == 'true'
