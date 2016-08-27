from future.standard_library import install_aliases

install_aliases()

from collections import OrderedDict
from itertools import filterfalse

from hq.soup_util import is_any_node, is_tag_node, is_text_node

BOOLEAN, NODE_SET, NUMBER, STRING = range(4)
TYPE_NAMES = ('BOOLEAN', 'NODE_SET', 'NUMBER', 'STRING')


def is_boolean(obj):
    return obj.__class__.__name__ == 'boolean'


def is_node_set(obj):
    return isinstance(obj, list)


def is_number(obj):
    return obj.__class__.__name__ == 'number'


def is_string(obj):
    return isinstance(obj, str)


def make_node_set(node_set):
    if not isinstance(node_set, list):
        node_set = [node_set]
    node_set = list(OrderedDict.fromkeys(node_set))
    non_node_member = next(filterfalse(is_any_node, node_set), False)
    if non_node_member:
        format_str = 'Constructed node set that includes {0} object "{1}"'
        raise RuntimeError(format_str.format(object_type_name(non_node_member), non_node_member))
    return node_set


def object_type(obj):
    if is_boolean(obj):
        return BOOLEAN
    elif is_node_set(obj):
        return NODE_SET
    elif is_number(obj):
        return NUMBER
    elif is_string(obj):
        return STRING
    else:
        return None


def object_type_name(obj):
    if isinstance(obj, int):
        index = obj
    else:
        index = object_type(obj)
    return TYPE_NAMES[index]


def string_value(obj):
    if is_tag_node(obj):
        return ''.join(obj.stripped_strings)
    elif is_text_node(obj) or is_number(obj):
        return str(obj);
    elif is_node_set(obj):
        return string_value(obj[0]) if len(obj) > 0 else ''
    elif isinstance(obj, str):
        return obj
    else:
        raise NotImplementedError('string_value not yet implemented for type "{0}"'.format(obj.__class__.__name__))
