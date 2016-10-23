from hq.hquery.evaluation_error import HqueryEvaluationError
from hq.hquery.expression_context import get_context_node, peek_context
from hq.hquery.functions.core_boolean import boolean

exports = ('class_', 'even', 'odd')


def class_(*args):
    if len(args) == 1:
        tag = get_context_node()
        name = args[0]
    elif len(args) == 2:
        HqueryEvaluationError.must_be_node_set(args[0])
        tag = args[0][0]
        name = args[1]
    else:
        raise HqueryEvaluationError('class() expects one or two arguments; got {0}'.format(len(args)))

    return boolean(name in tag['class'])


def even():
    return boolean(peek_context().position % 2 == 0)


def odd():
    return boolean(peek_context().position % 2 == 1)
