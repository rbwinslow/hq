import os
import re
import sys

sys.path.insert(0, os.path.abspath('../..'))

from ..test_util import expected_result, query_html_doc


def test_explicit_child_axis():
    html_body = """
    <div>
        <p>foo</p>
    </div>"""
    assert query_html_doc(html_body, '//div/child::p') == expected_result("""
    <p>
     foo
    </p>""")


def test_descendant_axis_returns_all_descendants_and_only_descendants_of_nodes_matching_node_test():
    html_body = """
    <div>
        <div>
            <div>selected</div>
        </div>
    </div>
    <!-- comment -->
    <div>not selected</div>
    <p>not selected</p>"""
    assert query_html_doc(html_body, '/html/body/div/descendant::div') == expected_result("""
    <div>
     <div>
      selected
     </div>
    </div>
    <div>
     selected
    </div>""")


def test_descendant_or_self_axis_returns_all_descendants_and_context_node_if_it_matches_node_test():
    html_body = """
    <div>
        <div>foo</div>
    </div>
    <div>bar</div>"""
    assert query_html_doc(html_body, '/html/body/descendant-or-self::div') == expected_result("""
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


def test_descendant_or_self_axis_does_not_produce_self_if_node_test_does_not_match():
    html_body = """
    <div>
        <p>foo</p>
    </div>"""
    assert query_html_doc(html_body, '//div/descendant-or-self::p') == expected_result("""
    <p>
     foo
    </p>""")


def test_parent_axis_returns_parent_of_tag_node():
    assert query_html_doc('<div></div>', '//div/parent::*') == expected_result("""
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
    assert query_html_doc(html_body, '//p/parent::*') == expected_result(html_body)


def test_parent_axis_produces_nothing_for_root_element():
    assert query_html_doc('', '/html/parent::*') == expected_result('')
    assert query_html_doc('<div></div>', 'div/parent::*', wrap_body=False) == expected_result('')


def test_ancestor_axis_produces_all_ancestors_and_only_ancestors():
    html_body = """
    <html>
        <body>
            <!-- comment -->
            <h1></h1>
            <div></div>
        </body>
    </html>"""
    assert query_html_doc(html_body, '//div/ancestor::*', wrap_body=False) == expected_result("""
    <html>
     <body>
      <!-- comment -->
      <h1>
      </h1>
      <div>
      </div>
     </body>
    </html>
    <body>
     <!-- comment -->
     <h1>
     </h1>
     <div>
     </div>
    </body>""")


def test_ancestor_or_self_axis_produces_ancestors_and_self_when_node_test_is_a_match():
    html_body = """
    <div>
        <div>foo</div>
    </div>"""
    assert query_html_doc(html_body, '/html/body/div/div/ancestor-or-self::div') == expected_result("""
    <div>
     <div>
      foo
     </div>
    </div>
    <div>
     foo
    </div>""")


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
    assert query_html_doc(html_body, '//div/following-sibling::p') == expected_result("""
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
    assert query_html_doc(html_body, '//p/following-sibling::text()') == expected_result('bar')
    assert query_html_doc('<h1></h1><div></div><p>foo</p>', '//div/following-sibling::*') == expected_result("""
    <p>
     foo
    </p>""")


def test_preceding_sibling_axis_works_with_name_test():
    html_body = """
    <p>foo</p>
    <div></div>
    <p>bar</p>"""
    assert query_html_doc(html_body, '//div/preceding-sibling::p') == expected_result("""
    <p>
     foo
    </p>""")


def test_preceding_sibling_axis_works_with_node_test():
    html_body = """
    <p>foo</p>
    <div></div>
    <p>bar</p>"""
    assert query_html_doc(html_body, '//div/preceding-sibling::node()') == expected_result("""
    <p>
     foo
    </p>""")


def test_preceding_sibling_axis_returns_nodes_in_document_order():
    "Node sets are unordered, but people really seem to like these being in document order."
    html_body = """
    <p>foo</p>
    <p>bar</p>
    <div></div>"""
    assert query_html_doc(html_body, '//div/preceding-sibling::p') == expected_result("""
    <p>
     foo
    </p>
    <p>
     bar
    </p>""")


def test_following_axis_finds_all_following_nodes_that_match():
    html_body = """
    <section>
        <p>moe</p>
        <aside>
            <p>larry</p>
        </aside>
        <div>
            <p>curly</p>
        </div>
    </section>
    <p>shemp</p>"""
    assert query_html_doc(html_body, '//aside/following::p') == expected_result("""
    <p>
     curly
    </p>
    <p>
     shemp
    </p>""")


def test_preceding_axis_finds_all_preceding_nodes_that_match_node_test():
    html_body = """
    foo
    <div>
        <p>bar</p>
    </div>
    <span></span>"""
    actual = query_html_doc(html_body, '//span/preceding::text()')
    actual = re.sub(r'\W+', ' ', actual)
    assert actual == 'foo bar'


def test_preceding_axis_finds_all_preceding_nodes_that_match():
    html_body = """
    <p>moe</p>
    <section>
        <div>
            <p>larry</p>
        </div>
        <aside>
            <p>curly</p>
        </aside>
        <p>shemp</p>
    </section>"""
    assert query_html_doc(html_body, '//aside/preceding::p') == expected_result("""
    <p>
     moe
    </p>
    <p>
     larry
    </p>""")


def test_preceding_axis_produces_results_in_document_order_and_also_works_with_node_test():
    html_body = """
    <p>moe</p>
    <section>
        <div>
            <div>
                <p>larry</p>
            </div>
        </div>
        <aside>
            <p>curly</p>
        </aside>
        <p>shemp</p>
    </section>
    <script></script>"""
    assert query_html_doc(html_body, '//script/preceding::p/text()') == expected_result("""
    moe
    larry
    curly
    shemp""")


def test_attribute_axis_in_full_and_abbreviated_form_selects_named_attributes_or_all_attributes():
    html_body = """
    <div id="one"></div>
    <div id="two" class="three"></div>"""
    expected_ids_result = expected_result('''
    id="one"
    id="two"''')
    expected_all_result = expected_result('''
    id="one"
    class="three"
    id="two"''')
    assert query_html_doc(html_body, '//div/attribute::id') == expected_ids_result
    assert query_html_doc(html_body, '//div/@id') == expected_ids_result
    assert query_html_doc(html_body, '//attribute::*') == expected_all_result
    assert query_html_doc(html_body, '//@*') == expected_all_result


def test_attribute_axis_matching_any_attribute_produces_attributes_from_each_element_in_alphabetical_order():
    html_body = """
    <span moe="3" LARRY="2" curly="1"></span>
    <span BBB="5" aaa="4" ccc="6"></span>"""
    actual = query_html_doc(html_body, '//span/@*')
    assert re.sub(r'\w+="(\d)"\n?', r'\1', actual) == '123456'


def test_self_axis_applies_only_to_self():
    html_body = """
    <div id="not selected">
        <div id="selected">
            <div></div>
        </div>
    </div>"""
    assert query_html_doc(html_body, '/html/body/div/div/self::div') == expected_result("""
    <div id="selected">
     <div>
     </div>
    </div>""")
