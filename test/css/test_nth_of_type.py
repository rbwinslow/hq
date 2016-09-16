import os
import sys

sys.path.insert(0, os.path.abspath('../..'))

from hq.output import result_object_to_text
from hq.css.query_css import query_css
from ..common_test_util import soup_with_body, expected_result


def test_nth_of_type_pseudoclass_support():
    html = soup_with_body('<div>one</div><div>two</div>')
    raw_result = query_css(html, 'div:nth-of-type(2)')
    actual = result_object_to_text(raw_result)
    assert actual == expected_result("""
    <div>
     two
    </div>""")
