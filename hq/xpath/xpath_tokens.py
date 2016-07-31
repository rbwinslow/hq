from hq.xpath.node_test import NodeTest

from .axis import Axis
from .name_test import NameTest
from .xpath_expression_context import XpathExpressionContext


class AxisToken:
    lbp = 20

    def __init__(self, value):
        self.value = value.rstrip(':')

    def __repr__(self):
        return '(axis "{0}")'.format(self.value)

    def led(self, left):
        def axis(document):
            return XpathExpressionContext(Axis[self.value], left(document).nodes)
        return axis


class DoubleSlashToken:
    lbp = 10

    def __repr__(self):
        return '(double-slash)'

    def nud(self):
        def entire_document(document):
            return XpathExpressionContext(axis=Axis.descendant, nodes=[document])
        return entire_document


class EndToken:
    lbp = 0


class NameTestToken:
    lbp = 20

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return '(name_test "{0}")'.format(self.value)

    def led(self, left):
        def name_test(document):
            context = left(document)
            test = NameTest(self.value)
            ragged = [test.apply(context.axis, node, document) for node in context.nodes]
            return XpathExpressionContext(nodes=[item for sublist in ragged for item in sublist])
        return name_test


class NodeTestToken:
    lbp = 20

    def __init__(self, value):
        self.value = value.rstrip('()')

    def __repr__(self):
        return '(node_test "{0}()")'.format(self.value)

    def led(self, left):
        def node_test(document):
            context = left(document)
            test = NodeTest(self.value)
            ragged = [test.apply(context.axis, node, document) for node in context.nodes]
            return XpathExpressionContext(nodes=[item for sublist in ragged for item in sublist])
        return node_test


class SlashToken:
    lbp = 10

    def __init__(self):
        self.right = None

    def __repr__(self):
        return '(slash)'

    def nud(self):
        def root(document):
            return XpathExpressionContext(nodes=[document])
        return root

    def led(self, left):
        def result_set_from_prior_test(document):
            return left(document)
        return result_set_from_prior_test
