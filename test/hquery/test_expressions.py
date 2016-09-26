from test.common_test_util import expected_result
from test.hquery.hquery_test_util import query_html_doc


def test_parentheses_boost_precedence():
    assert query_html_doc('', '(2+3)*3') == expected_result('15')
    assert query_html_doc('', '3*(3+2)') == expected_result('15')
    assert query_html_doc('', '2+3*3 != (2+3)*3') == expected_result('true')


def test_union_operator_combines_node_sets():
    html_body = """
    <div>one</div>
    <div>two</div>
    <p>three</p>"""
    assert query_html_doc(html_body, '//div | //p') == expected_result("""
    <div>
     one
    </div>
    <div>
     two
    </div>
    <p>
     three
    </p>""")


def test_union_operator_produces_node_set_sorted_in_document_order():
    html_body = """
    <div>one</div>
    <p>two</p>
    <div>three</div>"""
    assert query_html_doc(html_body, '//p | //div') == expected_result("""
    <div>
     one
    </div>
    <p>
     two
    </p>
    <div>
     three
    </div>""")
