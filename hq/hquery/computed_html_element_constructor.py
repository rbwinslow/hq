from bs4 import BeautifulSoup
from hq.hquery.evaluation_error import HqueryEvaluationError
from hq.hquery.object_type import is_string, make_node_set, object_type_name, make_sequence
from hq.soup_util import debug_dump_node, is_any_node, is_tag_node, is_attribute_node


class ComputedHtmlElementConstructor:

    def __init__(self, name):
        self.name = name
        self.contents = []


    def add_content(self, expression_fn):
        self.contents.append(expression_fn)


    def evaluate(self):
        soup = BeautifulSoup('<{0}></{0}>'.format(self.name), 'html.parser')
        result = getattr(soup, self.name)

        for expression_fn in self.contents:
            for value in make_sequence(expression_fn()):
                if is_string(value) or is_tag_node(value):
                    result.append(value)
                elif is_attribute_node(value):
                    result[value.name] = value.value
                else:
                    value_desc = debug_dump_node(value) if is_any_node(value) else object_type_name(
                        value)
                    raise HqueryEvaluationError(
                        'Cannot use {0} as a content object in a computed element constructor'.format(value_desc)
                    )

        return make_node_set(result)
