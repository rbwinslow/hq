from ..soup_util import object_is_tag

from .xpath_expression_context import *


class AxisToken:
    lbp = 20

    def __init__(self, value):
        self.value = value.rstrip(':')

    def led(self, left):
        def axis(document):
            if self.value == 'child':
                return left(document)
            elif self.value == 'descendant':
                context = left(document)
                if context.view == DOCUMENT_ROOT or context.view == ENTIRE_DOCUMENT:
                    return XpathExpressionContext(ENTIRE_DOCUMENT)
                elif context.view == NODES or context.view == NODES_AND_ALL_DESCENDANTS:
                    return XpathExpressionContext(NODES_AND_ALL_DESCENDANTS, context.nodes)
                else:
                    msg = 'Unhandled context view (#{0}) in AxisToken/descendant case'.format(context.view)
                    raise NotImplementedError(msg)
            elif self.value == 'parent':
                return XpathExpressionContext(PARENTS, left(document).nodes)
            else:
                raise NotImplementedError('Unhandled ')
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
                return XpathExpressionContext(NODES, document(self.value))
            elif context.view == NODES:
                result = []
                for item in context.nodes:
                    if object_is_tag(item):
                        result.extend([child for child in item.children if child.name == self.value])
                return XpathExpressionContext(NODES, result)
            elif context.view == NODES_AND_ALL_DESCENDANTS:
                result = []
                for item in context.nodes:
                    if object_is_tag(item):
                        result.extend(item(self.value))
                return XpathExpressionContext(NODES, result)
            elif context.view == PARENTS:
                result = []
                for item in context.nodes:
                    if object_is_tag(item):
                        parent = item.parent
                        if parent.name == self.value:
                            result.append(parent)
                return XpathExpressionContext(NODES, result)
            else:
                raise NotImplementedError('Unhandled context view (#{0}) in NameTestToken'.format(context.view))
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
