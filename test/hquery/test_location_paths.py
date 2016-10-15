import os
import sys

sys.path.insert(0, os.path.abspath('../..'))

from hq.output import convert_results_to_output_text
from hq.soup_util import make_soup
from hq.hquery.hquery_processor import HqueryProcessor

from ..common_test_util import expected_result
from test.hquery.hquery_test_util import query_html_doc


def test_absolute_location_path_should_find_multiple_grandchildren():
    actual = query_html_doc('<div>one</div><p>not a div</p><div>two</div>', '/html/body/div')
    assert actual == expected_result("""
    <div>
     one
    </div>
    <div>
     two
    </div>""")


def test_path_to_root_tag_succeeds_despite_other_root_level_objects():
    html = """
    <!DOCTYPE html>
    <!-- outside -->
    <html>
        <!-- inside -->
    </html>"""
    raw_result = HqueryProcessor('/*').query(make_soup(html))
    actual = convert_results_to_output_text(raw_result)
    assert actual == expected_result("""
    <html>
     <!-- inside -->
    </html>""")


def test_relative_location_path_as_predicate():
    html_body = """
    <div>
        <span>one</span>
    </div>
    <div>
        <p>two</p>
    </div>
    <div>
        <span>three</span>
    </div>"""
    actual = query_html_doc(html_body, '/html/body/div[span]')
    assert actual == expected_result("""
    <div>
     <span>
      one
     </span>
    </div>
    <div>
     <span>
      three
     </span>
    </div>""")


def test_abbreviated_context_node_works_in_path():
    html_body = """
    <div>
        <p>one</p>
    </div>
    <p>two</p>
    <div>
        <p>three</p>
    </div>"""
    actual = query_html_doc(html_body, '/html/body/div/./p')
    assert actual == expected_result("""
    <p>
     one
    </p>
    <p>
     three
    </p>""")


def test_abbreviated_context_node_works_in_predicate():
    html_body = """
    <div>
        <p>one</p>
    </div>
    <p>two</p>
    <div>
        three
    </div>
    <div>
        <p>four</p>
    </div>
    """
    actual = query_html_doc(html_body, '/html/body/node()[./p]')
    assert actual == expected_result("""
    <div>
     <p>
      one
     </p>
    </div>
    <div>
     <p>
      four
     </p>
    </div>""")


def test_abbreviated_parent_node_works_in_path():
    html_body = """
    <p>
        <span>one</span>
    </p>
    <p>
        <br/>
        <span>two</span>
    </p>"""
    actual = query_html_doc(html_body, '//p/br/../span')
    assert actual == expected_result("""
    <span>
     two
    </span>""")


def test_abbreviated_parent_node_works_in_predicate():
    html_body = """
    <p>
        <br/>
        <span>one</span>
    </p>
    <p>
        <span>two</span>
    </p>
    <p>
        <br/>
        <span>three</span>
    </p>"""
    actual = query_html_doc(html_body, '//span[../br]')
    assert actual == expected_result("""
    <span>
     one
    </span>
    <span>
     three
    </span>""")


def test_double_slash_works_within_path():
    html_body = """
    <section>
        <p>moe</p>
        <div>
            <div>
                <p>larry</p>
            </div>
            <p>curly</p>
        </div>
    </section>
    <p>joe besser</p>
    <section>
        <p>shemp</p>
    </section>"""
    assert query_html_doc(html_body, '//section//p') == expected_result("""
    <p>
     moe
    </p>
    <p>
     larry
    </p>
    <p>
     curly
    </p>
    <p>
     shemp
    </p>""")


def test_predicate_can_be_applied_to_variable_containing_node_set():
    html_body = """
    <p>not selected</p>
    <p id="foo">selected</p>"""
    assert query_html_doc(html_body, 'let $x := //p return $x[@id="foo"]') == expected_result("""
    <p id="foo">
     selected
    </p>""")


def test_no_space_between_text_runs_crossing_element_boundaries_in_element_string_value_if_there_was_none_in_doc():
    html_body = """<p>"<span>so-called</span>" Klingon  </p>"""
    assert query_html_doc(html_body, 'string(//p)') == '"so-called" Klingon'
    assert query_html_doc('<p>one <span>two</span></p>', 'string(//p)') == 'one two'
