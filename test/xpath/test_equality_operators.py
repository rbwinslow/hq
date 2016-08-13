import os
import sys

from pytest import skip

sys.path.insert(0, os.path.abspath('../..'))

from ..test_util import expected_html, process_xpath_query


@skip()
def test_equals_operator_compares_text_node_contents_with_string():
    html_body = """
    <div>
        <p>one</p>
    </div>
    <div>
        <p>two</p>
    </div>"""
    actual = process_xpath_query(html_body, '/html/body/div[p/text() = "two"]')
    assert actual == expected_html("""
    <div>
     <p>
      two
     </p>
    </div>""")
