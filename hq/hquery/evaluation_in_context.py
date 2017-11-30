from hq.hquery.evaluation_error import HqueryEvaluationError
from hq.hquery.expression_context import push_context, pop_context
from hq.hquery.sequences import make_node_set
from hq.soup_util import is_any_node, debug_dump_long_string


def evaluate_across_contexts(node_set, expression_fn):
    HqueryEvaluationError.must_be_node_set(node_set)

    node_set_len = len(node_set)
    ragged = [evaluate_in_context(node, expression_fn, position=index+1, size=node_set_len)
              for index, node in enumerate(node_set)]
    return make_node_set([item for sublist in ragged for item in sublist])


def evaluate_in_context(node, expression_fn, position=1, size=1, preserve_space=None):
    if not is_any_node(node):
        raise HqueryEvaluationError('cannot use {0} "{1}" as context node'.format(type(node),
                                                                                  debug_dump_long_string(str(node))))
    push_context(node, position, size, preserve_space)
    result = expression_fn()
    pop_context()
    return result
