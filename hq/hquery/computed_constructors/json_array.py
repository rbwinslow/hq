import json

from hq.hquery.evaluation_error import HqueryEvaluationError
from hq.hquery.object_type import make_sequence, string_value, is_string, object_type_name, debug_dump_anything, is_hash, \
    is_boolean, is_number
from hq.hquery.syntax_error import HquerySyntaxError
from hq.soup_util import is_tag_node, is_text_node, debug_dump_node, is_any_node, debug_dump_long_string
from hq.verbosity import verbose_print


class JsonArray:

    def __init__(self, contents):
        if not isinstance(contents, list):
            raise HqueryEvaluationError('Attempted to construct a JSON array based on a(n) {0} object'.format(
                contents.__class__.__name__))
        self.contents = contents


    def __repr__(self):
        return 'ARRAY {0}'.format(repr(self.contents))


    def __str__(self):
        return json.dumps(self.contents)



class ComputedJsonArrayConstructor:

    def __init__(self):
        self.contents = None


    def set_contents(self, expression_fn):
        if self.contents is not None:
            raise HquerySyntaxError('computed JSON array constructor already has contents')
        self.contents = expression_fn


    def evaluate(self):
        return JsonArray([self._make_array_item(item) for item in make_sequence(self.contents())])


    def _make_array_item(self, value):
        dump = debug_dump_anything(value)
        if is_tag_node(value):
            self._gab('appending text contents of element "{0}" to array'.format(dump))
            return string_value(value)
        elif is_text_node(value) or is_string(value):
            value = string_value(value)
            self._gab(u'appending text "{0}" to array'.format(dump))
            return value
        elif is_boolean(value) or is_number(value):
            self._gab('appending {0} to array'.format(dump))
            return value.value
        elif is_hash(value):
            self._gab(u'appending JSON {0} to array'.format(dump))
            return value.contents
        else:
            raise HqueryEvaluationError("Can't use {0} as contents in a computed JSON array constructor".format(dump))


    def _gab(self, message):
        verbose_print('JSON array constructor {0}'.format(message))
