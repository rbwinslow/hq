from hq.soup_util import soup_from_any_tag, is_tag_node
from hq.verbosity import verbose_print
from hq.xpath.core_functions import boolean
from hq.xpath.node_test import NodeTest
from hq.xpath.object_type import is_node_set, make_node_set
from hq.xpath.query_error import QueryError

from .axis import Axis
from .name_test import NameTest
from .expression_context import ExpressionContext


class LBP:
    """Left-binding precendence values."""
    (nothing, predicate, equality_op, location_step, node_test) = range(5)


class AxisToken:
    lbp = LBP.node_test

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return '(axis "{0}")'.format(self.value)

    def led(self, left, expression_fn):
        right = expression_fn(self.lbp)
        def node_test(context):
            node_set = left(context)
            QueryError.must_be_node_set(node_set)
            node_count = len(node_set)
            if node_count > 0:
                verbose_print('AxisToken evaluating node test on {0} nodes'.format(node_count))
                ragged = [right(ExpressionContext(node), axis=Axis[self.value]) for node in node_set]
                return make_node_set([item for sublist in ragged for item in sublist])
            else:
                verbose_print('AxisToken doing nothing (empty node set)')
                return make_node_set({})
        return node_test


class ContextNodeToken:
    lbp = LBP.node_test

    def __repr__(self):
        return '(context-node)'

    def led(self, left, expression_fn):
        def identity(context):
            result = left(context)
            verbose_print('ContextNodeToken passing along ({0})'.format(result))
            return result
        return identity

    def nud(self, expression_fn):
        def context_node(context):
            verbose_print('ContextNodeToken passing along context node {0}'.format(context.node))
            return make_node_set(context.node)
        return context_node


class DoubleSlashToken:
    lbp = LBP.location_step

    def __repr__(self):
        return '(double-slash)'

    def nud(self, expression_fn):
        right = expression_fn(self.lbp)
        def entire_document(context):
            verbose_print('DoubleSlashToken evaluating node test for entire document')
            return right(ExpressionContext(soup_from_any_tag(context.node)), axis=Axis.descendant)
        return entire_document


class EndToken:
    lbp = LBP.nothing


class EqualityOperatorToken:
    lbp = LBP.equality_op

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return '(relational-operator "{0}")'.format(self.value)

    def led(self, left, expression_fn):
        right = expression_fn(self.lbp)
        def evaluate(context):
            left_value = left(context)
            verbose_print('EqualityOperatorToken ({0}) evaluating right-hand side'.format(self.value))
            equals = self._eval_equals(left_value, right(context))
            result = equals if self.value == '=' else not equals
            verbose_print('EqualityOperatorToken ({0}) returning {1}'.format(self.value, result))
            return result
        return evaluate

    @staticmethod
    def _eval_equals(left_value, right_value):
        if is_node_set(left_value):
            raise NotImplementedError('node set comparison not yet implemented')
        elif is_node_set(right_value):
            raise NotImplementedError('comparison of node sets with other objects not yet implemented')
        else:
            return left_value == right_value


class LeftBraceToken:
    lbp = LBP.predicate

    def __repr__(self):
        return '(left-brace)'

    def led(self, left, expression_fn):
        right = expression_fn(self.lbp)
        def evaluate(context):
            node_set = left(context)
            QueryError.must_be_node_set(node_set)
            verbose_print('LeftBraceToken evaluating predicate for {0} nodes'.format(len(node_set)))
            return make_node_set([node for node in node_set if boolean(right(ExpressionContext(node)))])
        return evaluate


class LiteralStringToken:
    lbp = LBP.nothing

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return '(string "{0}")'.format(self.value)

    def nud(self, expression_fn):
        def value(context):
            verbose_print('LiteralStringToken returning value "{0}"'.format(self.value))
            return self.value
        return value


class NameTestToken:
    lbp = LBP.node_test

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return '(name-test "{0}")'.format(self.value)

    def led(self, left, expression_fn):
        def name_test(context, axis=Axis.child):
            node_set = left(context)
            QueryError.must_be_node_set(node_set)
            verbose_print('NameTestToken ({0}) evaluating {1} node(s)'.format(self.value, len(node_set)))
            return self._evaluate(node_set, axis)
        return name_test

    def nud(self, expression_fn):
        def name_test(context, axis=Axis.child):
            verbose_print('NameTestToken ({0}) evaluating context node'.format(self.value))
            return self._evaluate(make_node_set(context.node), axis)
        return name_test

    def _evaluate(self, node_set, axis):
        test = NameTest(self.value)
        ragged = [test.apply(axis, node) for node in node_set]
        result = make_node_set([item for sublist in ragged for item in sublist])
        verbose_print('NameTestToken evaluation produced {0} node(s)'.format(len(result)))
        return result


class NodeTestToken:
    lbp = LBP.node_test

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return '(node-test "{0}()")'.format(self.value)

    def led(self, left, expression_fn):
        def node_test(context, axis=Axis.child):
            node_set = left(context)
            QueryError.must_be_node_set(node_set)
            verbose_print('NodeTestToken {0}() evaluating {1} node(s)'.format(self.value, len(node_set)))
            return self._evaluate(node_set, axis)
        return node_test

    def nud(self, expression_fn):
        def node_test(context, axis=Axis.child):
            verbose_print('NodeTestToken {0}() evaluating context node'.format(self.value))
            return self._evaluate(make_node_set(context.node), axis)
        return node_test

    def _evaluate(self, node_set, axis):
        test = NodeTest(self.value)
        ragged = [test.apply(axis, node) for node in node_set]
        result = make_node_set([item for sublist in ragged for item in sublist])
        verbose_print('NodeTestToken evaluation produced {0} node(s)'.format(len(result)))
        return result


class ParentNodeToken:
    lbp = LBP.node_test

    def __repr__(self):
        return '(parent-node)'

    def led(self, left, expression_fn):
        def parent_node(context):
            node_set = left(context)
            verbose_print('ParentNodeToken returning parent(s) of {0} nodes'.format(len(node_set)))
            return self._perform_parent_node(node_set)
        return parent_node

    def nud(self, expression_fn):
        def parent_node(context):
            verbose_print('ParentNodeToken returning parent of context node')
            return self._perform_parent_node(make_node_set(context.node))
        return parent_node

    def _perform_parent_node(self, node_set):
        QueryError.must_be_node_set(node_set)
        return make_node_set([node.parent for node in node_set])


class RightBraceToken:
    lbp = LBP.predicate

    def __repr__(self):
        return '(right-brace)'

    def led(self, left, expression_fn):
        return left


class SlashToken:
    lbp = LBP.location_step

    def __repr__(self):
        return '(slash)'

    def led(self, left, expression_fn):
        return left

    def nud(self, expression_fn):
        def root(context):
            verbose_print('SlashToken returning document root as start of absolute path')
            return make_node_set(soup_from_any_tag(context.node))
        return root
