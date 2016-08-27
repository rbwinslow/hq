from hq.soup_util import soup_from_any_tag, debug_dump_node
from hq.verbosity import verbose_print
from hq.xpath.function_support import FunctionSupport
from hq.xpath.functions.core_boolean import boolean
from hq.xpath.functions.core_numeric import number
from hq.xpath.node_test import NodeTest
from hq.xpath.object_type import is_node_set, make_node_set, string_value, object_type_name
from hq.xpath.query_error import QueryError
from hq.xpath.equality_operators import equals, not_equals

from .axis import Axis
from .expression_context import ExpressionContext
from .name_test import NameTest


function_support = FunctionSupport()


class LBP:
    """Left-binding precendence values."""
    (nothing, predicate, equality_op, add_or_subtract, mult_or_div, function_call, location_step, node_test) = range(8)


class Token(object):
    def __init__(self, parse_interface, value=None, **kwargs):
        self.parse_interface = parse_interface
        self.value = value


class AddOrSubtractOperatorToken(Token):
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


class MultiplyOperatorToken(Token):
    lbp = LBP.mult_or_div

    def __repr__(self):
        return '(times)'

    def led(self, left):
        right = self.parse_interface.expression(self.lbp)

        def evaluate(context):
            verbose_print('AsteriskToken ({0}) evaluation...'.format(self.value), indent_after=True)
            verbose_print('Evaluating left-hand side.', indent_after=True)
            left_value = number(left(context))
            verbose_print('Evaluating right-hand side.', outdent_before=True, indent_after=True)
            right_value = number(right(context))

            verbose_print('Calculating.', outdent_before=True)
            result = left_value * right_value

            verbose_print('AsteriskToken ({0}) returning {1}'.format(self.value, result), outdent_before=True)
            return result

        return evaluate


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


class CommaToken(Token):
    lbp = LBP.function_call

    def __repr__(self):
        return '(comma)'


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


class DivOrModOperatorToken(Token):
    lbp = LBP.mult_or_div

    def __repr__(self):
        return '(operator "{0}")'.format(self.value)

    def led(self, left):
        right = self.parse_interface.expression(self.lbp)

        def evaluate(context):
            verbose_print('DivOrModOperatorToken ({0}) evaluation...'.format(self.value), indent_after=True)
            verbose_print('Evaluating left-hand side.', indent_after=True)
            left_value = number(left(context))
            verbose_print('Evaluating right-hand side.', outdent_before=True, indent_after=True)
            right_value = number(right(context))

            verbose_print('Calculating.', outdent_before=True)
            result = left_value / right_value if self.value == 'div' else left_value % right_value

            verbose_print('DivOrModOperatorToken ({0}) returning {1}'.format(self.value, result), outdent_before=True)
            return result

        return evaluate


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
        return '(equality-operator "{0}")'.format(self.value)

    def led(self, left):
        right = self.parse_interface.expression(self.lbp)

        def evaluate(context):
            verbose_print('EqualityOperatorToken ({0}) evaluation...'.format(self.value), indent_after=True)
            verbose_print('Evaluating left-hand side.', indent_after=True)
            left_value = left(context)
            verbose_print('Evaluating right-hand side.', outdent_before=True, indent_after=True)
            right_value = right(context)

            verbose_print('Comparing values.', outdent_before=True)
            result = equals(left_value, right_value) if self.value == '=' else not_equals(left_value, right_value)

            verbose_print('EqualityOperatorToken ({0}) returning {1}'.format(self.value, result), outdent_before=True)
            return result

        return evaluate


class FunctionCallToken(Token):
    lbp = LBP.function_call

    def __repr__(self):
        return '(function call "{0}")'.format(self.value)

    def nud(self):
        arg_generators = []

        while (not isinstance(self.parse_interface.peek(), CloseParenthesisToken)):
            arg_generators.append(self.parse_interface.expression(self.lbp))
            if isinstance(self.parse_interface.peek(), CommaToken):
                self.parse_interface.advance()

        right_paren = self.parse_interface.advance()
        if not isinstance(right_paren, CloseParenthesisToken):
            raise RuntimeError('FunctionCallToken expected right-hand parenthesis after argument(s)')

        def evaluate(context):
            verbose_print('FunctionCallToken evaluating argument list for function "{0}."'.format(self.value))
            arguments = [gen(context) for gen in arg_generators]
            arg_types = ','.join(object_type_name(arg) for arg in arguments)
            verbose_print('FunctionCallToken calling {0}({1}).'.format(self.value, arg_types))
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

    def __init__(self, parse_interface, value, **kwargs):
        super(LiteralStringToken, self).__init__(parse_interface, value[1:-1], **kwargs)

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
            msg_format = 'NameTestToken "{0}" evaluating children of context node {1}'
            verbose_print(msg_format.format(self.value, debug_dump_node(context.node)))
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
            verbose_print('NodeTestToken {0}() evaluating children of {1} node(s)'.format(self.value, len(node_set)))
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
