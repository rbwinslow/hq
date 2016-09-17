from test.common_test_util import expected_result
from test.xpath.xpath_test_util import query_html_doc


def test_parentheses_boost_precedence():
    assert query_html_doc('', '(2+3)*3') == expected_result('15.0')
    assert query_html_doc('', '3*(3+2)') == expected_result('15.0')
    assert query_html_doc('', '2+3*3 != (2+3)*3') == expected_result('true')
