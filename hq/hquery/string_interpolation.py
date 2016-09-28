import re

from hq.hquery.functions.extend_string import join
from hq.hquery.object_type import string_value
from hq.hquery.syntax_error import HquerySyntaxError
from hq.string_util import truncate_string
from hq.verbosity import verbose_print


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
    verbose_print('Parsing interpolated string contents `{0}`'.format(source))
    expressions = []
    clauses = _split_at_embedding_dollars_but_not_dollars_inside_expressions(source)
    expressions.append(lambda: clauses[0])
    for clause in clauses[1:]:
        if clause[0] == '{':
            inside, _, outside = clause[1:].partition('}')
            verbose_print('Parsing embedded expression "{0}"'.format(inside))
            expressions.append(reduce_filters_and_expression(inside, parse_interface))
            expressions.append(lambda: outside)
        else:
            name_match = re.match(r'[_\w][_\w\-]*', clause)
            if name_match is None:
                msg = 'Invalid character "{0}" following "$" in interpolated string'
                raise HquerySyntaxError(msg.format(clause[0]))
            outside_index = name_match.span()[1]
            verbose_print('Parsing variable reference "{0}"'.format(clause[:outside_index]))
            expressions.append(parse_interface.parse_in_new_processor('${0}'.format(clause[:outside_index])))
            expressions.append(lambda: clause[outside_index:])
    return lambda: ''.join([string_value(exp()) for exp in expressions])


def _split_at_embedding_dollars_but_not_dollars_inside_expressions(source):
    result = []
    stitching_together = None
    splits = source.split('$')
    result.append(splits[0])

    for split in splits[1:]:
        if len(split) > 0:
            if stitching_together is None:
                if split[0] != '{' or split.find('}') > 0:
                    result.append(split)
                else:
                    stitching_together = split
            else:
                stitching_together = '{0}${1}'.format(stitching_together, split)
                if split.find('}') >= 0:
                    result.append(stitching_together)
                    stitching_together = None

    return result
