from hq.hquery.expression_context import peek_context
from hq.hquery.functions.core_number import number


exports = ['last', 'position']


def last():
    return number(peek_context().size)


def position():
    return number(peek_context().position)
