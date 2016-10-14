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


def test_hash_constructor_can_contain_a_sequence_assembled_from_node_sets():
    html_body = """
    <p>foo</p>
    <div>bar</div>"""

    actual = json.loads(query_html_doc(html_body, 'hash { /html/body/p, /html/body/div }'))

    assert 'p' in actual
    assert 'div' in actual
    assert actual['p'] == 'foo'
    assert actual['div'] == 'bar'


def test_hash_keys_can_be_used_to_define_attributes_in_a_constructed_hash():
    actual = json.loads(query_html_doc('', 'hash {foo: "bar", moe: "larry"}'))

    assert 'foo' in actual
    assert actual['foo'] == 'bar'
    assert 'moe' in actual
    assert actual['moe'] == 'larry'


def test_hash_keys_can_be_mixed_with_other_types_of_content_in_a_constructed_hash():
    html_body = """
    <moe>Wake up and go back to sleep!</moe>
    <curly>I'm trying to think, but nothing happens!</curly>"""

    actual = json.loads(query_html_doc(html_body, 'hash {//moe, larry: "The pain goes away on payday.", //curly}'))

    assert 'moe' in actual
    assert 'larry' in actual
    assert 'curly' in actual
    assert actual['moe'] == 'Wake up and go back to sleep!'
    assert actual['larry'] == 'The pain goes away on payday.'
    assert actual['curly'] == "I'm trying to think, but nothing happens!"


def test_non_string_types_survive_conversion_to_json():
    actual = json.loads(query_html_doc('', 'hash { integer: 1, float: 1.1, boolean: true() }'))

    assert all(name in actual for name in ('integer', 'float', 'boolean'))
    assert isinstance(actual['integer'], int)
    assert isinstance(actual['float'], float)
    assert isinstance(actual['boolean'], bool)


def test_hash_can_contain_key_values_that_are_other_computed_json_objects():
    actual = json.loads(query_html_doc('', 'hash {a_hash: hash {foo: "bar"}, an_array: array {"one", 2}}'))

    assert 'a_hash' in actual
    assert 'an_array' in actual
    assert isinstance(actual['a_hash'], dict)
    assert isinstance(actual['an_array'], list)
    assert 'foo' in actual['a_hash']
    assert actual['a_hash']['foo'] == 'bar'
    assert len(actual['an_array']) == 2
    assert actual['an_array'][0] == 'one'
    assert actual['an_array'][1] == 2


def test_element_value_in_hash_key_is_transformed_into_string_value_by_default():
    html_body = '<p>you are <a href>here</a></p>'

    actual = json.loads(query_html_doc(html_body, 'hash { placement: //p }')) == 'You are here'


def test_array_constructor_uses_string_value_of_elements_when_given_node_sets_as_contents():
    html_body = """
    <p>one</p>
    <div>two</div>
    <p>three</p>"""

    actual = json.loads(query_html_doc(html_body, 'array { //p, //div }'))

    assert len(actual) == 3
    assert actual[0] == 'one'
    assert actual[1] == 'three'
    assert actual[2] == 'two'


def test_array_constructor_properly_handles_hash_constructors_as_contents():
    actual = json.loads(query_html_doc('', 'array { (0 to 2) -> hash {value: $_} }'))

    assert len(actual) == 3
    assert all('value' in hash for hash in actual)
    assert all(actual[i]['value'] == i for i in range(0, 3))


def test_text_content_normalization_is_applied_to_attribute_values_in_hash_constructor():
    preserved = u'\u00a0non\u00a0breaking\u00a0spaces '
    html_body = u'<p>{0}</p>'.format(preserved)

    actual = json.loads(query_html_doc(html_body, 'hash {para: //p/text()}'))
    assert actual['para'] == 'non breaking spaces'

    actual = json.loads(query_html_doc(html_body, 'hash {para: //p/text()}', preserve_space=True))
    assert actual['para'] == preserved
