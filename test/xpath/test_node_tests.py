
import os
import sys

sys.path.insert(0, os.path.abspath('../..'))

from ..test_util import expected_html, process_xpath_query


def test_node_type_test_selects_tags_but_not_other_stuff():
    html_body = """
    <h1></h1>
    <!-- comment -->
    some text
    <p></p>"""
    actual = process_xpath_query(html_body, '/html/body/node()')
    assert actual == expected_html("""
    <h1>
    </h1>
    <p>
    </p>""")


def test_text_node_test_selects_disjoint_text_nodes():
    html_body = """<p>one<span>two</span>three</p>"""
    actual = process_xpath_query(html_body, '/html/body/p/text()')
    assert actual == expected_html("""
    one
    three""")
