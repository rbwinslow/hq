from hq.hquery.evaluation_error import HqueryEvaluationError
from hq.hquery.expression_context import peek_context
from hq.hquery.functions.core_number import number


exports = ['count', 'last', 'position']


def count(nodes):
    HqueryEvaluationError.must_be_node_set(nodes)
    return number(len(nodes))


def last():
    return number(peek_context().size)


def position():
    return number(peek_context().position)
