
import os
import sys

from bs4 import BeautifulSoup
from hq.output import soup_objects_to_text
from hq.xpath.query_xpath import query_xpath

sys.path.insert(0, os.path.abspath('../..'))

from ..test_util import expected_html, process_xpath_query


def test_absolute_location_path_should_find_multiple_grandchildren():
    actual = process_xpath_query('<div>one</div><p>not a div</p><div>two</div>', '/html/body/div')
    assert actual == expected_html("""
    <div>
     one
    </div>
    <div>
     two
    </div>""")


def test_path_to_root_node_succeeds_despite_other_root_level_objects():
    html = """
    <!DOCTYPE html>
    <!-- outside -->
    <html>
        <!-- inside -->
    </html>"""
    raw_result = query_xpath(BeautifulSoup(html, 'html.parser'), '/node()')
    actual = soup_objects_to_text(raw_result)
    assert actual == expected_html("""
    <html>
     <!-- inside -->
    </html>""")
