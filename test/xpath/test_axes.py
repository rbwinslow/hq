import os
import sys

sys.path.insert(0, os.path.abspath('../..'))

from ..test_util import expected_result, process_xpath_query


def test_explicit_child_axis():
    html_body = """
    <div>
        <p>foo</p>
    </div>"""
    assert process_xpath_query(html_body, '//div/child::p') == expected_result("""
    <p>
     foo
    </p>""")


def test_descendant_axis_returns_all_descendants_and_only_descendants_of_nodes_matching_node_test():
    html_body = """
    <div>
        <div>foo</div>
    </div>
    <!-- comment -->
    <div>bar</div>
    <p>not selected</p>"""
    assert process_xpath_query(html_body, '/html/body/descendant::div') == expected_result("""
    <div>
     <div>
      foo
     </div>
    </div>
    <div>
     foo
    </div>
    <div>
     bar
    </div>""")


def test_parent_axis_returns_parent_of_tag_node():
    assert process_xpath_query('<div></div>', '//div/parent::*') == expected_result("""
    <body>
     <div>
     </div>
    </body>""")


def test_parent_axis_produces_nothing_for_root_element():
    assert process_xpath_query('', '/html/parent::*') == expected_result('')
    assert process_xpath_query('<div></div>', 'div/parent::*', wrap_body=False) == expected_result('')


def test_ancestor_axis_produces_all_ancestors_and_only_ancestors():
    html_body = """
    <html>
        <body>
            <!-- comment -->
            <h1></h1>
            <div></div>
        </body>
    </html>"""
    assert process_xpath_query(html_body, '//div/ancestor::*', wrap_body=False) == expected_result("""
    <body>
     <!-- comment -->
     <h1>
     </h1>
     <div>
     </div>
    </body>
    <html>
     <body>
      <!-- comment -->
      <h1>
      </h1>
      <div>
      </div>
     </body>
    </html>""")
