from test.common_test_util import expected_result
from test.hquery.hquery_test_util import query_html_doc


def test_if_then_else_works_with_literal_conditions():
    assert query_html_doc('', 'if (true()) then "foo" else "bar"') == 'foo'
    assert query_html_doc('', 'if ("") then "foo" else "bar"') == 'bar'
    assert query_html_doc('', 'if (0.001) then "foo" else "bar"') == 'foo'


def test_if_then_else_works_with_node_sets():
    html_body = """
    <p>eekaboo</p>"""
    assert query_html_doc(html_body, 'if (//p) then //p else 1 to 3') == expected_result("""
    <p>
     eekaboo
    </p>""")
    assert query_html_doc(html_body, 'if (//div) then //p else 1 to 3') == expected_result("""
    1
    2
    3""")


def test_if_then_else_works_with_variables_in_a_flwor():
    assert query_html_doc('', 'let $x := 0.1 return if ($x - 0.1) then $x else $x + 1') == '1.1'
