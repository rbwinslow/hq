from hq.soup_util import soup_from_any_tag, is_tag_object
from hq.xpath.node_test import NodeTest

from .axis import Axis
from .name_test import NameTest
from .xpath_expression_context import XpathExpressionContext


class LBP:
    """Left-binding precendence values."""
    (nothing, predicate, location_step, node_test) = range(4)


class AxisToken:
    lbp = LBP.node_test

    def __init__(self, value):
        self.value = value.rstrip(':')

    def __repr__(self):
        return '(axis "{0}")'.format(self.value)

    def led(self, left, expression_fn):
        def axis(context):
            return XpathExpressionContext(axis=Axis[self.value], nodes=left(context).nodes)
        return axis


class ContextNodeToken:
    lbp = LBP.node_test

    def __repr__(self):
        return '(context-node)'

    def led(self, left, expression_fn):
        def context_node(context):
            return left(context)
        return context_node

    def nud(self, expression_fn):
        def context_node(context):
            return context
        return context_node


class DoubleSlashToken:
    lbp = LBP.location_step

    def __repr__(self):
        return '(double-slash)'

    def nud(self, expression_fn):
        def entire_document(context):
            return XpathExpressionContext(axis=Axis.descendant, nodes=[soup_from_any_tag(context.nodes[0])])
        return entire_document


class EndToken:
    lbp = LBP.nothing


class LeftBraceToken:
    lbp = LBP.predicate

    def __repr__(self):
        return '(left-brace)'

    def led(self, left, expression_fn):
        right = expression_fn(self.lbp)
        def start_predicate(context):
            context = left(context)
            filtered = [node for node in context.nodes if len(right(XpathExpressionContext(nodes=[node])).nodes) > 0]
            return XpathExpressionContext(nodes=filtered)
        return start_predicate


class NameTestToken:
    lbp = LBP.node_test

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return '(name-test "{0}")'.format(self.value)

    def led(self, left, expression_fn):
        def in_path_name_test(context):
            context = left(context)
            return self._perform_name_test(context)
        return in_path_name_test

    def nud(self, expression_fn):
        def context_relative_name_test(context):
            return self._perform_name_test(context)
        return context_relative_name_test

    def _perform_name_test(self, context):
        test = NameTest(self.value)
        ragged = [test.apply(context.axis, node) for node in context.nodes]
        return XpathExpressionContext(nodes=[item for sublist in ragged for item in sublist])


class NodeTestToken:
    lbp = LBP.node_test

    def __init__(self, value):
        self.value = value.rstrip('()')

    def __repr__(self):
        return '(node-test "{0}()")'.format(self.value)

    def led(self, left, expression_fn):
        def node_test(context):
            context = left(context)
            test = NodeTest(self.value)
            ragged = [test.apply(context.axis, node) for node in context.nodes]
            return XpathExpressionContext(nodes=[item for sublist in ragged for item in sublist])
        return node_test


class ParentNodeToken:
    lbp = LBP.node_test

    def __repr__(self):
        return '(parent-node)'

    def led(self, left, expression_fn):
        def parent_node(context):
            context = left(context)
            return self._perform_parent_node(context)
        return parent_node

    def nud(self, expression_fn):
        def parent_node(context):
            return self._perform_parent_node(context)
        return parent_node

    def _perform_parent_node(self, context):
        return XpathExpressionContext(nodes=[node.parent for node in context.nodes if is_tag_object(node)])


class RightBraceToken:
    lbp = LBP.predicate

    def __repr__(self):
        return '(right-brace)'

    def led(self, left, expression_fn):
        return left


class SlashToken:
    lbp = LBP.location_step

    def __init__(self):
        self.right = None

    def __repr__(self):
        return '(slash)'

    def led(self, left, expression_fn):
        return left

    def nud(self, expression_fn):
        def root(context):
            return XpathExpressionContext(nodes=[soup_from_any_tag(context.nodes[0])])
        return root
