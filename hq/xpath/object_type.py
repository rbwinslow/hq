from future.standard_library import install_aliases

install_aliases()

from collections import OrderedDict
from itertools import filterfalse

from hq.soup_util import is_any_node, is_tag_node


def is_node_set(obj):
    return isinstance(obj, list)


def is_number(obj):
    return isinstance(obj, int) or isinstance(obj, float)


def make_node_set(node_set):
    if not isinstance(node_set, list):
        node_set = [node_set]
    node_set = list(OrderedDict.fromkeys(node_set))
    non_node_member = next(filterfalse(is_any_node, node_set), False)
    if non_node_member:
        raise RuntimeError('Constructed node set that includes non-node object "{0}"'.format(non_node_member))
    return node_set


def string_value(obj):
    if is_tag_node(obj):
        return ''.join(obj.stripped_strings)
    else:
        raise NotImplementedError('string_value not yet implemented for type "{0}"'.format(obj.__class__.__name__))
