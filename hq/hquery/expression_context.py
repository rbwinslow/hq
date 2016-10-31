from hq.verbosity import verbose_print
from ..soup_util import debug_dump_node

context_stack = []


class ExpressionContext:

    def __init__(self, node, position=1, size=1, preserve_space=None):
        self.node = node
        self.position = position
        self.size = size
        if preserve_space is not None:
            self.preserve_space = preserve_space
        else:
            try:
                self.preserve_space = peek_context().preserve_space
            except ExpressionStackEmptyError:
                self.preserve_space = False

    def __str__(self):
        return 'context(node={0})'.format(str(self.node))


class ExpressionStackEmptyError(RuntimeError):
    pass



def get_context_node():
    return peek_context().node


def peek_context():
    try:
        return context_stack[-1]
    except IndexError:
        raise ExpressionStackEmptyError('tried to peek while expression stack was empty')


def pop_context():
    result = context_stack.pop()
    msg = u'Popping (node={0}, position={1}, size={2} off of context stack.'
    verbose_print(lambda: msg.format(debug_dump_node(result.node), result.position, result.size))
    return result


def push_context(node, position=1, size=1, preserve_space=None):
    msg = u'Pushing (node={0}, position={1}, size={2} on context stack.'
    verbose_print(lambda: msg.format(debug_dump_node(node), position, size))
    context_stack.append(ExpressionContext(node=node, position=position, size=size, preserve_space=preserve_space))
