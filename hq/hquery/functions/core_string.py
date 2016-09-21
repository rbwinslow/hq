from hq.hquery.functions.core_boolean import boolean
from hq.hquery.object_type import string_value


exports = ['concat', 'starts_with']


def concat(*args):
    return ''.join(string_value(arg) for arg in args)


def starts_with(left, right):
    return boolean(string_value(left).startswith(string_value(right)))
