from itertools import filterfalse

from hq.hquery.evaluation_error import HqueryEvaluationError
from hq.hquery.object_type import object_type_name
from hq.soup_util import is_any_node


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

    non_node_member = next(filterfalse(is_any_node, node_set), False)
    if non_node_member:
        format_str = 'Constructed node set that includes {0} object "{1}"'
        raise HqueryEvaluationError(format_str.format(object_type_name(non_node_member), non_node_member))

    node_set = list(sorted(filter(is_unique_id, node_set), key=lambda n: n.hq_doc_index, reverse=reverse))

    return node_set


def make_sequence(sequence):
    if not isinstance(sequence, list):
        sequence = [sequence]
    return sequence


def sequence_concat(first, second):
    first = make_sequence(first)
    first.extend(make_sequence(second))
    return first
