from test.common_test_util import expected_result
from test.hquery.hquery_test_util import query_html_doc


def test_location_path_works_as_interpolated_string_expression():
    assert query_html_doc("<div>world</div>", '`Hello, ${//div/text()}!`') == expected_result('Hello, world!')


def test_element_node_becomes_normalized_text_contents_in_interpolated_string():
    html_body = """
    <p>
        foo   bar
    </p>"""
    assert query_html_doc(html_body, '`-->${//p}<--`') == expected_result('-->foo bar<--')


def test_text_between_embedded_expressions_gets_picked_up():
    html_body = """
    <p>one</p>
    <p>two</p>
    <p>three</p>"""
    assert query_html_doc(html_body, 'let $_ := 2 return `${//p[1]}, $_, ${//p[3]}`') == 'one, 2, three'


def test_join_filter_joins_string_values_from_node_set():
    html_body = """
    <p>one</p>
    <p>two</p>
    <p>three</p>"""
    assert query_html_doc(html_body, '`${j:,://p}`') == expected_result('one,two,three')


def test_join_filter_defaults_to_empty_string_delimiter():
    html_body = """
    <p>one</p>
    <p>two</p>"""
    assert query_html_doc(html_body, '`${j:://p}`') == expected_result('onetwo')


def test_truncate_filter_elides_contents():
    html_body = '<p>The quick brown fox jumped over the lazy dog.</p>'
    assert query_html_doc(html_body, '`${tru:23:?://p}`') == expected_result('The quick brown fox?')


def test_truncate_filter_defaults_to_no_suffix():
    html_body = '<p>short, sharp shock</p>'
    assert query_html_doc(html_body, '`${tru:15:://p}`') == expected_result('short, sharp')


def test_regex_replace_filter_replaces_stuff_with_other_stuff():
    html_body = '<span>May 25, 1979<span>'
    assert query_html_doc(html_body, r'`${rr:(\w+) (\d+)(, \d+):\2th of \1\3:://span}`') == '25th of May, 1979'


def test_use_of_escapes_for_forbidden_characters_in_regex_replace_patterns():
    assert query_html_doc('', r"""`it's ${rr:\w{3&#125;:dog::"a cat's"} life`""") == "it's a dog's life"
    assert query_html_doc('', r'`${rr:&#58; ::: let $x := "re: " return concat($x, "search")}`') == 'research'


def test_regex_replace_filter_can_be_used_to_replace_unicode_characters():
    assert query_html_doc('', u'`${rr:&nbsp;: :: "non-breaking\u00a0space"}`') == 'non-breaking space'


def test_filters_chain_left_to_right():
    html_body = """
    <p>one</p>
    <p>two</p>
    <p>three</p>"""
    assert query_html_doc(html_body, '`${j:, :tru:12: ...://p} whatever!`') == 'one, two, ... whatever!'


def test_character_escape_is_not_prematurely_decoded_in_interpolated_string():
    query = 'let $x := "foo" return `Variable "&#36;x" contains value $x`'
    assert query_html_doc('', query) == 'Variable "$x" contains value foo'  # Not 'Variable "foo" contains...'


def test_filters_are_applied_to_all_items_in_sequence_when_input_is_not_atomic():
    html_body = """
    <p>Hello, world!</p>
    <p>Goodbye, world!</p>"""
    assert query_html_doc(html_body, '`${tru:8:://p}`') == 'Hello,Goodbye,'
    assert query_html_doc(html_body, '`${rr:world:test:://p}`') == 'Hello, test!Goodbye, test!'
