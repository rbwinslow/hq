"""
These tests verify results from the samples of unabbreviated location paths in the W3C XPath 1.0 specification (chapter
2, Location Paths).

https://www.w3.org/TR/xpath/#location-paths
"""

import os
import sys

sys.path.insert(0, os.path.abspath('../..'))

from ..test_util import expected_result, query_context_node



def test_selects_the_para_element_children_of_the_context_node():
    assert query_context_node("<context><para></para></context>", 'child::para') == expected_result("""
    <para>
    </para>""")


def test_selects_all_text_node_children_of_the_context_node():
    html = "<context>before<span>during</span>after</context>"
    assert query_context_node(html, 'child::text()') == expected_result("""
    before
    after""")


# def test_selects_all_the_children_of_the_context_node_whatever_their_node_type():
#     html = """
#     <context>selected text<selected-element>
#         </selected-element>
#         <!-- selected comment -->
#     </context>"""
#     assert query_context_node(html, 'child::node()') == expected_result("""
#     <selected-element>
#     </selected-element>
#     <!-- selected comment -->""")


# def test_selects_the_name_attribute_of_the_context_node():
#     html = ""
#     assert query_context_node(html, 'attribute::name') == expected_result("""
#     """)
#
#
# def test_selects_all_the_attributes_of_the_context_node():
#     html = ""
#     assert query_context_node(html, 'attribute::*') == expected_result("""
#     """)
#
#
# def test_selects_the_para_element_descendants_of_the_context_node():
#     html = ""
#     assert query_context_node(html, 'descendant::para') == expected_result("""
#     """)
#
#
# def test_selects_all_div_ancestors_of_the_context_node():
#     html = ""
#     assert query_context_node(html, 'ancestor::div') == expected_result("""
#     """)
#
#
# def test_selects_the_div_ancestors_of_the_context_node_and_if_the_context_node_is_a_div_element_the_context_node_as_well():
#     html = ""
#     assert query_context_node(html, 'ancestor-or-self::div') == expected_result("""
#     """)
#
#
# def test_selects_the_para_element_descendants_of_the_context_node_and_if_the_context_node_is_a_para_element_the_context_node_as_well():
#     html = ""
#     assert query_context_node(html, 'descendant-or-self::para') == expected_result("""
#     """)
#
#
# def test_selects_the_context_node_if_it_is_a_para_element_and_otherwise_selects_nothing():
#     html = ""
#     assert query_context_node(html, 'self::para') == expected_result("""
#     """)
#
#
# def test_selects_the_para_element_descendants_of_the_chapter_element_children_of_the_context node():
#     html = ""
#     assert query_context_node(html, 'child::chapter/descendant::para') == expected_result("""
#     """)
#
#
# def test_selects_all_para_grandchildren_of_the_context_node():
#     html = ""
#     assert query_context_node(html, 'child::*/child::para') == expected_result("""
#     """)
#
#
# def test_selects_the_document_root_which_is_always_the_parent_of_the_document_element():
#     html = ""
#     assert query_context_node(html, '/') == expected_result("""
#     """)
#
#
# def test_selects_all_the_para_elements_in_the_same_document_as_the_context_node():
#     html = ""
#     assert query_context_node(html, '/descendant::para') == expected_result("""
#     """)
#
#
# def test_selects_all_the_item_elements_that_have_an_olist_parent_and_that_are_in_the_same_document_as_the_context_node():
#     html = ""
#     assert query_context_node(html, '/descendant::olist/child::item') == expected_result("""
#     """)
#
#
# def test_selects_the_first_para_child_of_the_context_node():
#     html = ""
#     assert query_context_node(html, 'child::para[position()=1]') == expected_result("""
#     """)
#
#
# def test_selects_the_last_para_child_of_the_context_node():
#     html = ""
#     assert query_context_node(html, 'child::para[position()=last()]') == expected_result("""
#     """)
#
#
# def test_selects_the_last_but_one_para_child_of_the_context_node():
#     html = ""
#     assert query_context_node(html, 'child::para[position()=last()-1]') == expected_result("""
#     """)
#
#
# def test_selects_all_the_para_children_of_the_context_node_other_than_the_first_para_child_of_the_context_node():
#     html = ""
#     assert query_context_node(html, 'child::para[position()>1]') == expected_result("""
#     """)
#
#
# def test_selects_the_next_chapter_sibling_of_the_context_node():
#     html = ""
#     assert query_context_node(html, 'following-sibling::chapter[position()=1]') == expected_result("""
#     """)
#
#
# def test_selects_the_previous_chapter_sibling_of_the_context_node():
#     html = ""
#     assert query_context_node(html, 'preceding-sibling::chapter[position()=1]') == expected_result("""
#     """)
#
#
# def test_selects_the_forty_second_figure_element_in_the_document():
#     html = ""
#     assert query_context_node(html, '/descendant::figure[position()=42]') == expected_result("""
#     """)
#
#
# def test_selects_the_second_section_of_the_fifth_chapter_of_the_doc_document_element():
#     html = ""
#     assert query_context_node(html, '/child::doc/child::chapter[position()=5]/child::section[position()=2]') == expected_result("""
#     """)
#
#
# def test_selects_all_para_children_of_the_context_node_that_have_a_type_attribute_with_value_warning():
#     html = ""
#     assert query_context_node(html, 'child::para[attribute::type="warning"]') == expected_result("""
#     """)
#
#
# def test_selects_the_fifth_para_child_of_the_context_node_that_has_a_type_attribute_with_value_warning():
#     html = ""
#     assert query_context_node(html, "child::para[attribute::type='warning'][position()=5]") == expected_result("""
#     """)
#
#
# def test_selects_the_fifth_para_child_of_the_context_node_if_that_child_has_a_type_attribute_with_value_warning():
#     html = ""
#     assert query_context_node(html, 'child::para[position()=5][attribute::type="warning"]') == expected_result("""
#     """)
#
#
# def test_selects_the_chapter_children_of_the_context_node_that_have_one_or_more_title_children_with_string_value_equal_to_Introduction():
#     html = ""
#     assert query_context_node(html, 'child::chapter[child::title='Introduction']') == expected_result("""
#     """)
#
#
# def test_selects_the_chapter_children_of_the_context_node_that_have_one_or_more_title_children():
#     html = ""
#     assert query_context_node(html, 'child::chapter[child::title]') == expected_result("""
#     """)
#
#
# def selects_the_chapter_and_appendix_children_of_the_context_node()
#     html = ""
#     assert query_context_node(html, 'child::*[self::chapter or self::appendix]') == expected_result("""
#     """)
#
#
# def selects_the_last_chapter_or_appendix_child_of_the_context_node():
#     html = ""
#     assert query_context_node(html, 'child::*[self::chapter or self::appendix][position()=last()]') == expected_result("""
#     """)
