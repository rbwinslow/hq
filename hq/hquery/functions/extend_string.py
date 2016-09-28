import re
from functools import reduce

from hq.hquery.evaluation_error import HqueryEvaluationError
from hq.hquery.expression_context import get_context_node
from hq.hquery.functions.core_boolean import boolean
from hq.hquery.object_type import string_value

exports = ['join', 'matches']


def join(sequence, delimiter):
    return delimiter.join([string_value(x) for x in sequence])


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
