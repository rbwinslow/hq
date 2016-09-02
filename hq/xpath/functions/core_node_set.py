from hq.xpath.expression_context import peek_context
from hq.xpath.functions.core_numeric import number


exports = ['position']


def position():
    return number(peek_context().position)
