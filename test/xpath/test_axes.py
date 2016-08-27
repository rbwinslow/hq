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


def test_parent_axis_returns_parents_for_multiple_matching_nodes():
    html_body = """
    <div id="first">
     <p>
     </p>
    </div>
    <div id="second">
     <p>
     </p>
    </div>"""
    assert process_xpath_query(html_body, '//p/parent::*') == expected_result(html_body)


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


def test_following_sibling_axis_selects_all_following_siblings_and_only_following_siblings_that_match_name_test():
    html_body = """
    <section>
        <div></div>
        <h1></h1>
        <p>moe</p>
    </section>
    <section>
        <p>larry<p>
        <div></div>
        <p>curly</p>
    </section>"""
    assert process_xpath_query(html_body, '//div/following-sibling::p') == expected_result("""
    <p>
     moe
    </p>
    <p>
     curly
    </p>""")


def test_following_sibling_axis_works_with_node_test():
    html_body = """
    <div>
     foo
     <p></p>
     bar
    </div>"""
    assert process_xpath_query(html_body, '//p/following-sibling::text()') == expected_result('bar')
    assert process_xpath_query('<h1></h1><div></div><p>foo</p>', '//div/following-sibling::*') == expected_result("""
    <p>
     foo
    </p>""")


def test_preceding_sibling_axis_works_with_name_test():
    html_body = """
    <p>foo</p>
    <div></div>
    <p>bar</p>"""
    assert process_xpath_query(html_body, '//div/preceding-sibling::p') == expected_result("""
    <p>
     foo
    </p>""")


def test_preceding_sibling_axis_works_with_node_test():
    html_body = """
    <p>foo</p>
    <div></div>
    <p>bar</p>"""
    assert process_xpath_query(html_body, '//div/preceding-sibling::node()') == expected_result("""
    <p>
     foo
    </p>""")
