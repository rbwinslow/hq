import re

from future.standard_library import install_aliases
from hq.hquery.expression_context import peek_context

install_aliases()

from itertools import filterfalse

from ..verbosity import verbose_print
from ..soup_util import is_any_node, is_tag_node, is_text_node, is_attribute_node


BOOLEAN, SEQUENCE, NUMBER, STRING = range(4)
TYPE_NAMES = ('BOOLEAN', 'SEQUENCE', 'NUMBER', 'STRING')


def is_boolean(obj):
    return obj.__class__.__name__ == 'boolean'


def is_node_set(obj):
    return isinstance(obj, list) and all(is_any_node(x) for x in obj)


def is_number(obj):
    return obj.__class__.__name__ == 'number'


def is_sequence(obj):
    return isinstance(obj, list)


def is_string(obj):
    return isinstance(obj, str) or obj.__class__.__name__.endswith('unicode')


def make_node_set(node_set, reverse=False):
    ids = []

    def is_unique_id(node):
        node_id = id(node)
        if node_id in ids:
            return False
        else:
            ids.append(node_id)
            return True

    if not isinstance(node_set, list):
        node_set = [node_set]

    node_set = list(sorted(filter(is_unique_id, node_set), key=lambda n: n.hq_doc_index, reverse=reverse))

    non_node_member = next(filterfalse(is_any_node, node_set), False)
    if non_node_member:
        format_str = 'Constructed node set that includes {0} object "{1}"'
        raise RuntimeError(format_str.format(object_type_name(non_node_member), non_node_member))

    return node_set


def make_sequence(sequence):
    if not isinstance(sequence, list):
        sequence = [sequence]
    return sequence


def sequence_concat(first, second):
    first = make_sequence(first)
    first.extend(make_sequence(second))
    return first


def normalize_content(value):
    return re.sub(r'\s+', ' ', string_value(value))


def object_type(obj):
    if is_boolean(obj):
        return BOOLEAN
    elif is_node_set(obj):
        return SEQUENCE
    elif is_sequence(obj):
        return SEQUENCE
    elif is_number(obj):
        return NUMBER
    elif is_string(obj):
        return STRING
    else:
        verbose_print('UH-OH! Returning None from object_type({0})'.format(obj.__class__.__name__))
        return None


def object_type_name(obj):
    result = 'NULL OR UNKNOWN TYPE'

    if obj is not None:
        if isinstance(obj, int):
            index = obj
        else:
            index = object_type(obj)
        result = TYPE_NAMES[index]

    return result


def string_value(obj):
    if is_tag_node(obj):
        if peek_context().preserve_space:
            return ''.join(obj.strings)
        else:
            return normalize_content(''.join(obj.stripped_strings))
    elif is_attribute_node(obj):
        return obj.value
    elif is_text_node(obj) or is_number(obj) or is_boolean(obj):
        return str(obj)
    elif is_node_set(obj):
        return string_value(obj[0]) if len(obj) > 0 else ''
    elif is_sequence(obj):
        return ''.join(string_value(item) for item in obj)
    elif is_string(obj):
        return obj
    else:
        raise NotImplementedError('string_value not yet implemented for type "{0}"'.format(obj.__class__.__name__))
