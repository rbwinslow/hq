import json

from test.hquery.hquery_test_util import query_html_doc


def test_hash_constructor_turns_tags_into_tag_name_keys_with_tag_content_values():
    html_body = """
    <p>foo</p>
    <div>bar</div>"""
    actual = json.loads(query_html_doc(html_body, 'hash { /html/body/* }'))
    assert actual['p'] == 'foo'
    assert actual['div'] == 'bar'


def test_hash_constructor_turns_text_into_attribute_named_text():
    html_body = '<p>Hello, world!</p>'
    expected = '{"text": "Hello, world!"}'
    assert query_html_doc(html_body, 'hash { //p/text() }') == expected
    assert query_html_doc('', 'hash { "Hello, world!" }') == expected


def test_hash_constructor_joins_discontinuous_text_from_content_sequence_with_spaces_in_between():
    html_body = '<p>vidi</p>'
    assert query_html_doc(html_body, 'hash { "veni", //p/text(), "vici" }') == '{"text": "veni vidi vici"}'


def test_hash_constructor_coalesces_like_elements_into_an_array_by_default():
    html_body = """
    <p>one</p>
    <div>two</div>
    <p>three</p>"""

    actual = json.loads(query_html_doc(html_body, 'hash { /html/body/* }'))
    assert isinstance(actual['p'], list)
    assert len(actual['p']) == 2
    assert actual['p'][1] == 'three'
    assert actual['div'] == 'two'


def test_hash_constructor_array_filter_causes_matching_elements_to_be_put_in_an_array():
    html_body = """
    <h1>zero</h1>
    <p>one</p>"""
    actual = json.loads(query_html_doc(html_body, 'hash {a:h1:} { /html/body/* }'))

    assert actual['p'] == 'one'
    assert isinstance(actual['h1'], list)
    assert len(actual['h1']) == 1
    assert actual['h1'][0] == 'zero'


def test_hash_constructor_number_filter_causes_contents_of_matching_elements_to_be_interpreted_as_numbers():
    html_body = """
    <p>20</p>
    <div>20</div>
    <h1>20.20</h1>"""

    actual = json.loads(query_html_doc(html_body, 'hash {n:div,h1:} { /html/body/* }'))

    assert actual['p'] == '20'
    assert actual['div'] == 20
    assert actual['h1'] == 20.2


def test_hash_constructor_filters_can_be_combined():
    html_body = """
    <p>20</p>
    <div>20</div>
    <h1>20.20</h1>"""

    actual = json.loads(query_html_doc(html_body, 'hash {a:p,h1:n:div,h1:} { /html/body/* }'))
    assert isinstance(actual['p'], list)
    assert isinstance(actual['h1'], list)
    assert actual['p'][0] == '20'
    assert actual['div'] == 20
    assert actual['h1'][0] == 20.2

    actual = json.loads(query_html_doc(html_body, 'hash {n:div,h1:a:p,h1:} { /html/body/* }'))
    assert isinstance(actual['p'], list)
    assert isinstance(actual['h1'], list)
    assert actual['p'][0] == '20'
    assert actual['div'] == 20
    assert actual['h1'][0] == 20.2


def test_hash_constructor_mapping_filter_renames_attributes_derived_from_element_content():
    html_body = """
    <p>foo</p>
    <div>bar</div>"""

    actual = json.loads(query_html_doc(html_body, 'hash {m:p>paragraph,div>other:} { /html/body/* }'))

    assert 'paragraph' in actual
    assert 'other' in actual
    assert 'p' not in actual
    assert 'div' not in actual
    assert actual['paragraph'] == 'foo'
    assert actual['other'] == 'bar'
