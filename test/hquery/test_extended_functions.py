import re

from test.common_test_util import expected_result
from test.hquery.hquery_test_util import query_html_doc


def test_class_function_returns_true_when_element_has_name_in_class_attribute():
    html_body = """
    <p class="not selected">not selected</p>
    <p class="foo bar">expected</p>"""

    assert query_html_doc(html_body, 'class(//p[1], "foo")') == 'false'
    assert query_html_doc(html_body, 'class(//p[2], "foo")') == 'true'
    assert query_html_doc(html_body, '//p[class("bar")]/text()') == 'expected'


def test_matches_function_performs_regex_matching_as_per_xpath_30_functions_spec():
    html_body = """
    <p>moe</p>
    <p>larry</p>
    <p>curly</p>"""

    assert query_html_doc(html_body, '//p[matches(text(), "^l[ary]+")]/text()') == expected_result('larry')
    assert query_html_doc(html_body, '//p[matches(text(), ".URL.", "i")]/text()') == expected_result('curly')


def test_matches_function_supports_a_subset_of_xpath_30_flag_values():
    html_body = """
    <p>first</p>
    <p>second one</p>
    <p>
        multiple
        lines
        of
        text
    </p>"""
    multiline_pattern = r'.+multiple.+text.+'

    assert query_html_doc(html_body, r'//p[matches(text(), "\w+RST", "i")]/text()') == expected_result('first')
    assert query_html_doc(html_body, r'//p[matches(text(), ".+lines.+text")]', preserve_space=True) == ''
    assert re.match(
        multiline_pattern,
        query_html_doc(html_body, r'//p[matches(text(), ".+lines.+text", "s")]', preserve_space=True),
        re.S
    )
    assert query_html_doc(html_body, r'//p[matches(text(), "^ *lines$")]', preserve_space=True) == ''
    assert re.match(
        multiline_pattern,
        query_html_doc(html_body, r'//p[matches(text(), "^\s*lines$", "m")]', preserve_space=True),
        re.S
    )
    assert query_html_doc(html_body, r'//p[matches(text(), "sec  ond\sone")]/text()') == ''
    assert query_html_doc(html_body, r'//p[matches(text(), "sec  ond\sone", "x")]/text()') == 'second one'


def test_matches_function_extends_to_using_context_node_when_passed_no_input_string():
    html_body = """
    <p>bar</p>
    <p>foo</p>"""

    assert query_html_doc(html_body, '//p[matches("^f.+")]/text()') == expected_result('foo')


def test_even_and_odd_functions_select_the_appropriate_elements_based_on_position():
    html_body = """
    <p>You</p>
    <p>I</p>
    <p>are</p>
    <p>am</p>
    <p>odd.</p>
    <p>even.</p>"""

    assert query_html_doc(html_body, '//p[even()]/text()') == expected_result("""
    I
    am
    even.""")
    assert query_html_doc(html_body, '//p[odd()]/text()') == expected_result("""
    You
    are
    odd.""")
