from hq.output import convert_results_to_output_text
from hq.soup_util import make_soup, is_any_node, root_tag_from_soup
from hq.hquery.hquery_processor import HqueryProcessor
from test.common_test_util import soup_with_body, eliminate_blank_lines


def query_html_doc(html_body, hquery, preserve_space=False, wrap_body=True):
    soup = soup_with_body(html_body) if wrap_body else make_soup(html_body)
    raw_result = HqueryProcessor(hquery, preserve_space=preserve_space).query(soup)
    return eliminate_blank_lines(convert_results_to_output_text(raw_result, preserve_space=preserve_space).strip())


def query_context_node(node_or_source, hquery):
    if not is_any_node(node_or_source):
        node_or_source = root_tag_from_soup(make_soup(node_or_source))
    raw_result = HqueryProcessor(hquery).query(node_or_source)
    return eliminate_blank_lines(convert_results_to_output_text(raw_result).strip())
