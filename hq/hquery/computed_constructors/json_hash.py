import json
import re

from hq.hquery.computed_constructors.hash_key_value import HashKeyValue
from hq.hquery.evaluation_error import HqueryEvaluationError
from hq.hquery.expression_context import peek_context
from hq.hquery.functions.core_number import number
from hq.hquery.object_type import string_value, object_type_name, is_string, is_number, is_boolean, \
    is_hash, is_array, is_sequence
from hq.hquery.sequences import make_sequence
from hq.hquery.syntax_error import HquerySyntaxError
from hq.soup_util import is_tag_node, debug_dump_node, is_any_node, is_text_node, debug_dump_long_string
from hq.verbosity import verbose_print


class JsonHash:

    def __init__(self, contents):
        if not isinstance(contents, dict):
            raise HqueryEvaluationError('Attempted to construct a JSON hash based on a(n) {0} object'.format(
                contents.__class__.__name__))
        self.contents = contents


    def __repr__(self):
        return 'HASH {0}'.format(repr(self.contents))


    def __str__(self):
        return json.dumps(self.contents)



def _construct_array_filter(tag_names):
    tag_names = tag_names.split(',')

    def evaluate(hash):
        for key, value in hash.items():
            if key in tag_names:
                if not isinstance(value, list):
                    verbose_print('JSON hash constructor array filter converting attribute "{0}" to array'.format(key))
                    hash[key] = [value]

    return evaluate


def _construct_map_filter(mappings):
    mappings = {old: new for (old, _, new) in [m.partition('>') for m in mappings.split(',')]}

    def evaluate(hash):
        for key, value in hash.items():
            if key in mappings:
                verbose_print('JSON hash constructor mapping filter converting attribute name "{0}" to "{1}"'.format(key, value))
                hash[mappings[key]] = hash[key]
                del hash[key]

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

def _skip_over_embedded_groups_from_list_matches(groups):
    return groups[::2]


_filter_map = {
    r'a:{0}:'.format(_name_list_arg_regex): _construct_array_filter,
    r'm:(([a-zA-Z]\w*>[a-zA-Z]\w*,?)+):': _construct_map_filter,
    r'n:{0}:'.format(_name_list_arg_regex): _construct_number_filter,
}


class ComputedJsonHashConstructor:

    def __init__(self):
        self.contents = None
        self.filters = []


    def set_contents(self, expression_fn):
        if self.contents is not None:
            raise HquerySyntaxError('computed JSON hash constructor already has contents')
        self.contents = expression_fn


    def set_filters(self, source):
        while len(source) > 0:
            match = None
            for regex, constructor in _filter_map.items():
                match = re.match(regex, source)
                if match:
                    filter_fn = constructor(*_skip_over_embedded_groups_from_list_matches(match.groups()))
                    self.filters.append(filter_fn)
                    source = source[match.span()[1]:]
                    break
            if match is None:
                raise HquerySyntaxError(
                    'Malformed filter "{0}" in computed JSON hash constructor filter clause'.format(source)
                )


    def evaluate(self):
        result = dict()

        for item in make_sequence(self.contents()) if self.contents is not None else []:
            if isinstance(item, HashKeyValue):
                if is_sequence(item.value) and len(item.value) == 1:
                    item.value = item.value[0]

                if is_number(item.value) or is_boolean(item.value):
                    result[item.key] = item.value.value
                elif is_hash(item.value) or is_array(item.value):
                    result[item.key] = item.value.contents
                else:
                    result[item.key] = string_value(item.value)
            elif is_tag_node(item):
                self._gab('adding element "{0}" to contents'.format(item.name))
                self._process_tag(result, item)
            elif is_text_node(item) or is_string(item):
                self._gab('adding text "{0}" to contents'.format(debug_dump_long_string(string_value(item))))
                result['text'] = self._append_to_text(result['text'] if 'text' in result else '', string_value(item))
            else:
                value_desc = debug_dump_node(item) if is_any_node(item) else object_type_name(item)
                raise HqueryEvaluationError(
                    'Cannot use {0} as a content object in a computed JSON hash constructor'.format(value_desc)
                )

            self._process_filters(result)

        return JsonHash(result)


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
