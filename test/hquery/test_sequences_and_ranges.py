from test.common_test_util import expected_result
from test.hquery.hquery_test_util import query_html_doc


def test_range_expression_produces_expected_sequence():
    assert query_html_doc('', '(1 to 3)') == expected_result("""
    1
    2
    3""")


def test_range_expression_works_without_parentheses():
    assert query_html_doc('', '1 to 3') == expected_result("""
    1
    2
    3""")


def test_range_operator_is_interpreted_as_name_test_in_appropriate_contexts():
    html_body = '<to>from</to>'
    assert query_html_doc(html_body, '//to') == expected_result("""
    <to>
     from
    </to>""")


def test_range_within_sequence_constructor_collapses_into_sequence():
    assert query_html_doc('', '(1, 2 to 4)') == expected_result("""
    1
    2
    3
    4""")


def test_sequences_collapse():
    assert query_html_doc('', '(1, (2, 3), 4)') == expected_result("""
    1
    2
    3
    4""")


def test_string_value_of_a_sequence_is_concatenation_of_all_items_unlike_node_set():
    html_body = """
    <p>one</p>
    <p>two</p>"""

    assert query_html_doc(html_body, 'let $_ := //p/text() return string($_)') == 'one'
    assert query_html_doc(html_body, 'let $_ := ("one", "two") return string($_)') == 'onetwo'
