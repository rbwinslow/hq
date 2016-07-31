
import os
import sys

sys.path.insert(0, os.path.abspath('../..'))

from ..test_util import expected_html, process_xpath_query


def test_child_axis_selects_only_immediate_children():
    html_body = """
    <p>uncle</p>
    <div>
        <p>niece</p>
        <p>nephew</p>
    </div>"""
    actual = process_xpath_query(html_body, '/html/body/child::p')
    assert actual == expected_html("""
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
    assert actual == expected_html("""
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
    assert actual == expected_html("""
    <div id="mom">
     <p>
      daughter
     </p>
    </div>""")
