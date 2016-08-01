
import os
import sys

sys.path.insert(0, os.path.abspath('../..'))

from ..test_util import expected_html, process_xpath_query


def test_tag_node_test_selects_tag_children_but_not_other_stuff():
    html_body = """
    <h1></h1>
    <!-- comment -->
    Has he ever whaled it any?
    <p></p>"""
    actual = process_xpath_query(html_body, '/html/body/node()')
    assert actual == expected_html("""
    <h1>
    </h1>
    <p>
    </p>""")


def test_tag_node_test_selects_descendants():
    html_body = """
    <!-- a section -->
    <div>
        <p>text</p>
    </div>"""
    actual = process_xpath_query(html_body, '/html/body/descendant::node()')
    assert actual == expected_html("""
    <div>
     <p>
      text
     </p>
    </div>
    <p>
     text
    </p>""")


def test_tag_node_test_selects_parent():
    html_body = """
    <section>
        <div id="id">
            <p></p>
        </div>
    </section>"""
    actual = process_xpath_query(html_body, '/html/body/section/div/p/parent::node()')
    assert actual == expected_html("""
    <div id="id">
     <p>
     </p>
    </div>""")


def test_tag_node_test_selects_ancestors():
    html_body = """
    <div id="id">
        <p></p>
    </div>"""
    actual = process_xpath_query(html_body, '/html/body/div/p/ancestor::node()')
    assert actual == expected_html("""
    <div id="id">
     <p>
     </p>
    </div>
    <body>
     <div id="id">
      <p>
      </p>
     </div>
    </body>
    <html>
     <body>
      <div id="id">
       <p>
       </p>
      </div>
     </body>
    </html>""")


def test_text_node_test_selects_disjoint_text_nodes():
    html_body = """<p>one<span>two</span>three</p>"""
    actual = process_xpath_query(html_body, '/html/body/p/text()')
    assert actual == expected_html("""
    one
    three""")
