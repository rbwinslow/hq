import re

from hq.hquery.functions.extend_string import join
from hq.hquery.object_type import string_value
from hq.string_util import truncate_string


def _join_filter_link(arguments):
    if arguments is None or len(arguments) == 0:
        delimiter = ''
    else:
        delimiter = arguments[0]

    def construct(eval_fn):
        def evaluate():
            return join(eval_fn(), delimiter)
        return evaluate

    return construct


def _truncate_filter_link(arguments):

    def construct(eval_fn):
        length = int(arguments[0])
        if len(arguments) == 1:
            suffix = ''
        else:
            suffix = arguments[1]
        return lambda: truncate_string(string_value(eval_fn()), length, suffix=suffix)

    return construct


filters = {
    r'j:([^:]*):': _join_filter_link,
    r't:(\d+):([^:]*):': _truncate_filter_link,
}


def reduce_filters_and_expression(remainder, parse_interface, chain=None):
    for pattern in filters:
        match = re.match(pattern, remainder)
        if match is not None:
            filter_constructor = filters[pattern](match.groups())
            remainder = remainder[match.span()[1]:]
            if chain is None:
                return reduce_filters_and_expression(remainder, parse_interface, filter_constructor)
            else:
                return reduce_filters_and_expression(remainder, parse_interface, lambda eval_fn: filter_constructor(chain(eval_fn)))

    eval_fn = parse_interface.parse_in_new_processor(remainder)
    if chain is None:
        return eval_fn
    else:
        return chain(eval_fn)


def parse_interpolated_string(source, parse_interface):
    expressions = []
    clauses = source.split('$')
    expressions.append(lambda: clauses[0])
    for clause in clauses[1:]:
        if clause[0] == '{':
            inside, _, outside = clause[1:].partition('}')
            expressions.append(reduce_filters_and_expression(inside, parse_interface))
            expressions.append(lambda: outside)
        else:
            # parse variable
            pass
    return lambda: ''.join([string_value(exp()) for exp in expressions])
