
from .xpath_expression_context import *


class Axis:
    lbp = 20

    def __init__(self, value):
        self.value = value.rstrip(':')

    def led(self, left):
        def axis(document):
            if self.value == 'child':
                return left(document)
        return axis


class DoubleSlashToken:
    lbp = 10

    def __repr__(self):
        return '(double-slash)'

    def nud(self):
        def entire_document(document):
            return XpathExpressionContext(ENTIRE_DOCUMENT)
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
            if context.view == DOCUMENT_ROOT:
                return XpathExpressionContext(NODES, [child for child in document.children if child.name == self.value])
            elif context.view == ENTIRE_DOCUMENT:
                return XpathExpressionContext(NODES, document.find_all(self.value))
            elif context.view == NODES:
                result = []
                for item in context.nodes:
                    if str(type(item)).find('.Tag') > 0:
                        result.extend([child for child in item.children if child.name == self.value])
                return XpathExpressionContext(NODES, result)
        return name_test


class SlashToken:
    lbp = 10

    def __init__(self):
        self.right = None

    def __repr__(self):
        return '(slash)'

    def nud(self):
        def root(document):
            return XpathExpressionContext(DOCUMENT_ROOT)
        return root

    def led(self, left):
        def result_set_from_prior_test(document):
            return left(document)
        return result_set_from_prior_test
