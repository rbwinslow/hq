from test.common_test_util import expected_result
from test.hquery.hquery_test_util import query_html_doc


def test_range_expression_produces_expected_sequence():
    assert query_html_doc('', '(1 to 3)') == expected_result("""
    1
    2
    3""")
