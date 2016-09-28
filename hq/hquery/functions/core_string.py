from hq.hquery.evaluation_error import HqueryEvaluationError
from hq.hquery.expression_context import get_context_node
from hq.hquery.functions.core_boolean import boolean
from hq.hquery.functions.core_number import number
from hq.hquery.object_type import string_value, normalize_content, is_string

exports = ['concat', 'normalize_space', 'starts_with', 'string', 'string_length']


def concat(*args):
    return ''.join(string_value(arg) for arg in args)


def normalize_space(*args):
    if len(args) == 1:
        return normalize_content(args[0])
    else:
        return normalize_content(get_context_node())


def starts_with(left, right):
    return boolean(string_value(left).startswith(string_value(right)))


def string(*args):
    if len(args) == 1:
        return string_value(args[0])
    else:
        return string_value(get_context_node())


def string_length(*args):
    value = args[0] if len(args) == 1 else string_value(get_context_node())
    if not is_string(value):
        raise HqueryEvaluationError('string_length() expecting a string, got a {0}'.format(value.__class__.__name__))
    return number(len(value))
