from hq.soup_util import make_soup
from test.common_test_util import expected_result
from test.hquery.hquery_test_util import query_context_node


def test_selects_the_para_element_children_of_the_context_node():
    html = """
    <context>
        <para>selected</para>
        <not-para>not selected</not-para>
        <para>also selected</para>
    </context>"""
    assert query_context_node(html, 'para') == expected_result("""
    <para>
     selected
    </para>
    <para>
     also selected
    </para>""")


def test_selects_all_element_children_of_the_context_node():
    html = """
    <context>
        <!-- comment -->
        <element>selected</element>
        non-selected text
        <para>also selected</para>
    </context>"""
    assert query_context_node(html, '*') == expected_result("""
    <element>
     selected
    </element>
    <para>
     also selected
    </para>""")


def test_selects_all_text_node_children_of_the_context_node():
    html = """
    <context>
        first
        <element>second</element>
        third
    </context>"""
    actual = query_context_node(html, 'text()')
    assert 'first' in actual
    assert 'second' not in actual
    assert 'third' in actual


def test_selects_the_name_attribute_of_the_context_node():
    html = '<context name="value">not value</context>'
    assert query_context_node(html, '@name') == expected_result('name="value"')


def test_selects_all_the_attributes_of_the_context_node():
    html = '<context first="first value" second="second value" third="third value"></context>'
    assert query_context_node(html, '@*') == expected_result('''
    first="first value"
    second="second value"
    third="third value"''')


def test_selects_the_first_para_child_of_the_context_node():
    html = """
    <context>
        <para>selected</para>
        <para>not selected</para>
    </context>"""
    assert query_context_node(html, 'para[1]') == expected_result("""
    <para>
     selected
    </para>""")


def test_selects_the_last_para_child_of_the_context_node():
    html = """
    <context>
        <para>not selected</para>
        <para>also not selected</para>
        <para>selected</para>
    </context>"""
    assert query_context_node(html, 'para[last()]') == expected_result("""
    <para>
     selected
    </para>""")


def test_selects_all_para_grandchildren_of_the_context_node():
    html = """
    <context>
        <para>
            not selected
            <para>selected</para>
            <para>also selected</para>
        </para>
    </context>"""
    assert query_context_node(html, '*/para') == expected_result("""
    <para>
     selected
    </para>
    <para>
     also selected
    </para>""")


def test_selects_the_second_section_of_the_fifth_chapter_of_the_doc():
    html = """
    <doc>
        <chapter>one</chapter>
        <chapter>two</chapter>
        <chapter>three</chapter>
        <chapter>four</chapter>
        <chapter>
            <section>five point one</section>
            <section>five point two</section>
        </chapter>
    </doc>"""
    assert query_context_node(html, '/doc/chapter[5]/section[2]') == expected_result("""
    <section>
     five point two
    </section>""")


def test_selects_the_para_element_descendants_of_the_chapter_element_children_of_the_context_node():
    html = """
    <context>
        <para>not selected</para>
        <chapter>
            <para>
                <para>selected</para>
            </para>
        </chapter>
    </context>"""
    assert query_context_node(html, 'chapter//para') == expected_result("""
    <para>
     <para>
      selected
     </para>
    </para>
    <para>
     selected
    </para>""")


def test_selects_all_the_para_descendants_of_the_document_root_and_thus_selects_all_para_elements_in_the_same_document_as_the_context_node():
    html = """
    <root>
        <para>
            <para>selected</para>
        </para>
        <context></context>
        <para>also selected</para>
    </root>"""
    soup = make_soup(html)
    assert query_context_node(soup.root.context, '//para') == expected_result("""
    <para>
     <para>
      selected
     </para>
    </para>
    <para>
     selected
    </para>
    <para>
     also selected
    </para>""")


def test_selects_all_the_item_elements_in_the_same_document_as_the_context_node_that_have_an_olist_parent():
    html = """
    <root>
        <olist>no items</olist>
        <item>not selected</item>
        <context></context>
        <olist>
            <item>first</item>
        </olist>
        <item>
            <olist>
                <item>second</item>
            <olist>
        </item>
    </root>"""
    soup = make_soup(html)
    assert query_context_node(soup.root.context, '//olist/item') == expected_result("""
    <item>
     first
    </item>
    <item>
     second
    </item>""")


def test_selects_the_context_node():
    html = """
    <context>
        selected
    </context>"""
    assert query_context_node(html, '.') == expected_result("""
    <context>
     selected
    </context>""")


def test_selects_the_para_element_descendants_of_the_context_node():
    html = """
    <para>
        <context>
            <para>selected</para>
            <not-para>not selected</not-para>
            <para>
                <para>also selected</para>
            </para>
        </context>
    </para>"""
    soup = make_soup(html)
    assert query_context_node(soup.para.context, './/para') == expected_result("""
    <para>
     selected
    </para>
    <para>
     <para>
      also selected
     </para>
    </para>
    <para>
     also selected
    </para>""")


def test_selects_the_parent_of_the_context_node():
    html = """
    <root>
        <context></context>
    </root>"""
    soup = make_soup(html)
    assert query_context_node(html, '..') == expected_result("""
    <root>
     <context>
     </context>
    </root>""")


def test_selects_the_lang_attribute_of_the_parent_of_the_context_node():
    html = """
    <root lang="English">
        <context></context>
    </root>"""
    soup = make_soup(html)
    assert query_context_node(soup.root.context, '../@lang') == expected_result('lang="English"')


def test_selects_all_para_children_of_the_context_node_that_have_a_type_attribute_with_value_warning():
    html = """
    <context>
        <para>not selected</para>
        <para type="warning">selected</para>
        <para type="error">not selected</para>
        <para type="warning">also selected</para>
    </context>"""
    assert query_context_node(html, 'para[@type="warning"]') == expected_result("""
    <para type="warning">
     selected
    </para>
    <para type="warning">
     also selected
    </para>""")


def test_selects_the_fifth_para_child_of_the_context_node_that_has_a_type_attribute_with_value_warning():
    html = """
    <context>
        <para type="error">first error</para>
        <para type="warning">first warning</para>
        <para type="error">second error</para>
        <para type="warning">second warning</para>
        <para type="error">third error</para>
        <para type="warning">third warning</para>
        <para type="error">fourth error</para>
        <para type="warning">fourth warning</para>
        <para type="error">fifth error</para>
        <para type="warning">fifth warning</para>
    </context>"""
    assert query_context_node(html, 'para[@type="warning"][5]') == expected_result("""
    <para type="warning">
     fifth warning
    </para>""")


def test_selects_the_fifth_para_child_of_the_context_node_if_that_child_has_a_type_attribute_with_value_warning():
    html = """
    <context>
        <para>not selected</para>
        <para>not selected</para>
        <para>not selected</para>
        <para>not selected</para>
        <para type="error">selected</para>
    </context>"""
    assert query_context_node(html, 'para[5][@type="warning"]') == expected_result("")
    assert query_context_node(html.replace('error', 'warning'), 'para[5][@type="warning"]') == expected_result("""
    <para type="warning">
     selected
    </para>""")


def test_selects_the_chapter_children_of_the_context_node_that_have_one_or_more_title_children_with_string_value_equal_to_Introduction():
    html = """
    <context>
        <chapter>
            <title>Introduction</title>
        </chapter>
        <chapter>not selected</chapter>
        <chapter>
            <title>Author's Note</title>
        </chapter>
        <chapter>
            <title>Introduction</title>
            <content>Hello, I'm chapter.</content>
        </chapter>
    </context>"""
    assert query_context_node(html, 'chapter[title="Introduction"]') == expected_result("""
    <chapter>
     <title>
      Introduction
     </title>
    </chapter>
    <chapter>
     <title>
      Introduction
     </title>
     <content>
      Hello, I'm chapter.
     </content>
    </chapter>""")


def test_selects_the_chapter_children_of_the_context_node_that_have_one_or_more_title_children():
    html = """
    <context>
        <chapter>
            <title>selected</title>
        </chapter>
        <chapter>
            <not-title></not-title>
        </chapter>
        <chapter>
            <title>also selected</title>
        </chapter>
    </context>"""
    assert query_context_node(html, 'chapter[title]') == expected_result("""
    <chapter>
     <title>
      selected
     </title>
    </chapter>
    <chapter>
     <title>
      also selected
     </title>
    </chapter>""")


def test_selects_all_the_employee_children_of_the_context_node_that_have_both_a_secretary_attribute_and_an_assistant_attribute():
    html = """
    <context>
        <employee secretary="not selected"></employee>
        <employee assistant="" secretary="">selected</employee>
        <employee assistant="not selected"></employee>
        <employee secretary="also" assistant="selected"></employee>
    </context>"""
    assert query_context_node(html, 'employee[@secretary and @assistant]') == expected_result("""
    <employee assistant="" secretary="">
     selected
    </employee>
    <employee assistant="selected" secretary="also">
    </employee>""")
