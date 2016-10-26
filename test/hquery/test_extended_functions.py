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


def test_lower_case_and_upper_case_change_string_case_as_expected():
    assert query_html_doc('', 'lower-case("Foo BAR")') == 'foo bar'
    assert query_html_doc('', 'upper-case("fOO bar")') == 'FOO BAR'


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


def test_replace_function_performs_regex_replacement_as_per_xpath_30_functions_spec():
    assert query_html_doc('', 'replace("dog mattress dog", "^dog", "cat")') == 'cat mattress dog'


def test_replace_function_extends_standard_by_taking_string_value_of_any_type_of_input_object():
    assert query_html_doc('<p>hello</p>', 'replace(//p, "h", "j")') == 'jello'


def test_string_join_function_accepts_sequence_as_first_parameter_and_delimiter_as_second():
    assert query_html_doc('', 'string-join(1 to 3, ", ")') == '1, 2, 3'


def test_string_join_second_argument_is_optional():
    assert query_html_doc('', 'string-join(1 to 2)') == '12'


def test_tokenize_function_breaks_up_strings_as_per_xpath_30_functions_spec():
    assert query_html_doc('', 'tokenize("Moe:Larry:..Curly", ":\.*")') == expected_result("""
    Moe
    Larry
    Curly""")
    assert query_html_doc('', 'tokenize("HaxtaXpatience", "x", "i")') == expected_result("""
    Ha
    ta
    patience""")
    assert query_html_doc('', 'count(tokenize("haxtaxstax", "x"))') == '4'


def test_tokenize_function_extends_standard_by_supporting_any_object_as_input():
    assert query_html_doc('<p>foo,bar</p>', 'tokenize(//p, ",")') == expected_result("""
    foo
    bar""")
