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


def test_ceiling_returns_expected_integer_values_baserd_on_xpath_3_examples():
    assert query_html_doc('', 'ceiling(10.5)') == '11'
    assert query_html_doc('', 'ceiling(-10.5)') == '-10'


def test_floor_returns_expected_integer_values_baserd_on_xpath_3_examples():
    assert query_html_doc('', 'floor(10.5)') == '10'
    assert query_html_doc('', 'floor(-10.5)') == '-11'


def test_id_function_returns_node_set_where_node_ids_match_any_names_in_whitespace_separated_list():
    html_body = """
    <p id="one">one</p>
    <p id="two">two</p>
    <p id="3">three</p>"""
    assert query_html_doc(html_body, 'id("one")') == expected_result("""
    <p id="one">
     one
    </p>""")
    assert query_html_doc(html_body, 'id("one 3")') == expected_result("""
    <p id="one">
     one
    </p>
    <p id="3">
     three
    </p>""")
    assert query_html_doc(html_body, 'id(3)') == expected_result("""
    <p id="3">
     three
    </p>""")


def test_id_function_crazy_use_case_where_id_values_are_derived_from_string_values_of_nodes_in_node_set():
    html_body = """
    <ul>
        <li>one</li>
        <li>2</li>
    </ul>
    <p id="one">one</p>
    <p id="2">two</p>"""
    assert query_html_doc(html_body, 'id(//li)') == expected_result("""
    <p id="one">
     one
    </p>
    <p id="2">
     two
    </p>""")


def test_name_function_returns_tag_name_of_given_element_or_first_element_if_given_a_node_set():
    html_body = '<div></div><p></p>'
    assert query_html_doc(html_body, 'name(/html/body/*)') == 'div'


def test_name_function_returns_name_of_context_node_if_passed_no_argument():
    html_body = """
    <div>not selected</div>
    <p>selected</p>"""
    assert query_html_doc(html_body, '/html/body/*[name() = "p"]') == expected_result("""
    <p>
     selected
    </p>""")


def test_name_function_returns_empty_string_if_passed_a_node_that_is_not_an_element():
    html_body = 'Text comes first <span>then element</span>'
    assert query_html_doc(html_body, 'name(/html/body/node()[1])') == ''
    assert query_html_doc(html_body, 'name(/html/body/node()[2])') == 'span'


def test_not_function_produces_expected_results():
    assert query_html_doc('', 'not(false())') == expected_result('true')
    assert query_html_doc('', 'not(not("foo" = "bar"))') == expected_result('false')
    assert query_html_doc('', 'not(0)') == expected_result('true')
    assert query_html_doc('', 'not(10000)') == expected_result('false')


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


def test_round_function_follows_xpath_1_rules_for_positive_numbers_but_python_rules_for_negative_ones():
    """
    Not fooling with positive or negative infinity or zero, nor the numeric type business in the XPath 3.0 functions
    spec.. Also not, as the test name attests, respecting XPath 1 rules for negative numbers, as Python rounds away
    from zero and I anticipate some tiresome drudgery for no particular benefit (again, HQuery is not intended as an
    execution target for existing XPath code).
    """
    assert query_html_doc('', 'round(5.49)') == '5'
    assert query_html_doc('', 'round(5.5)') == '6'
    assert query_html_doc('', 'round(1 div 0)') == 'NaN'
    assert query_html_doc('', 'round(-5.5)') == '-6'
    assert query_html_doc('', 'round(-5.49)') == '-5'


def test_round_function_supports_an_optional_precision_argument():
    assert query_html_doc('', 'round(3.456)') == '3'
    assert query_html_doc('', 'round(3.456, 1)') == '3.5'
    assert query_html_doc('', 'round(3.456, 2)') == '3.46'
    assert query_html_doc('', 'round(3.456, 3)') == '3.456'


def test_substring_function_behaves_reasonably_and_lets_agree_to_ignore_all_that_NaN_crap():
    assert query_html_doc('', 'substring("12345", 1.5, 2.6)') == '234'
    assert query_html_doc('', 'substring("12345", 0, 3)') == '12'
    assert query_html_doc('', 'substring("12345", -1, 3)') == '1'
    assert query_html_doc('', 'substring("12345", 5, 2)') == '5'


def test_substring_after_and_substring_before_work_per_spec():
    assert query_html_doc('', 'substring-after("1999/04/01", "/")') == '04/01'
    assert query_html_doc('', 'substring-after("1999/04/01", ":")') == ''
    assert query_html_doc('', 'substring-before("1999/04/01", "/")') == '1999'
    assert query_html_doc('', 'substring-before("1999/04/01", ":")') == ''


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


def test_string_function_returns_expected_results_for_various_objects():
    html_body = """
    <p>one</p>
    <p>two</p>"""

    assert query_html_doc(html_body, 'string(//p)') == expected_result('one')
    assert query_html_doc('', 'string(2 div 0)') == expected_result('NaN')
    assert query_html_doc('', 'string(-0)') == expected_result('0')
    assert query_html_doc('', 'string(-9)') == expected_result('-9')
    assert query_html_doc('', 'string(98.6)') == expected_result('98.6')
    assert query_html_doc('', 'string(true())') == expected_result('true')
    assert query_html_doc('', 'string(1 = -1)') == expected_result('false')


def test_string_value_of_an_element_with_mixed_content_inserts_proper_spaces_between_text_runs():
    html_body = '<p>once <a href>twice</a> thrice</p>'
    assert query_html_doc(html_body, 'string(//p)') == expected_result('once twice thrice')


def test_string_length_function_returns_expected_values():
    assert query_html_doc('', 'string-length("foo")') == expected_result('3')
    assert query_html_doc('', 'string-length("")') == expected_result('0')


def test_sum_function_sums_number_interpretation_of_items_in_sequence():
    html_body = """
    <span>30</span>
    <div value="10.42"></div>
    <span>2</span>"""

    assert query_html_doc(html_body, 'sum(//span)') == '32'
    assert query_html_doc(html_body, 'sum((//span, //div/@value))') == '42.42'


def test_sum_function_supports_zero_value_for_empty_sequence_as_second_argument():
    assert query_html_doc('', 'sum(//span, "zero")') == 'zero'


def test_various_functions_use_context_node_when_no_argument_passed():
    html_body = """
    <p>first</p>
    <p>foo   bar</p>
    <p>last</p>"""

    assert query_html_doc(html_body, '//p[string() = "first"]/text()') == expected_result('first')
    assert query_html_doc(html_body, '//p[normalize-space() = "foo bar"]/text()', preserve_space=True) == \
           expected_result('foo   bar')
    assert query_html_doc(html_body, '//p[string-length() = 4]/text()') == expected_result('last')
