
from test.common_test_util import expected_result
from test.hquery.hquery_test_util import query_html_doc


def test_union_decomposition_with_parentheses():
    html_body = """
    <h1>heading</h1>
    <p>content</p>
    <h1>another heading</h1>"""
    assert query_html_doc(html_body, '(//h1 | //p) => ("fizz" | "buzz")') == expected_result("""
    fizz
    buzz
    fizz""")


def test_union_decomposition_naked():
    html_body = """
    <h1>heading</h1>
    <p>content</p>
    <h1>another heading</h1>"""
    assert query_html_doc(html_body, '(//h1 | //p) => `h1 $_` | `p $_`') == expected_result("""
    h1 heading
    p content
    h1 another heading""")


def test_union_decomposition_applies_first_matching_clause():
    html_body = """
    <div>div1</div>
    <p>p1</p>
    <div>
        <p>p2</p>
    </div>"""
    query = '(//p | /html/body/div | /html/body//*) => "one" | "two" | "three"'
    assert query_html_doc(html_body, query) == expected_result("""
    two
    one
    two
    one""")
