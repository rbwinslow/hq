import re

from hq.hquery.functions.extend_string import _xpath_flags_to_re_flags, string_join
from hq.hquery.object_type import string_value, is_sequence
from hq.hquery.syntax_error import HquerySyntaxError
from hq.soup_util import debug_dump_long_string
from hq.string_util import truncate_string, html_entity_decode
from hq.verbosity import verbose_print


clauses_pattern = re.compile(r'(\$\{[^\}]+\})|(\$[a-zA-Z_]\w*)|((?:[^\$]+))')


def _join_filter_link(arguments):
    if arguments is None or len(arguments) == 0:
        delimiter = ''
    else:
        delimiter = arguments[0]

    def construct(eval_fn):
        return lambda: string_join(eval_fn(), delimiter)

    return construct


def _regex_replace_filter_link(arguments):
    if arguments is None or len(arguments) < 2:
        msg = 'interpolated string regex replace filter expects three arguments; got {0}'
        raise HquerySyntaxError(msg.format(arguments))

    if len(arguments) == 3:
        flags = _xpath_flags_to_re_flags(arguments[2])
    else:
        flags = 0

    def construct(eval_fn):
        def evaluate():
            value = eval_fn()
            if is_sequence(value):
                return [re.sub(arguments[0], arguments[1], string_value(item), flags=flags) for item in value]
            else:
                return re.sub(arguments[0], arguments[1], string_value(value), flags=flags)
        return evaluate

    return construct


def _truncate_filter_link(arguments):

    def construct(eval_fn):
        length = int(arguments[0])
        if len(arguments) == 1:
            suffix = ''
        else:
            suffix = arguments[1]

        def evaluate():
            value = eval_fn()
            if is_sequence(value):
                return [truncate_string(string_value(item), length, suffix=suffix) for item in value]
            else:
                return truncate_string(string_value(value), length, suffix=suffix)

        return evaluate

    return construct


filters = {
    r'j:([^:]*):': _join_filter_link,
    r'rr:([^:]+):([^:]*):([i]*):': _regex_replace_filter_link,
    r'tru:(\d+):([^:]*):': _truncate_filter_link,
}


def reduce_filters_and_expression(remainder, parse_interface, chain=None):
    for pattern in filters:
        match = re.match(pattern, remainder)
        if match is not None:
            filter_constructor = filters[pattern]([html_entity_decode(arg) for arg in match.groups()])
            remainder = remainder[match.span()[1]:]
            if chain is None:
                return reduce_filters_and_expression(remainder, parse_interface, filter_constructor)
            else:
                return reduce_filters_and_expression(remainder,
                                                     parse_interface,
                                                     lambda eval_fn: filter_constructor(chain(eval_fn)))

    eval_fn = parse_interface.parse_in_new_processor(remainder)
    if chain is None:
        return eval_fn
    else:
        return chain(eval_fn)


def parse_interpolated_string(source, parse_interface):
    verbose_print(u'Parsing interpolated string contents `{0}`'.format(source), indent_after=True)

    expressions = []
    for embedded_expr, embedded_var, literal in clauses_pattern.findall(source):
        if embedded_expr:
            verbose_print(u'Adding embedded expression: {0}'.format(embedded_expr))
            expressions.append(reduce_filters_and_expression(embedded_expr[2:-1], parse_interface))
        elif embedded_var:
            verbose_print('Adding embedded variable reference: {0}'.format(embedded_var))
            expressions.append(parse_interface.parse_in_new_processor(embedded_var))
        else:
            verbose_print(u'Adding literal string contents `{0}`'.format(literal))
            expressions.append(_make_literal_identity_closure(literal))

    def evaluate():
        chunks = [string_value(exp()) for exp in expressions]
        verbose_print(u'Interpolated string evaluation assembling {0} chunks{1}.'.format(
            len(chunks),
            '' if len(chunks) == 0 else u' ("{0}")'.format(u'", "'.join(chunks)))
        )
        return ''.join(chunks)

    verbose_print(
        u'Finished parsing interpolated string `{0}` ({1} chunk(s) found)'.format(debug_dump_long_string(source),
                                                                                  len(expressions)),
        outdent_before=True
    )
    return evaluate


def _make_literal_identity_closure(value):
    return lambda: html_entity_decode(value)
