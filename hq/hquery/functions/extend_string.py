import re

from hq.hquery.evaluation_error import HqueryEvaluationError
from hq.hquery.expression_context import get_context_node
from hq.hquery.functions.core_boolean import boolean
from hq.hquery.object_type import string_value

exports = ('lower_case', 'matches', 'replace', 'string_join', 'tokenize', 'upper_case')


def lower_case(value):
    return string_value(value).lower()


def matches(*args):
    scenario = len(args)
    flags = 0

    if scenario < 1 or scenario > 3:
        raise HqueryEvaluationError('matches() called with {0} arguments; expected one, two or three.'.format(scenario))

    if scenario == 1:
        input = string_value(get_context_node())
        pattern = args[0]
    else:
        input = string_value(args[0])
        pattern = args[1]
        if scenario == 3:
            flags = _xpath_flags_to_re_flags(args[2])

    return boolean(re.search(pattern, input, flags))


def replace(*args):
    argc = len(args)
    if argc < 3 or argc > 4:
        raise HqueryEvaluationError('replace() expects 3 or 4 arguments; was passed {0}'.format(argc))

    input = string_value(args[0])
    pattern = args[1]
    replacement = args[2]
    if argc == 4:
        flags = _xpath_flags_to_re_flags(args[3])
    else:
        flags = 0

    return re.sub(pattern, replacement, input, flags=flags)


def string_join(sequence, *args):
    if len(args) > 0:
        delimiter = args[0]
    else:
        delimiter = ''
    return delimiter.join([string_value(x) for x in sequence])


def tokenize(*args):
    argc = len(args)
    if argc < 2 or argc > 3:
        raise HqueryEvaluationError('replace() expects 2 or 3 arguments; was passed {0}'.format(argc))

    input = string_value(args[0])
    pattern = args[1]
    if argc == 3:
        flags = _xpath_flags_to_re_flags(args[2])
    else:
        flags = 0

    return re.split(pattern, input, flags=flags)


def upper_case(value):
    return string_value(value).upper()


def _xpath_flags_to_re_flags(flags):
    re_flags_map = {
        'i': re.IGNORECASE,
        'm': re.MULTILINE,
        's': re.DOTALL,
        'x': re.VERBOSE,
    }

    try:
        result = 0
        for flag in flags:
            result |= re_flags_map[flag]
        return result
    except KeyError as e:
        raise HqueryEvaluationError('Unexpected regular expression flag "{0}"'.format(e.args[0]))
