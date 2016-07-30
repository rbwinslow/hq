
import os
import sys

sys.path.insert(0, os.path.abspath('../..'))

from hq.xpath.query_xpath import query_xpath
from hq.output import soup_objects_to_text
from ..test_util import soup_with_body, expected_html


def test_absolute_location_path_should_find_multiple_grandchildren():
    html = soup_with_body('<div>one</div><p>not a div</p><div>two</div>')
    raw_result = query_xpath(html, '/html/body/div')
    actual = soup_objects_to_text(raw_result)
    assert actual == expected_html("""
    <div>
     one
    </div>
    <div>
     two
    </div>""")
