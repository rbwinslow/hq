from test.common_test_util import expected_result
from test.hquery.hquery_test_util import query_html_doc


def test_location_path_works_as_interpolated_string_expression():
    assert query_html_doc("<div>world</div>", '`Hello, ${//div/text()}!`') == expected_result('Hello, world!')


def test_element_node_becomes_normalized_text_contents_in_interpolated_string():
    html_body = """
    <p>
        foo   bar
    </p>"""
    assert query_html_doc(html_body, '`-->${//p}<--`') == expected_result('-->foo bar<--')


def test_text_between_embedded_expressions_gets_picked_up():
    html_body = """
    <p>one</p>
    <p>two</p>
    <p>three</p>"""
    assert query_html_doc(html_body, 'let $_ := 2 return `${//p[1]}, $_, ${//p[3]}`') == 'one, 2, three'


def test_join_filter_joins_string_values_from_node_set():
    html_body = """
    <p>one</p>
    <p>two</p>
    <p>three</p>"""
    assert query_html_doc(html_body, '`${j:,://p}`') == expected_result('one,two,three')


def test_join_filter_defaults_to_empty_string_delimiter():
    html_body = """
    <p>one</p>
    <p>two</p>"""
    assert query_html_doc(html_body, '`${j:://p}`') == expected_result('onetwo')


def test_truncate_filter_elides_contents():
    html_body = "<p>The quick brown fox jumped over the lazy dog.</p>"
    assert query_html_doc(html_body, '`${t:23:?://p}`') == expected_result('The quick brown fox?')


def test_truncate_filter_defaults_to_no_suffix():
    html_body = "<p>short, sharp shock</p>"
    assert query_html_doc(html_body, '`${t:15:://p}`') == expected_result('short, sharp')


def test_filters_chain_left_to_right():
    html_body = """
    <p>one</p>
    <p>two</p>
    <p>three</p>"""
    assert query_html_doc(html_body, '`${j:, :t:12: ...://p} whatever!`') == expected_result('one, two, ... whatever!')
