from test.common_test_util import expected_result
from test.hquery.hquery_test_util import query_html_doc


def test_escapes_work_in_string_literals():
    assert query_html_doc('', '"foo&#10;bar"') == expected_result("""
    foo
    bar""")
    assert query_html_doc('', "'foo&#10;bar'") == expected_result("""
    foo
    bar""")
    assert query_html_doc('', '`foo&#10;bar`') == expected_result("""
    foo
    bar""")
