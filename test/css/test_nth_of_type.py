import os
import sys

sys.path.insert(0, os.path.abspath('../..'))

from hq.output import soup_objects_to_text
from hq.css.query_css import query_css
from ..test_util import soup_with_body, expected_html


def test_nth_of_type_pseudoclass_support():
    html = soup_with_body('<div>one</div><div>two</div>')
    raw_result = query_css(html, 'div:nth-of-type(2)')
    actual = soup_objects_to_text(raw_result)
    assert actual == expected_html("""
    <div>
     two
    </div>""")
