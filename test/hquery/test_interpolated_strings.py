from test.common_test_util import expected_result
from test.hquery.hquery_test_util import query_html_doc


def test_location_path_works_as_interpolated_string_expression():
    assert query_html_doc("<div>world</div>", '`Hello, ${//div/text()}!`') == expected_result('Hello, world!')
