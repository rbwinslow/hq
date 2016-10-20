import re
from builtins import str

from future.standard_library import install_aliases
from hq.hquery.expression_context import peek_context
from hq.string_util import truncate_string

install_aliases()

from itertools import filterfalse

from ..verbosity import verbose_print
from ..soup_util import is_any_node, is_tag_node, is_text_node, is_attribute_node, debug_dump_node, \
    debug_dump_long_string, derive_text_from_node


BOOLEAN, SEQUENCE, NUMBER, STRING = range(4)
TYPE_NAMES = ('BOOLEAN', 'SEQUENCE', 'NUMBER', 'STRING')


def debug_dump_anything(obj):
    if is_any_node(obj):
        result = debug_dump_node(obj)
    elif is_boolean(obj) or is_number(obj) or is_hash(obj) or is_array(obj):
        result = repr(obj)
    elif is_string(obj):
        result = u'string("{0}")'.format(obj)
    elif is_node_set(obj):
        result = u'node-set({0})'.format(', '.join(truncate_string(debug_dump_node(node), 20) for node in obj))
    elif is_sequence(obj):
        result = u'sequence({0})'.format(', '.join(truncate_string(debug_dump_anything(item), 20) for item in obj))
    else:
        raise RuntimeError("debug_dump_anything doesn't know how to handle {0}".format(obj.__class__.__name__))
    return debug_dump_long_string(result)


def is_array(obj):
    return obj.__class__.__name__ == 'JsonArray'


def is_boolean(obj):
    return obj.__class__.__name__ == 'boolean'


def is_hash(obj):
    return obj.__class__.__name__ == 'JsonHash'


def is_node_set(obj):
    return isinstance(obj, list) and all(is_any_node(x) for x in obj)


def is_number(obj):
    return obj.__class__.__name__ == 'number'


def is_sequence(obj):
    return isinstance(obj, list)


def is_string(obj):
    class_name = obj.__class__.__name__
    return class_name.endswith('str') or class_name.endswith('unicode')


def make_node_set(node_set, reverse=False):
    ids = set()

    def is_unique_id(node):
        node_id = id(node)
        if node_id in ids:
            return False
        else:
            ids.add(node_id)
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
    if is_tag_node(obj) or is_attribute_node(obj) or is_text_node(obj):
        return derive_text_from_node(obj, peek_context().preserve_space)
    elif is_number(obj) or is_boolean(obj):
        return str(obj)
    elif is_node_set(obj):
        return string_value(obj[0]) if len(obj) > 0 else ''
    elif is_sequence(obj):
        return ''.join(string_value(item) for item in obj)
    elif is_string(obj):
        return obj
    else:
        raise NotImplementedError('string_value not implemented for type "{0}"'.format(obj.__class__.__name__))
