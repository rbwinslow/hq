from bs4 import BeautifulSoup
from hq.hquery.evaluation_error import HqueryEvaluationError
from hq.hquery.object_type import is_string, object_type_name, is_number, is_boolean
from hq.hquery.sequences import make_node_set, make_sequence
from hq.hquery.syntax_error import HquerySyntaxError
from hq.soup_util import debug_dump_node, is_any_node, is_tag_node, is_attribute_node


class ComputedHtmlElementConstructor:

    def __init__(self, name):
        self.name = name
        self.contents = None


    def set_content(self, expression_fn):
        if self.contents is not None:
            raise HquerySyntaxError('Computed element constructor already has contents')
        self.contents = expression_fn


    def evaluate(self):
        soup = BeautifulSoup('<{0}></{0}>'.format(self.name), 'html.parser')
        result = getattr(soup, self.name)

        for value in make_sequence(self.contents()) if self.contents is not None else []:
            if is_tag_node(value):
                result.append(self._clone_tag(value))
            elif is_attribute_node(value):
                result[value.name] = value.value
            elif is_string(value) or is_number(value) or is_boolean(value):
                result.append(str(value))
            else:
                value_desc = debug_dump_node(value) if is_any_node(value) else object_type_name(value)
                raise HqueryEvaluationError(
                    'Cannot use {0} as a content object in a computed element constructor'.format(value_desc)
                )

        return make_node_set(result)


    def _clone_tag(self, tag):
        name = tag.name
        soup = BeautifulSoup(str(tag), 'html.parser')
        return getattr(soup, name)
