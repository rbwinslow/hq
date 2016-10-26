from hq.hquery.syntax_error import HquerySyntaxError
from pytest import raises
from test.common_test_util import expected_result
from test.hquery.hquery_test_util import query_html_doc


def test_variable_declaration_and_reference_in_a_flwor():
    expected = 'bar'
    assert query_html_doc('', 'let $foo := "{0}" return $foo'.format(expected)) == expected


def test_variable_declarations_are_processed_in_order():
    hquery = 'let $hello := "hello, " let $whole-phrase := concat($hello, "world!") return $whole-phrase'
    assert query_html_doc('', hquery) == 'hello, world!'


def test_variable_is_accessible_inside_interpolated_string():
    assert query_html_doc('', 'let $foo := "bar" return `foo is $foo`') == 'foo is bar'
    assert query_html_doc('', 'let $foo := (1 to 3) return `${j:, :$foo}`') == '1, 2, 3'


def test_multiple_return_clauses_are_not_allowed():
    with raises(HquerySyntaxError):
        query_html_doc('', 'let $x := "whatever" return $x return "uh-oh"')


def test_that_no_other_clauses_are_allowed_after_a_return():
    with raises(HquerySyntaxError):
        query_html_doc('', 'let $x := "whatevs" return $x let $uh-oh := "oh no"')


def test_iteration_using_for():
    html_body = """
    <p>one</p>
    <p>two</p>
    <p>three</p>"""
    assert query_html_doc(html_body, 'for $x in //p return $x/text()') == expected_result("""
    one
    two
    three""")


def test_flwor_variable_declaration_within_iteration():
    query = 'for $x in (1 to 2) let $y := concat("Thing ", string($x)) return $y'
    assert query_html_doc('', query) == expected_result("""
    Thing 1
    Thing 2""")


def test_rooted_location_paths_work_with_both_kinds_of_slash():
    html_body = """
    <section>
        <div>
            <div>foo</div>
        </div>
    </section>
    <section>
        <div>
            <div>bar</div>
        </div>
    </section>"""

    assert query_html_doc(html_body, 'for $x in //section return $x/div') == expected_result("""
    <div>
     <div>
      foo
     </div>
    </div>
    <div>
     <div>
      bar
     </div>
    </div>""")

    assert query_html_doc(html_body, 'for $x in //section return $x//div') == expected_result("""
    <div>
     <div>
      foo
     </div>
    </div>
    <div>
     foo
    </div>
    <div>
     <div>
      bar
     </div>
    </div>
    <div>
     bar
    </div>""")


def test_variables_before_for_have_global_scope_and_within_for_have_iteration_scope():
    query = """
    let $x := 2
    let $z := $x
    for $_ in (1, $x)
    let $y := $_
    let $x := $_
    return ($x, $z, $x = $y)"""

    assert query_html_doc('', ' '.join(query.split('\n'))) == expected_result("""
    1
    2
    true
    2
    2
    true""")


def test_flwor_with_multiple_for_clauses_is_a_syntax_error():
    with raises(HquerySyntaxError):
        query_html_doc('', 'for $x in (1, 2) let $y := 0 for $z in (3, 4) return $z')


def test_flwor_with_multiple_return_clauses_is_a_syntax_error():
    with raises(HquerySyntaxError):
        query_html_doc('', 'let $x := 0 return $x return $x + 1')


def test_abbreviated_flowr_provides_expected_iteration_variable_in_value_clause():
    html_body = """
    <p>one</p>
    <p>two</p>
    <p>three</p>"""

    assert query_html_doc(html_body, '//p -> $_/text()') == expected_result("""
    one
    two
    three""")


def test_nested_abbreviated_flwors_evaluate_as_expected():
    html_body = """
    <div>
        <p>one</p>
        <p>two</p>
    </div>
    <div>
        <p>three</p>
        <p>four</p>
        <p>five</p>
    </div>"""

    assert query_html_doc(html_body, '//div -> $_/p[odd()] -> $_/text()') == expected_result("""
    one
    three
    five""")


def test_comma_as_sequence_cat_operator_does_not_bind_at_end_of_return_clause():
    assert query_html_doc('', 'for $x in (1 to 2) return $x, "!"') == expected_result("""
    1
    2
    !""")
    assert query_html_doc('', 'sum(for $x in //span return $x, "zero")') == 'zero'
    assert query_html_doc('', 'sum(//span -> $_, "zero")') == 'zero'


def test_lack_of_return_at_end_of_flwor_is_a_syntax_error():
    with raises(HquerySyntaxError):
        query_html_doc('', 'let $nil := "nothing"')


def test_comma_can_be_used_to_declare_multiple_variables_in_a_let_clause():
    assert query_html_doc('', 'let $foo := "foo", $bar := "bar" return string-join(($foo, $bar), " ")') == 'foo bar'
