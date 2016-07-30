
import os
import sys

sys.path.insert(0, os.path.abspath('../..'))

from hq.xpath.query_xpath import query_xpath
from hq.output import soup_objects_to_text
from ..test_util import soup_with_body, expected_html


def test_child_axis_selects_only_immediate_children():
    html = soup_with_body("""
    <p>uncle</p>
    <div>
        <p>niece</p>
        <p>nephew</p>
    </div>""")
    raw_result = query_xpath(html, '/html/body/child::p')
    actual = soup_objects_to_text(raw_result)
    assert actual == expected_html("""
    <p>
     uncle
    </p>""")
