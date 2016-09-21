
import os
import sys

sys.path.insert(0, os.path.abspath('../..'))

from ..common_test_util import expected_result
from .hquery_test_util import query_html_doc


def test_any_node_test_selects_all_node_types():
    html_body = """Has he ever whaled it any?<h1>
    </h1>
    <!-- comment -->
    <p></p>"""
    assert query_html_doc(html_body, '/html/body/node()') == expected_result("""
    Has he ever whaled it any?
    <h1>
    </h1>
    <!-- comment -->
    <p>
    </p>""")


def test_tag_node_test_selects_tag_children_but_not_other_stuff():
    html_body = """
    <h1></h1>
    <!-- comment -->
    Has he ever whaled it any?
    <p></p>"""
    actual = query_html_doc(html_body, '/html/body/*')
    assert actual == expected_result("""
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
    actual = query_html_doc(html_body, '/html/body/descendant::*')
    assert actual == expected_result("""
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
    actual = query_html_doc(html_body, '/html/body/section/div/p/parent::*')
    assert actual == expected_result("""
    <div id="id">
     <p>
     </p>
    </div>""")


def test_tag_node_test_selects_ancestors():
    html_body = """
    <div id="id">
        <p></p>
    </div>"""
    actual = query_html_doc(html_body, '/html/body/div/p/ancestor::*')
    assert actual == expected_result("""
    <html>
     <body>
      <div id="id">
       <p>
       </p>
      </div>
     </body>
    </html>
    <body>
     <div id="id">
      <p>
      </p>
     </div>
    </body>
    <div id="id">
     <p>
     </p>
    </div>""")


def test_text_node_test_selects_disjoint_text_nodes():
    html_body = """<p>one<span>two</span>three</p>"""
    actual = query_html_doc(html_body, '/html/body/p/text()')
    assert actual == expected_result("""
    one
    three""")


def test_comment_node_test_selects_comments():
    html_body = """
    <!-- head comment -->
    <div>
        <!-- comment in div -->
    </div>"""
    assert query_html_doc(html_body, '//comment()') == expected_result("""
    <!-- head comment -->
    <!-- comment in div -->""")
