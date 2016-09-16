from hq.soup_util import is_any_node, debug_dump_long_string, debug_dump_node
from hq.verbosity import verbose_print
from hq.xpath.object_type import make_node_set
from hq.xpath.query_error import XpathQueryError

context_stack = []


class ExpressionContext:
    def __init__(self, node, position=1, size=1):
        self.node = node
        self.position = position
        self.size = size

    def __str__(self):
        return 'context(node={0})'.format(str(self.node))


def evaluate_across_contexts(node_set, expression_fn):
    XpathQueryError.must_be_node_set(node_set)

    node_set_len = len(node_set)
    ragged = [evaluate_in_context(node, expression_fn, position=index+1, size=node_set_len)
              for index, node in enumerate(node_set)]
    return make_node_set([item for sublist in ragged for item in sublist])


def evaluate_in_context(node, expression_fn, position=1, size=1):
    if not is_any_node(node):
        raise XpathQueryError('cannot use {0} "{1}" as context node'.format(type(node),
                                                                            debug_dump_long_string(str(node))))
    push_context(node, position, size)
    result = expression_fn()
    pop_context()
    return result


def get_context_node():
    return peek_context().node


def peek_context():
    return context_stack[-1]


def pop_context():
    result = context_stack.pop()
    verbose_print(u'Popping (node={0}, position={1}, size={2} off of context stack.'.format(debug_dump_node(result.node),
                                                                                            result.position,
                                                                                            result.size))
    return result


def push_context(node, position=1, size=1):
    verbose_print(u'Pushing (node={0}, position={1}, size={2} on context stack.'.format(debug_dump_node(node),
                                                                                        position,
                                                                                        size))
    context_stack.append(ExpressionContext(node=node, position=position, size=size))
