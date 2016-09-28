from hq.verbosity import verbose_print
from hq.hquery.functions.core_boolean import boolean
from hq.hquery.functions.core_number import number
from hq.hquery.object_type import object_type, string_value, object_type_name
from hq.hquery.evaluation_error import HqueryEvaluationError


def _eq_bool_vs_primitive(bool_val, other_val):
    verbose_print('Comparing boolean value {0} with non-node-set value {1} (coerced to {2})'.format(bool_val, other_val, boolean(other_val)))
    return bool_val == boolean(other_val)


def _eq_native(first, second):
    return first == second


def _eq_node_sets(first, second):
    first_values = set([string_value(node) for node in first])
    second_values = set([string_value(node) for node in second])

    verbose_print('Comparing two nodes sets (size {0} and {1}).'.format(len(first_values), len(second_values)))

    for first_value in first_values:
        if first_value in second_values:
            verbose_print(u'Found value "{0}" from first node set in second node set'.format(first_value))
            return True

    verbose_print('Found no matching nodes between node sets.')
    return False


def _eq_node_set_vs_bool(bool_val, nodes_val):
    return bool_val == boolean(nodes_val)


def _eq_node_set_vs_number(nodes_val, num_val):
    verbose_print('(=) comparing number {0} to {1} nodes'.format(num_val, len(nodes_val)))

    for node in nodes_val:
        node_str_val = string_value(node)
        node_num_val = number(node_str_val)
        verbose_print('(=) node string value "{0}" is{1} equal to "{2}"'.format(
            node_num_val,
            (' not' if node_num_val == num_val else ''),
            num_val))

        if node_num_val == num_val:
            return True

    return False


def _eq_node_set_vs_string(nodes_val, string_val):
    string_val = str(string_val)
    verbose_print(u'(=) comparing number "{0}" to {1} nodes'.format(string_val, len(nodes_val)))

    for node in nodes_val:
        node_val_string = string_value(node)
        verbose_print(u'(=) node string value "{0}" is{1} equal to "{2}"'.format(
            node_val_string,
            ('' if node_val_string == string_val else ' not'),
            string_val))

        if node_val_string == string_val:
            return True

    return False


def _eq_num_vs_string(num_val, string_val):
    return num_val == number(string_val)


equality_ops_table = (
    # BOOLEAN,      SEQUENCE,               NUMBER,                 STRING
    (_eq_native,    _eq_node_set_vs_bool,   _eq_bool_vs_primitive,  _eq_bool_vs_primitive),     # BOOLEAN
    (None,          _eq_node_sets,          _eq_node_set_vs_number, _eq_node_set_vs_string),    # SEQUENCE
    (None,          None,                   _eq_native,             _eq_num_vs_string),         # NUMBER
    (None,          None,                   None,                   _eq_native),                # STRING
)


def equals(first, second):
    first_type = object_type(first)
    second_type = object_type(second)
    try:
        reverse = first_type > second_type
        op = equality_ops_table[first_type if not reverse else second_type][second_type if not reverse else first_type]
        return boolean(op(first if not reverse else second, second if not reverse else first))
    except TypeError:
        msg = 'type mismatch comparing {0} and {1} for equality'
        raise HqueryEvaluationError(msg.format(object_type_name(first_type), object_type_name(second_type)))


def not_equals(first, second):
    return boolean(not bool(equals(first, second)))
