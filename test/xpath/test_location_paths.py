import os
import sys

sys.path.insert(0, os.path.abspath('../..'))

from bs4 import BeautifulSoup
from hq.output import result_object_to_text
from hq.xpath.query_xpath import query_xpath

from ..test_util import expected_result, process_xpath_query


def test_absolute_location_path_should_find_multiple_grandchildren():
    actual = process_xpath_query('<div>one</div><p>not a div</p><div>two</div>', '/html/body/div')
    assert actual == expected_result("""
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
    actual = result_object_to_text(raw_result)
    assert actual == expected_result("""
    <html>
     <!-- inside -->
    </html>""")


def test_relative_location_path_as_predicate():
    html_body = """
    <div>
        <span>one</span>
    </div>
    <div>
        <p>two</p>
    </div>
    <div>
        <span>three</span>
    </div>"""
    actual = process_xpath_query(html_body, '/html/body/div[span]')
    assert actual == expected_result("""
    <div>
     <span>
      one
     </span>
    </div>
    <div>
     <span>
      three
     </span>
    </div>""")


def test_abbreviated_context_node_works_in_path():
    html_body = """
    <div>
        <p>one</p>
    </div>
    <p>two</p>
    <div>
        <p>three</p>
    </div>"""
    actual = process_xpath_query(html_body, '/html/body/div/./p')
    assert actual == expected_result("""
    <p>
     one
    </p>
    <p>
     three
    </p>""")


def test_abbreviated_context_node_works_in_predicate():
    html_body = """
    <div>
        <p>one</p>
    </div>
    <p>two</p>
    <div>
        three
    </div>
    <div>
        <p>four</p>
    </div>
    """
    actual = process_xpath_query(html_body, '/html/body/node()[./p]')
    assert actual == expected_result("""
    <div>
     <p>
      one
     </p>
    </div>
    <div>
     <p>
      four
     </p>
    </div>""")


def test_abbreviated_parent_node_works_in_path():
    html_body = """
    <p>
        <span>one</span>
    </p>
    <p>
        <br/>
        <span>two</span>
    </p>"""
    actual = process_xpath_query(html_body, '//p/br/../span')
    assert actual == expected_result("""
    <span>
     two
    </span>""")


def test_abbreviated_parent_node_works_in_predicate():
    html_body = """
    <p>
        <br/>
        <span>one</span>
    </p>
    <p>
        <span>two</span>
    </p>
    <p>
        <br/>
        <span>three</span>
    </p>"""
    actual = process_xpath_query(html_body, '//span[../br]')
    assert actual == expected_result("""
    <span>
     one
    </span>
    <span>
     three
    </span>""")
