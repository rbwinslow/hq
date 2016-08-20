
import os
import sys

from bs4 import BeautifulSoup
from hq.output import result_object_to_text
from hq.xpath.query_xpath import query_xpath

sys.path.insert(0, os.path.abspath('../..'))

from ..test_util import expected_result, process_xpath_query


def test_name_test_is_case_insensitive():
    html_body = """
    <SPAN>one</SPAN>
    <sPaN>two</sPaN>
    <span>three</span>"""
    actual = process_xpath_query(html_body, '/html/body/SpAn')
    assert actual == expected_result("""
    <span>
     one
    </span>
    <span>
     two
    </span>
    <span>
     three
    </span>""")


def test_name_test_at_root_ignores_all_but_root_element():
    html = """
    <!DOCTYPE html>
    <!-- html -->
    <html id="root">
    </html>"""
    raw_result = query_xpath(BeautifulSoup(html, 'html.parser'), '/html')
    actual = result_object_to_text(raw_result)
    assert actual == expected_result("""
    <html id="root">
    </html>""")


def test_child_axis_selects_only_immediate_children():
    html_body = """
    <p>uncle</p>
    <div>
        <p>niece</p>
        <p>nephew</p>
    </div>"""
    actual = process_xpath_query(html_body, '/html/body/child::p')
    assert actual == expected_result("""
    <p>
     uncle
    </p>""")


def test_descendant_axis_selects_from_descendants_not_ancestors():
    html_body = """
    <div id="grandma">
        <section>
            <div>uncle</div>
            <aside>
                <div>niece</div>
            </aside>
        </section>
    </div>"""
    actual = process_xpath_query(html_body, '/html/body/div/descendant::div')
    assert actual == expected_result("""
    <div>
     uncle
    </div>
    <div>
     niece
    </div>""")


def test_parent_axis_selects_only_the_immediate_parent():
    html_body = """
    <div id="grandma">
        <div id="mom">
            <p>daughter</p>
        </div>
    </div>"""
    actual = process_xpath_query(html_body, '//p/parent::div')
    assert actual == expected_result("""
    <div id="mom">
     <p>
      daughter
     </p>
    </div>""")


def test_ancestor_axis_selects_all_matching_ancestors():
    html_body = """
    <div>
        <section>
            <div>
                <p>text</p>
            </div>
        </section>
    </div>"""
    actual = process_xpath_query(html_body, '//p/ancestor::div')
    assert actual == expected_result("""
    <div>
     <p>
      text
     </p>
    </div>
    <div>
     <section>
      <div>
       <p>
        text
       </p>
      </div>
     </section>
    </div>""")
