from hq.hquery.evaluation_error import HqueryEvaluationError
from hq.hquery.expression_context import peek_context, get_context_node
from hq.hquery.functions.core_number import number
from hq.hquery.object_type import string_value, is_sequence, object_type_name
from hq.hquery.sequences import make_node_set
from hq.soup_util import root_tag_from_any_tag, is_tag_node

exports = ('count', 'id', 'last', 'name', 'position')


def count(sequence):
    HqueryEvaluationError.must_be_node_set_or_sequence(sequence)
    return number(len(sequence))


def id(ids):
    if is_sequence(ids):
        ids = set(string_value(item) for item in ids)
    else:
        ids = set(string_value(ids).split())
    result = []
    for node in root_tag_from_any_tag(get_context_node()).descendants:
        if is_tag_node(node) and 'id' in node.attrs and node['id'] in ids:
            result.append(node)
    return make_node_set(result)


def last():
    return number(peek_context().size)


def name(*args):
    if len(args) > 0:
        value = args[0]
        if is_sequence(value):
            value = value[0]
        if is_tag_node(value):
            return value.name
        else:
            return ''
    else:
        node = get_context_node()
        if is_tag_node(node):
            return node.name
        else:
            return ''


def position():
    return number(peek_context().position)
