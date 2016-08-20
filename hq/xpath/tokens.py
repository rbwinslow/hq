from hq.soup_util import soup_from_any_tag
from hq.verbosity import verbose_print
from hq.xpath.function_support import FunctionSupport
from hq.xpath.functions.core_boolean import boolean
from hq.xpath.functions.core_numeric import number
from hq.xpath.node_test import NodeTest
from hq.xpath.object_type import is_node_set, make_node_set, string_value
from hq.xpath.query_error import QueryError

from .axis import Axis
from .expression_context import ExpressionContext
from .name_test import NameTest


function_support = FunctionSupport()


class LBP:
    """Left-binding precendence values."""
    (nothing, predicate, equality_op, add_or_subtract, function_call, location_step, node_test) = range(7)


class Token:
    def __init__(self, parse_interface, value=None):
        self.parse_interface = parse_interface
        self.value = value


class AxisToken(Token):
    lbp = LBP.node_test

    def __repr__(self):
        return '(axis "{0}")'.format(self.value)

    def led(self, left):
        right = self.parse_interface.expression(self.lbp)
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


class CloseParenthesisToken(Token):
    lbp = LBP.function_call

    def __repr__(self):
        return '(close-parenthesis)'


class ContextNodeToken(Token):
    lbp = LBP.node_test

    def __repr__(self):
        return '(context-node)'

    def led(self, left):
        def identity(context):
            result = left(context)
            verbose_print('ContextNodeToken passing along ({0})'.format(result))
            return result
        return identity

    def nud(self):
        def context_node(context):
            verbose_print('ContextNodeToken passing along context node {0}'.format(context.node))
            return make_node_set(context.node)
        return context_node


class DoubleSlashToken(Token):
    lbp = LBP.location_step

    def __repr__(self):
        return '(double-slash)'

    def nud(self):
        right = self.parse_interface.expression(self.lbp)
        def entire_document(context):
            verbose_print('DoubleSlashToken evaluating node test for entire document')
            return right(ExpressionContext(soup_from_any_tag(context.node)), axis=Axis.descendant)
        return entire_document


class EndToken(Token):
    lbp = LBP.nothing


class EqualityOperatorToken(Token):
    lbp = LBP.equality_op

    def __repr__(self):
        return '(relational-operator "{0}")'.format(self.value)

    def led(self, left):
        right = self.parse_interface.expression(self.lbp)

        def evaluate(context):
            verbose_print('EqualityOperatorToken ({0}) evaluation...'.format(self.value), indent_after=True)
            verbose_print('Evaluating left-hand side.', indent_after=True)
            left_value = left(context)
            verbose_print('Evaluating right-hand side.', outdent_before=True, indent_after=True)
            right_value = right(context)

            verbose_print('Comparing values.', outdent_before=True)
            equals = self._eval_equals(left_value, right_value)
            result = equals if self.value == '=' else not equals

            verbose_print('EqualityOperatorToken ({0}) returning {1}'.format(self.value, result), outdent_before=True)
            return result

        return evaluate

    @staticmethod
    def _eval_equals(left_value, right_value):
        if is_node_set(left_value):
            if is_node_set(right_value):
                return EqualityOperatorToken._compare_node_sets(left_value, right_value)
            else:
                raise NotImplementedError('comparison of node sets with other objects not yet implemented')
        elif is_node_set(right_value):
            raise NotImplementedError('comparison of node sets with other objects not yet implemented')
        else:
            return boolean(left_value == right_value)

    @staticmethod
    def _compare_node_sets(left_node_set, right_node_set):
        left_values = set([string_value(node) for node in left_node_set])
        right_values = set([string_value(node) for node in right_node_set])

        msg = 'Comparing two nodes sets (size {0} and {1}).'
        verbose_print(msg.format(len(left_values), len(right_values)), indent_after=True)

        for left_value in left_values:
            if left_value in right_values:
                verbose_print('Found value "{0}" from left-hand node set in right-hand node set'.format(left_value))
                return boolean(True)
        verbose_print('Found no matching nodes between node sets.')
        return boolean(False)


class FunctionCallToken(Token):
    lbp = LBP.function_call

    def __repr__(self):
        return '(function call "{0}")'.format(self.value)

    def nud(self):
        right = self.parse_interface.expression(self.lbp)
        right_paren = self.parse_interface.advance()
        if not isinstance(right_paren, CloseParenthesisToken):
            raise RuntimeError('FunctionCallToken expected right-hand parenthesis after argument(s)')
        def evaluate(context):
            verbose_print('FunctionCallToken evaluating argument list for function "{0}."'.format(self.value))
            arguments = [right(context)]
            verbose_print('FunctionCallToken calling function "{0}" with {1} arguments.'.format(self.value,
                                                                                                len(arguments)))
            return function_support.call_function(self.value, *arguments)
        return evaluate


class LeftBraceToken(Token):
    lbp = LBP.predicate

    def __repr__(self):
        return '(left-brace)'

    def led(self, left):
        right = self.parse_interface.expression(self.lbp)
        def evaluate(context):
            node_set = left(context)
            QueryError.must_be_node_set(node_set)
            verbose_print('LeftBraceToken evaluating predicate for {0} nodes'.format(len(node_set)), indent_after=True)
            result = make_node_set([node for node in node_set if boolean(right(ExpressionContext(node)))])
            verbose_print('LeftBraceToken (predicate) evaluation returning {0} nodes'.format(len(result)),
                          outdent_before=True)
            return result
        return evaluate


class LiteralNumberToken(Token):
    lbp = LBP.nothing

    def __repr__(self):
        return '(literal-number {0})'.format(self.value)

    def nud(self):
        def value(context):
            verbose_print('LiteralNumberToken returning value {0}'.format(self.value))
            return number(self.value)
        return value


class LiteralStringToken(Token):
    lbp = LBP.nothing

    def __repr__(self):
        return '(literal-string "{0}")'.format(self.value)

    def nud(self):
        def value(context):
            verbose_print('LiteralStringToken returning value "{0}"'.format(self.value))
            return self.value
        return value


class NameTestToken(Token):
    lbp = LBP.node_test

    def __repr__(self):
        return '(name-test "{0}")'.format(self.value)

    def led(self, left):
        def name_test(context, axis=Axis.child):
            node_set = left(context)
            QueryError.must_be_node_set(node_set)
            verbose_print('NameTestToken "{0}" evaluating children of {1} node(s)'.format(self.value, len(node_set)))
            return self._evaluate(node_set, axis)
        return name_test

    def nud(self):
        def name_test(context, axis=Axis.child):
            verbose_print('NameTestToken "{0}" evaluating children of context node'.format(self.value))
            return self._evaluate(make_node_set(context.node), axis)
        return name_test

    def _evaluate(self, node_set, axis):
        test = NameTest(self.value)
        ragged = [test.apply(axis, node) for node in node_set]
        result = make_node_set([item for sublist in ragged for item in sublist])
        verbose_print('NameTestToken evaluation produced {0} node(s)'.format(len(result)))
        return result


class NodeTestToken(Token):
    lbp = LBP.node_test

    def __repr__(self):
        return '(node-test "{0}()")'.format(self.value)

    def led(self, left):
        def node_test(context, axis=Axis.child):
            node_set = left(context)
            QueryError.must_be_node_set(node_set)
            verbose_print('NodeTestToken {0}() evaluating children of  {1} node(s)'.format(self.value, len(node_set)))
            return self._evaluate(node_set, axis)
        return node_test

    def nud(self):
        def node_test(context, axis=Axis.child):
            verbose_print('NodeTestToken {0}() evaluating children of context node'.format(self.value))
            return self._evaluate(make_node_set(context.node), axis)
        return node_test

    def _evaluate(self, node_set, axis):
        test = NodeTest(self.value)
        ragged = [test.apply(axis, node) for node in node_set]
        result = make_node_set([item for sublist in ragged for item in sublist])
        verbose_print('NodeTestToken evaluation produced {0} node(s)'.format(len(result)))
        return result


class ParentNodeToken(Token):
    lbp = LBP.node_test

    def __repr__(self):
        return '(parent-node)'

    def led(self, left):
        def parent_node(context):
            node_set = left(context)
            verbose_print('ParentNodeToken returning parent(s) of {0} nodes'.format(len(node_set)))
            return self._perform_parent_node(node_set)
        return parent_node

    def nud(self):
        def parent_node(context):
            verbose_print('ParentNodeToken returning parent of context node')
            return self._perform_parent_node(make_node_set(context.node))
        return parent_node

    def _perform_parent_node(self, node_set):
        QueryError.must_be_node_set(node_set)
        return make_node_set([node.parent for node in node_set])


class PlusOrMinusToken(Token):
    lbp = LBP.add_or_subtract

    def __repr__(self):
        return '(plus)' if self.value == '+' else '(minus)'

    def led(self, left):
        right = self.parse_interface.expression(self.lbp)

        def evaluate(context):
            verbose_print('PlusOrMinusToken ({0}) evaluation...'.format(self.value), indent_after=True)
            verbose_print('Evaluating left-hand side.', indent_after=True)
            left_value = number(left(context))
            verbose_print('Evaluating right-hand side.', outdent_before=True, indent_after=True)
            right_value = number(right(context))

            verbose_print('Calculating.', outdent_before=True)
            result = left_value + right_value if self.value == '+' else left_value - right_value

            verbose_print('PlusOrMinusToken ({0}) returning {1}'.format(self.value, result), outdent_before=True)
            return result

        return evaluate


class RightBraceToken(Token):
    lbp = LBP.predicate

    def __repr__(self):
        return '(right-brace)'

    def led(self, left):
        return left


class SlashToken(Token):
    lbp = LBP.location_step

    def __repr__(self):
        return '(slash)'

    def led(self, left):
        return left

    def nud(self):
        def root(context):
            verbose_print('SlashToken returning document root as start of absolute path')
            return make_node_set(soup_from_any_tag(context.node))
        return root