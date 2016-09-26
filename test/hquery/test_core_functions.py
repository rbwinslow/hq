import os
import sys

sys.path.insert(0, os.path.abspath('../..'))

from ..common_test_util import expected_result
from test.hquery.hquery_test_util import query_html_doc


def test_boolean_function_converts_numbers_according_to_w3c_rules():
    assert query_html_doc('', 'boolean(0)') == expected_result('false')
    assert query_html_doc('', 'boolean(-0)') == expected_result('false')
    assert query_html_doc('', 'boolean(1)') == expected_result('true')
    assert query_html_doc('', 'boolean(-1)') == expected_result('true')
    assert query_html_doc('', 'false() = boolean(false())') == expected_result('true')
    assert query_html_doc('', 'boolean(0 div 0)') == expected_result('false')


def test_boolean_function_converts_node_sets_according_to_w3c_rules():
    assert query_html_doc('<div></div>', 'boolean(//div)') == expected_result('true')
    assert query_html_doc('<div></div>', 'boolean(//p)') == expected_result('false')


def test_boolean_function_converts_strings_according_to_w3c_rules():
    assert query_html_doc('', 'boolean("")') == expected_result('false')
    assert query_html_doc('', 'boolean(" ")') == expected_result('true')


def test_number_function_converts_string_to_number():
    assert query_html_doc('', 'number("43") + number("-1")') == expected_result('42')
    assert query_html_doc('', 'number("10") + number("1.11")') == expected_result('11.11')


def test_number_function_converts_boolean_values_to_one_and_zero():
    assert query_html_doc('', 'number(true())') == expected_result('1')
    assert query_html_doc('', 'number(false())') == expected_result('0')


def test_number_function_converts_node_set_based_on_string_value_of_first_node_in_doc_order():
    html_body = """
    <div>
        <div>
            <p>98.6</p>
        </div>
    </div>
    <p>24</p>"""
    assert query_html_doc(html_body, 'number(//p)') == expected_result('98.6')


def test_true_and_false_functions_return_expected_values():
    assert query_html_doc('', 'false()') == expected_result('false')
    assert query_html_doc('', 'true()') == expected_result('true')
    assert query_html_doc('', 'true() = false()') == expected_result('false')
    assert query_html_doc('', 'true() != false()') == expected_result('true')


def test_position_function_in_predicate_applies_to_current_step_only():
    html_body = """
    <table>
        <tr class="select-me">
            <td>one</td>
            <td>two</td>
        </tr>
        <tr class="forget-me">
            <td>uno</td>
            <td>dos</td>
        </tr>
        <tr class="select-me">
            <td>ichi</td>
            <td>ni</td>
        </tr>
    </table>"""
    assert query_html_doc(html_body, '//tr[@class="select-me"]/td[position()=2]') == expected_result("""
    <td>
     two
    </td>
    <td>
     ni
    </td>""")


def test_position_function_in_second_predicate_applies_to_results_from_first_predicate():
    html_body = """
    <table>
        <tr class="select-me">
            <td>one</td>
            <td>two</td>
        </tr>
        <tr class="forget-me">
            <td>uno</td>
            <td>dos</td>
        </tr>
        <tr class="select-me">
            <td>ichi</td>
            <td>ni</td>
        </tr>
    </table>"""
    assert query_html_doc(html_body, '//td[../@class="select-me"][position()=1]') == expected_result("""
    <td>
     one
    </td>
    <td>
     ichi
    </td>""")
