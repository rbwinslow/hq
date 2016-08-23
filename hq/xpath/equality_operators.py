from hq.verbosity import verbose_print
from hq.xpath.functions.core_boolean import boolean
from hq.xpath.object_type import object_type, string_value, object_type_name


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


def _eq_node_set_vs_number(nodes_val, num_val):
    return _eq_node_set_vs_string(nodes_val, string_value(num_val))


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


equality_ops_table = (
    # BOOLEAN,      NODE_SET,       NUMBER,                 STRING
    (_eq_native,    None,           None,                   None),  # BOOLEAN
    (None,          _eq_node_sets,  _eq_node_set_vs_number, _eq_node_set_vs_string),  # NODE_SET
    (None,          None,           _eq_native,             None),  # NUMBER
    (None,          None,           None,                   _eq_native),  # STRING
)


def equals(left, right):
    left_type = object_type(left)
    right_type = object_type(right)
    reverse = left_type > right_type
    op = equality_ops_table[left_type if not reverse else right_type][right_type if not reverse else left_type]
    if op is None:
        raise NotImplementedError('{0} = {1} not yet implemented'.format(object_type_name(left_type),
                                                                         object_type_name(right_type)))
    return boolean(op(left if not reverse else right, right if not reverse else left))


def not_equals(left, right):
    return boolean(not bool(equals(left, right)))
