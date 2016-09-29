from test.common_test_util import expected_result
from test.hquery.hquery_test_util import query_html_doc


def test_simple_element_construction_with_string_content():
    assert query_html_doc('', 'element foo { "bar" }') == expected_result("""
    <foo>
     bar
    </foo>""")


def test_element_constructor_accepts_numbers_and_booleans():
    assert query_html_doc('', 'element test { 98.6 }') == expected_result("""
    <test>
     98.6
    </test>""")

    assert query_html_doc('', 'element test { false() }') == expected_result("""
    <test>
     false
    </test>""")


def test_construction_of_elements_containing_content_queried_from_original_document():
    html_body = """
    <div>
        <p>Hello, world!</p>
        <div>other div</div>
    </div>"""
    assert query_html_doc(html_body, 'element hello { //div }') == expected_result("""
    <hello>
     <div>
      <p>
       Hello, world!
      </p>
      <div>
       other div
      </div>
     </div>
     <div>
      other div
     </div>
    </hello>""")


def test_element_constructor_accepts_attributes_from_original_document_including_multi_values_like_classes():
    html_body = """
    <p class="one two" three="four">
        contents
    </p>"""

    assert query_html_doc(html_body, 'element test { //p/@* }') == expected_result("""
    <test class="one two" three="four">
    </test>""")

    assert query_html_doc(html_body, 'element test { //p/@three, //p }') == expected_result("""
    <test three="four">
     <p class="one two" three="four">
      contents
     </p>
    </test>""")


def test_element_constructor_can_be_nested():
    assert query_html_doc('', 'element moe {element larry {}, element curly {"Hey, Moe!"}}') == expected_result("""
    <moe>
     <larry>
     </larry>
     <curly>
      Hey, Moe!
     </curly>
    </moe>""")


def test_attribute_constructor_adds_attributes_to_an_element():
    html_body = '<p ng-bind="someModel"></p>'
    assert query_html_doc(html_body, 'element model { attribute name { //p[1]/@ng-bind } }') == expected_result("""
    <model name="someModel">
    </model>""")


def test_attribute_constructor_takes_string_value_of_tag_nodes_in_content_sequence_and_separates_with_spaces():
    html_body = '<p>Easy as</p>'
    assert query_html_doc(html_body, 'element foo {attribute bar {//p, 1 to 3}}') == expected_result("""
    <foo bar="Easy as 1 2 3">
    </foo>""")
