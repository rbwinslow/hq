import re

from hq.hquery.evaluation_error import HqueryEvaluationError
from hq.hquery.expression_context import get_context_node
from hq.hquery.functions.core_boolean import boolean
from hq.hquery.functions.core_number import number
from hq.hquery.functions.extend_string import _xpath_flags_to_re_flags
from hq.hquery.object_type import string_value, normalize_content, is_string

exports = ('concat', 'contains', 'normalize_space', 'starts_with', 'string', 'string_length', 'substring',
           'substring_after', 'substring_before')


def concat(*args):
    return ''.join(string_value(arg) for arg in args)


def contains(*args):
    argc = len(args)
    if argc < 2 or argc > 3:
        raise HqueryEvaluationError('contains() function expects two or three arguments; {0} passed'.format(argc))
    if argc == 3:
        flags = args[2]
    else:
        flags = ''

    pattern = re.escape(string_value(args[1]))
    to_search = string_value(args[0])
    return boolean(bool(re.search(pattern, to_search, flags=_xpath_flags_to_re_flags(flags))))


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


def substring(*args):
    if len(args) < 2:
        raise HqueryEvaluationError('substring() expects at least 2 arguments; {0} were passed'.format(len(args)))
    value = args[0]
    start_index = args[1].value
    start = int(round(start_index) - 1)
    if len(args) >= 3:
        end = start + int(round(args[2].value))
    else:
        end = len(value) - start + 1
    return value[start if start >= 0 else 0:end]


def substring_after(first, second):
    first = string_value(first)
    index = first.find(second)
    if index < 0:
        return ''
    else:
        return first[index + 1:]


def substring_before(first, second):
    first = string_value(first)
    index = first.find(second)
    if index < 0:
        return ''
    else:
        return first[:index]
