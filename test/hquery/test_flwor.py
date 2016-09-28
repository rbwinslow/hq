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
