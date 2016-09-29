import json
import re

from hq.hquery.evaluation_error import HqueryEvaluationError
from hq.hquery.functions.core_number import number
from hq.hquery.object_type import make_sequence, string_value, object_type_name, is_string
from hq.hquery.syntax_error import HquerySyntaxError
from hq.soup_util import is_tag_node, debug_dump_node, is_any_node, is_text_node, debug_dump_long_string
from hq.verbosity import verbose_print


def _construct_array_filter(tag_names):
    tag_names = tag_names.split(',')

    def evaluate(hash):
        for key, value in hash.items():
            if key in tag_names:
                if not isinstance(value, list):
                    verbose_print('JSON hash constructor array filter converting attribute "{0}" to array'.format(key))
                    hash[key] = [value]

    return evaluate


def _construct_number_filter(tag_names):
    tag_names = tag_names.split(',')

    def evaluate(hash):
        for key, value in hash.items():
            if key in tag_names:
                verbose_print(
                    'JSON hash constructor number filter converting attribute "{0}" value(s) to numbers'.format(key)
                )
                if isinstance(value, list):
                    hash[key] = [number(v).value for v in value]
                else:
                    hash[key] = number(value).value

    return evaluate


_name_list_arg_regex = r'(([a-zA-Z]\w*,?)+)'

def _skip_over_embedded_groups_from_name_list_matches(groups):
    return groups[::2]


_filter_map = {
    r'a:{0}:'.format(_name_list_arg_regex): _construct_array_filter,
    r'n:{0}:'.format(_name_list_arg_regex): _construct_number_filter,
}


class ComputedJsonHashConstructor:

    def __init__(self):
        self.contents = None
        self.filters = []


    def set_content(self, expression_fn):
        if self.contents is not None:
            raise HquerySyntaxError('Computed JSON hash constructor already has contents')
        self.contents = expression_fn


    def set_filters(self, source):
        while len(source) > 0:
            for regex, constructor in _filter_map.items():
                match = re.match(regex, source)
                if match:
                    filter_fn = constructor(*_skip_over_embedded_groups_from_name_list_matches(match.groups()))
                    self.filters.append(filter_fn)
                    source = source[match.span()[1]:]
                    break


    def evaluate(self):
        result = dict()

        for value in make_sequence(self.contents()) if self.contents is not None else []:
            if is_tag_node(value):
                self._gab('adding element "{0}" to contents'.format(value.name))
                self._process_tag(result, value)
            elif is_text_node(value) or is_string(value):
                self._gab('adding text "{0}" to contents'.format(debug_dump_long_string(string_value(value))))
                result['text'] = self._append_to_text(result['text'] if 'text' in result else '', string_value(value))
            else:
                value_desc = debug_dump_node(value) if is_any_node(value) else object_type_name(value)
                raise HqueryEvaluationError(
                    'Cannot use {0} as a content object in a computed JSON hash constructor'.format(value_desc)
                )

            self._process_filters(result)

        return json.dumps(result)


    def _append_to_text(self, so_far, more_content):
        return '{0}{1}{2}'.format(so_far, ' ' if len(so_far) > 0 else '', more_content)


    def _gab(self, message):
        verbose_print('JSON hash constructor {0}'.format(message))


    def _process_filters(self, result):
        for filter in self.filters:
            filter(result)


    def _process_tag(self, result, value):
        new_value = string_value(value)
        if value.name in result:
            if isinstance(result[value.name], list):
                result[value.name].append(new_value)
            else:
                result[value.name] = [result[value.name], new_value]
        else:
            result[value.name] = new_value
