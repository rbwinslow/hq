"""
These tests verify results from the samples of unabbreviated location paths in the W3C XPath 1.0 specification (chapter
2, Location Paths).

https://www.w3.org/TR/xpath/#location-paths
"""

import os
import sys

from hq.soup_util import make_soup

sys.path.insert(0, os.path.abspath('../..'))

from ..common_test_util import expected_result
from test.hquery.hquery_test_util import query_html_doc, query_context_node


def test_selects_the_para_element_children_of_the_context_node():
    assert query_context_node("<context><para></para></context>", 'child::para') == expected_result("""
    <para>
    </para>""")


def test_selects_all_text_node_children_of_the_context_node():
    html = "<context>before<span>during</span>after</context>"
    assert query_context_node(html, 'child::text()') == expected_result("""
    before
    after""")


def test_selects_all_the_children_of_the_context_node_whatever_their_node_type():
    html = """
    <context>selected text<selected-element>
        </selected-element>
        <!-- selected comment -->
    </context>"""
    assert query_context_node(html, 'child::node()') == expected_result("""
    selected text
    <selected-element>
    </selected-element>
    <!-- selected comment -->""")


def test_selects_the_name_attribute_of_the_context_node():
    html = "<context name='selected'></context>"
    assert query_context_node(html, 'attribute::name') == expected_result('name="selected"')


def test_selects_all_the_attributes_of_the_context_node():
    html = "<context foo='bar' bar='foo'></context>"
    assert query_context_node(html, 'attribute::*') == expected_result('''
    bar="foo"
    foo="bar"''')


def test_selects_the_para_element_descendants_of_the_context_node():
    html = """
    <context>
        <para>
            <para/>
        </para>
    </context>"""
    assert query_context_node(html, 'descendant::para') == expected_result("""
    <para>
     <para>
     </para>
    </para>
    <para>
    </para>""")


def test_selects_all_div_ancestors_of_the_context_node():
    html = """
    <div>
        <notdiv/>
    </div>"""
    assert query_context_node(make_soup(html).div.notdiv, 'ancestor::div') == expected_result("""
    <div>
     <notdiv>
     </notdiv>
    </div>""")


def test_selects_the_div_ancestors_of_the_context_node_and_if_the_context_node_is_a_div_element_the_context_node_as_well():
    html = """
    <div>
        <div/>
        <notdiv/>
    </div>"""
    soup = make_soup(html)
    assert query_context_node(soup.div.div, 'ancestor-or-self::div') == expected_result("""
    <div>
     <div>
     </div>
     <notdiv>
     </notdiv>
    </div>
    <div>
    </div>""")
    assert query_context_node(soup.div.notdiv, 'ancestor-or-self::div') == expected_result("""
    <div>
     <div>
     </div>
     <notdiv>
     </notdiv>
    </div>""")


def test_selects_the_para_element_descendants_of_the_context_node_and_if_the_context_node_is_a_para_element_the_context_node_as_well():
    context_is_para = """
    <para>
        <para>foo</para>
        <para>bar</para>
    </para>"""
    context_is_not_para = """
    <notpara>
        <para>foo</para>
        <para>bar</para>
    </notpara>"""
    assert query_context_node(context_is_para, 'descendant-or-self::para') == expected_result("""
    <para>
     <para>
      foo
     </para>
     <para>
      bar
     </para>
    </para>
    <para>
     foo
    </para>
    <para>
     bar
    </para>""")
    assert query_context_node(context_is_not_para, 'descendant-or-self::para') == expected_result("""
    <para>
     foo
    </para>
    <para>
     bar
    </para>""")


def test_selects_the_context_node_if_it_is_a_para_element_and_otherwise_selects_nothing():
    is_para = "<para></para>"
    is_not_para = "<notpara></notpara>"
    assert query_context_node(is_para, 'self::para') == expected_result("""
    <para>
    </para>""")
    assert query_context_node(is_not_para, 'self::para') == ''


def test_selects_the_para_element_descendants_of_the_chapter_element_children_of_the_context_node():
    html = """
    <context>
        <verse>
            <para>not selected</para>
        </verse>
        <chapter>
            <div>
                <para>selected</para>
            </div>
        </chapter>
    </context>"""
    assert query_context_node(html, 'child::chapter/descendant::para') == expected_result("""
    <para>
     selected
    </para>""")


def test_selects_all_para_grandchildren_of_the_context_node():
    html = """
    <context>
        <para>not selected</para>
        <foo>
            <notpara>not selected</notpara>
            <para>selected</para>
        </foo>
        <bar>
            <para>also selected</para>
        </bar>
    </context>"""
    assert query_context_node(html, 'child::*/child::para') == expected_result("""
    <para>
     selected
    </para>
    <para>
     also selected
    </para>""")


def test_selects_the_document_root_which_is_always_the_parent_of_the_document_element():
    html = """
    <!-- comment -->
    <root-tag>
    </root-tag>"""
    assert query_context_node(html, '/') == expected_result(html)


def test_selects_all_the_para_elements_in_the_same_document_as_the_context_node():
    html = """
    <root>
        <notpara/>
        <para>selected</para>
    </root>"""
    soup = make_soup(html)
    assert query_context_node(soup.root.notpara, '/descendant::para') == expected_result("""
    <para>
     selected
    </para>""")


def test_selects_all_the_item_elements_that_have_an_olist_parent_and_that_are_in_the_same_document_as_the_context_node():
    html = """
    <root>
        <notolist/>
        <olist>
            <notitem>not selected</notitem>
            <item>selected</item>
        <olist>
    </root>"""
    soup = make_soup(html)
    assert query_context_node(soup.root.notolist, '/descendant::olist/child::item') == expected_result("""
    <item>
     selected
    </item>""")


def test_selects_the_first_para_child_of_the_context_node():
    html = """
    <context>
        <para>selected</para>
        <para>not selected</para>
    </context>"""
    assert query_context_node(html, 'child::para[position()=1]') == expected_result("""
    <para>
     selected
    </para>""")


def test_selects_the_last_para_child_of_the_context_node():
    html = """
    <context>
        <para>not selected</para>
        <para>selected</para>
    </context>"""
    assert query_context_node(html, 'child::para[position()=last()]') == expected_result("""
    <para>
     selected
    </para>""")


def test_selects_the_last_but_one_para_child_of_the_context_node():
    html = """
    <context>
        <para>not selected</para>
        <para>selected</para>
        <para>also not selected</para>
    </context>"""
    assert query_context_node(html, 'child::para[position()=last()-1]') == expected_result("""
    <para>
     selected
    </para>""")


def test_selects_all_the_para_children_of_the_context_node_other_than_the_first_para_child_of_the_context_node():
    html = """
    <context>
        <para>not selected</para>
        <para>selected</para>
        <para>also selected</para>
    </context>"""
    assert query_context_node(html, 'child::para[position()>1]') == expected_result("""
    <para>
     selected
    </para>
    <para>
     also selected
    </para>""")


def test_selects_the_next_chapter_sibling_of_the_context_node():
    html = """
    <root>
        <context/>
        <chapter>selected</chapter>
        <chapter>not selected</chapter>
    </root>"""
    soup = make_soup(html)
    assert query_context_node(soup.root.context, 'following-sibling::chapter[position()=1]') == expected_result("""
    <chapter>
     selected
    </chapter>""")


def test_selects_the_previous_chapter_sibling_of_the_context_node():
    html = """
    <root>
        <chapter>not selected</chapter>
        <chapter>selected</chapter>
        <context/>
    </root>"""
    soup = make_soup(html)
    assert query_context_node(soup.root.context, 'preceding-sibling::chapter[position()=1]') == expected_result("""
    <chapter>
     selected
    </chapter>""")


def test_selects_the_forty_second_figure_element_in_the_document():
    html_body = ''.join('<figure>{0}</figure>'.format(n) for n in range(1, 43))
    assert query_html_doc(html_body, '/descendant::figure[position()=42]') == expected_result("""
    <figure>
     42
    </figure>""")


def test_selects_the_second_section_of_the_fifth_chapter_of_the_doc_document_element():
    html_body = """
    <doc>
        <chapter>
            <section>chapter 1, section 1</section>
        </chapter>
        <chapter></chapter>
        <chapter></chapter>
        <chapter></chapter>
        <chapter>
            <section>chapter 5, section 1</section>
            <section>chapter 5, section 2</section>
        </chapter>
    </doc>"""
    actual = query_html_doc(html_body,
                            '/child::doc/child::chapter[position()=5]/child::section[position()=2]',
                            wrap_body=False)
    assert actual == expected_result("""
    <section>
     chapter 5, section 2
    </section>""")


def test_selects_all_para_children_of_the_context_node_that_have_a_type_attribute_with_value_warning():
    html = """
    <context>
        <para>no type</para>
        <para type="warning">warning one</para>
        <para type="error">error type</para>
        <para type="warning">warning two</para>
    </context>"""
    assert query_context_node(html, 'child::para[attribute::type="warning"]') == expected_result("""
    <para type="warning">
     warning one
    </para>
    <para type="warning">
     warning two
    </para>""")


def test_selects_the_fifth_para_child_of_the_context_node_that_has_a_type_attribute_with_value_warning():
    html = """
    <context>
        <para type="warning">warning one</para>
        <para type="error">error type</para>
        <para type="warning">warning two</para>
        <para type="warning">warning three</para>
        <para type="warning">warning four</para>
        <para type="warning">warning five</para>
    </context>"""
    assert query_context_node(html, "child::para[attribute::type='warning'][position()=5]") == expected_result("""
    <para type="warning">
     warning five
    </para>""")


def test_selects_the_fifth_para_child_of_the_context_node_if_that_child_has_a_type_attribute_with_value_warning():
    html_with = """
    <context>
        <para type="warning">para one</para>
        <para type="warning">para two</para>
        <para type="warning">para three</para>
        <para type="warning">para four</para>
        <para type="warning">para five</para>
    </context>"""
    html_without = """
    <context>
        <para type="warning">para one</para>
        <para type="warning">para two</para>
        <para type="warning">para three</para>
        <para type="warning">para four</para>
        <para type="error">para five</para>
    </context>"""

    actual_with = query_context_node(html_with, 'child::para[position()=5][attribute::type="warning"]')
    actual_without = query_context_node(html_without, 'child::para[position()=5][attribute::type="warning"]')

    assert actual_with == expected_result("""
    <para type="warning">
     para five
    </para>""")
    assert actual_without == expected_result('')


def test_selects_the_chapter_children_of_the_context_node_that_have_one_or_more_title_children_with_string_value_equal_to_Introduction():
    html = """
    <context>
        <chapter>No Title</chapter>
        <chapter>
            <title>Wrong Title</title>
        </chapter>
        <chapter>
            <title>Introduction</title>
        </chapter>
    </context>"""
    assert query_context_node(html, "child::chapter[child::title='Introduction']") == expected_result("""
    <chapter>
     <title>
      Introduction
     </title>
    </chapter>""")


def test_selects_the_chapter_children_of_the_context_node_that_have_one_or_more_title_children():
    html = """
    <context>
        <chapter>not selected</chapter>
        <chapter><title></title></chapter>
    </context>"""
    assert query_context_node(html, 'child::chapter[child::title]') == expected_result("""
    <chapter>
     <title>
     </title>
    </chapter>""")


def test_selects_the_chapter_and_appendix_children_of_the_context_node():
    html = """
    <context>
        <title>not selected</title>
        <chapter></chapter>
        <appendix></appendix>
    </context>"""
    assert query_context_node(html, 'child::*[self::chapter or self::appendix]') == expected_result("""
    <chapter>
    </chapter>
    <appendix>
    </appendix>""")


def test_selects_the_last_chapter_or_appendix_child_of_the_context_node():
    html_with_last_chapter = """
    <context>
        <chapter></chapter>
        <appendix></appendix>
        <chapter>selected</chapter>
    </context>"""
    html_with_last_appendix = """
    <context>
        <appendix></appendix>
        <chapter></chapter>
        <appendix>selected</appendix>
    </context>"""
    actual_last_chapter = query_context_node(html_with_last_chapter,
                                             'child::*[self::chapter or self::appendix][position()=last()]')
    actual_last_appendix = query_context_node(html_with_last_appendix,
                                              'child::*[self::chapter or self::appendix][position()=last()]')
    assert actual_last_chapter == expected_result("""
    <chapter>
     selected
    </chapter>""")
    assert actual_last_appendix == expected_result("""
    <appendix>
     selected
    </appendix>""")
