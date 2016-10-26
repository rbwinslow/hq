from operator import gt, lt, ge, le

from hq.hquery.functions.core_string import string
from hq.verbosity import verbose_print
from hq.hquery.functions.core_boolean import boolean
from hq.hquery.functions.core_number import number
from hq.hquery.object_type import object_type, is_boolean, is_number
from hq.hquery.syntax_error import HquerySyntaxError


class RelationalOperator:

    def __init__(self, op):
        if op == '>':
            self.base_op = gt
        elif op == '>=':
            self.base_op = ge
        elif op == '<':
            self.base_op = lt
        elif op == '<=':
            self.base_op = le
        else:
            raise HquerySyntaxError('unexpected relational operator "{0}"'.format(op))


    def evaluate(self, first, second):
        first_type = object_type(first)
        second_type = object_type(second)
        cmp = comparison_method_table[first_type][second_type]
        return boolean(cmp(self.base_op, first, second))


    @property
    def name(self):
        return self.base_op.__name__



def _cmp_node_sets(base_op, first, second):
    first_values = set([number(node) for node in first])
    second_values = set([number(node) for node in second])

    verbose_print('Comparing two nodes sets (size {0} and {1}).'.format(len(first_values), len(second_values)))

    for first_value in first_values:
        for second_value in second_values:
            if base_op(first_value, second_value):
                msg = 'Comparison succeeded for "{0}" from first node set and "{1}" in second node set'
                verbose_print(msg.format(first_value, second_value))
                return True

    verbose_print('Comparison failed for all nodes in both node sets.')
    return False


def _cmp_nodes_to_value(base_op, first, second):
    node_values = set([number(node) for node in first])
    second = number(second)
    verbose_print('Comparing {0} nodes in node set to value {1}'.format(len(node_values), second))

    for node_value in node_values:
        if base_op(node_value, second):
            verbose_print('Comparison succeeded for node value "{0}" and value "{1}"'.format(node_value, second))
            return True

    verbose_print('Comparison failed for all nodes in the node set.')
    return False


def _cmp_value_to_nodes(base_op, first, second):
    node_values = set([number(node) for node in second])
    first = number(first)
    verbose_print('Comparing {0} nodes in node set to value "{1}"'.format(len(node_values), first))

    for node_value in node_values:
        if base_op(first, node_value):
            verbose_print('Comparison succeeded for value "{0}" and node value "{1}'.format(first, node_value))
            return True

    verbose_print('Comparison failed for all nodes in the node set.')
    return False


def _cmp_values(base_op, first, second):
    if is_boolean(first) or is_boolean(second):
        return base_op(1 if boolean(first) else 0, 1 if boolean(second) else 0)
    elif is_number(first) or is_number(second):
        return base_op(number(first), number(second))
    else:
        return base_op(string(first), string(second))


comparison_method_table = (
    # BOOLEAN,              SEQUENCE,               NUMBER,                 STRING
    (_cmp_values,           _cmp_value_to_nodes,    _cmp_values,            _cmp_values),           # BOOLEAN
    (_cmp_nodes_to_value,   _cmp_node_sets,         _cmp_nodes_to_value,    _cmp_nodes_to_value),   # SEQUENCE
    (_cmp_values,           _cmp_value_to_nodes,    _cmp_values,            _cmp_values),           # NUMBER
    (_cmp_values,           _cmp_value_to_nodes,    _cmp_values,            _cmp_values),           # STRING
)
