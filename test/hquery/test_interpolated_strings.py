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
