from hq.hquery.syntax_error import HquerySyntaxError
from pytest import raises
from test.hquery.hquery_test_util import query_html_doc


def test_variable_declaration_and_reference_in_a_flwor():
    expected = 'bar'
    assert query_html_doc('', 'let $foo := "{0}" return $foo'.format(expected)) == expected


def test_variable_declarations_are_processed_in_order():
    assert query_html_doc('', 'let $hello := "hello, " let $whole-phrase := concat($hello, "world!") return $whole-phrase') == 'hello, world!'


def test_multiple_return_clauses_are_not_allowed():
    with raises(HquerySyntaxError):
        query_html_doc('', 'let $x := "whatever" return $x return "uh-oh"')


def test_that_no_other_clauses_are_allowed_after_a_return():
    with raises(HquerySyntaxError):
        query_html_doc('', 'let $x := "whatevs" return $x let $uh-oh := "oh no"')
