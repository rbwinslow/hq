from hq.verbosity import verbose_print
from hq.xpath.functions.core_boolean import boolean
from hq.xpath.functions.core_number import number
from hq.xpath.object_type import object_type, string_value, object_type_name
from hq.xpath.query_error import XpathQueryError


def _eq_bool_vs_primitive(bool_val, other_val):
    verbose_print('Comparing boolean value {0} with non-node-set value {1} (coerced to {2})'.format(bool_val, other_val, boolean(other_val)))
    return bool_val == boolean(other_val)


def _eq_native(left, right):
    return left == right


def _eq_node_sets(left, right):
    left_values = set([string_value(node) for node in left])
    right_values = set([string_value(node) for node in right])

    verbose_print('Comparing two nodes sets (size {0} and {1}).'.format(len(left_values), len(right_values)))

    for left_value in left_values:
        if left_value in right_values:
            verbose_print('Found value "{0}" from left-hand node set in right-hand node set'.format(left_value))
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
    verbose_print('(=) comparing number "{0}" to {1} nodes'.format(string_val, len(nodes_val)))

    for node in nodes_val:
        node_val_string = string_value(node)
        verbose_print('(=) node string value "{0}" is{1} equal to "{2}"'.format(
            node_val_string,
            (' not' if node_val_string == string_val else ''),
            string_val))

        if node_val_string == string_val:
            return True

    return False


def _eq_num_vs_string(num_val, string_val):
    return num_val == number(string_val)


equality_ops_table = (
    # BOOLEAN,      NODE_SET,               NUMBER,                 STRING
    (_eq_native,    _eq_node_set_vs_bool,   _eq_bool_vs_primitive,  _eq_bool_vs_primitive),     # BOOLEAN
    (None,          _eq_node_sets,          _eq_node_set_vs_number, _eq_node_set_vs_string),    # NODE_SET
    (None,          None,                   _eq_native,             _eq_num_vs_string),         # NUMBER
    (None,          None,                   None,                   _eq_native),                # STRING
)


def equals(left, right):
    left_type = object_type(left)
    right_type = object_type(right)
    try:
        reverse = left_type > right_type
        op = equality_ops_table[left_type if not reverse else right_type][right_type if not reverse else left_type]
        return boolean(op(left if not reverse else right, right if not reverse else left))
    except TypeError:
        raise XpathQueryError('type mismatch comparing {0} and {1} for equality'.format(object_type_name(left_type),
                                                                                        object_type_name(right_type)))


def not_equals(left, right):
    return boolean(not bool(equals(left, right)))
