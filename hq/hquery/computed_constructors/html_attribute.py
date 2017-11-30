from hq.hquery.evaluation_error import HqueryEvaluationError
from hq.hquery.object_type import is_string, is_number, is_boolean, object_type_name, string_value
from hq.hquery.sequences import make_sequence
from hq.hquery.syntax_error import HquerySyntaxError
from hq.soup_util import debug_dump_node, is_any_node, AttributeNode, is_attribute_node, is_tag_node


class ComputedHtmlAttributeConstructor:

    def __init__(self, name):
        self.name = name
        self.contents = None


    def set_content(self, expression_fn):
        if self.contents is not None:
            raise HquerySyntaxError('Computed attribute constructor already has contents')
        self.contents = expression_fn


    def evaluate(self):
        result = ''

        for value in make_sequence(self.contents()) if self.contents is not None else []:
            if is_string(value) or is_number(value) or is_boolean(value):
                result = self._append_to_contents(result, str(value))
            elif is_attribute_node(value):
                result = self._append_to_contents(result, value.value)
            elif is_tag_node(value):
                result = self._append_to_contents(result, string_value(value))
            else:
                value_desc = debug_dump_node(value) if is_any_node(value) else object_type_name(value)
                raise HqueryEvaluationError(
                    'Cannot use {0} as a content object in a computed attribute constructor'.format(value_desc)
                )

        return AttributeNode(self.name, result)


    def _append_to_contents(self, so_far, more_content):
        return '{0}{1}{2}'.format(so_far, ' ' if len(so_far) > 0 else '', more_content)
