from hq.soup_util import soup_from_any_tag, debug_dump_node, preorder_traverse_node_tree, debug_dump_long_string
from hq.verbosity import verbose_print
from hq.xpath.equality_operators import equals, not_equals
from hq.xpath.function_support import FunctionSupport
from hq.xpath.functions.core_boolean import boolean
from hq.xpath.functions.core_numeric import number
from hq.xpath.node_test import NodeTest
from hq.xpath.object_type import make_node_set, object_type_name
from hq.xpath.query_error import QueryError

from .axis import Axis
from .expression_context import ExpressionContext

function_support = FunctionSupport()


class LBP:
    """Left-binding precendence values."""
    (nothing, predicate, equality_op, add_or_subtract, mult_or_div, function_call, location_step, node_test) = range(8)


class Token(object):
    def __init__(self, parse_interface, value=None, **kwargs):
        self.parse_interface = parse_interface
        self.value = value

    def gab(self, msg, **kwargs):
        verbose_print('{0} {1}'.format(repr(self), msg), **kwargs)


class AddOrSubtractOperatorToken(Token):
    lbp = LBP.add_or_subtract

    def __repr__(self):
        return '(plus)' if self.value == '+' else '(minus)'

    def led(self, left):
        right = self.parse_interface.expression(self.lbp)

        def evaluate(context):
            self.gab('({0}) evaluation...'.format(self.value), indent_after=True)
            self.gab('Evaluating left-hand side.', indent_after=True)
            left_value = number(left(context))
            self.gab('Evaluating right-hand side.', outdent_before=True, indent_after=True)
            right_value = number(right(context))

            self.gab('Calculating.', outdent_before=True)
            result = left_value + right_value if self.value == '+' else left_value - right_value

            self.gab('({0}) returning {1}'.format(self.value, result), outdent_before=True)
            return result

        return evaluate


class AxisToken(Token):
    lbp = LBP.node_test

    def __init__(self, parse_interface, value, **kwargs):
        super(AxisToken, self).__init__(parse_interface, value if value != '@' else 'attribute', **kwargs)

    def __repr__(self):
        return '(axis "{0}")'.format(self.value)

    def led(self, left=None):
        right = self.parse_interface.expression(self.lbp)
        def node_test(context):
            if left is None:
                node_set = make_node_set(context.node)
            else:
                node_set = left(context)
            QueryError.must_be_node_set(node_set)
            node_count = len(node_set)
            if node_count > 0:
                self.gab('evaluating node test on {0} nodes'.format(node_count))
                ragged = [right(ExpressionContext(node), axis=Axis[self.value.replace('-', '_')]) for node in node_set]
                return make_node_set([item for sublist in ragged for item in sublist])
            else:
                self.gab('doing nothing (empty node set)')
                return make_node_set({})
        return node_test

    def nud(self):
        return self.led()


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
            self.gab('passing along ({0})'.format(result))
            return result
        return identity

    def nud(self):
        def context_node(context):
            self.gab('passing along context node {0}'.format(context.node))
            return make_node_set(context.node)
        return context_node


class DivOrModOperatorToken(Token):
    lbp = LBP.mult_or_div

    def __repr__(self):
        return '(operator "{0}")'.format(self.value)

    def led(self, left):
        right = self.parse_interface.expression(self.lbp)

        def evaluate(context):
            self.gab('({0}) evaluation...'.format(self.value), indent_after=True)
            self.gab('Evaluating left-hand side.', indent_after=True)
            left_value = number(left(context))
            self.gab('Evaluating right-hand side.', outdent_before=True, indent_after=True)
            right_value = number(right(context))

            self.gab('Calculating.', outdent_before=True)
            result = left_value / right_value if self.value == 'div' else left_value % right_value

            self.gab('({0}) returning {1}'.format(self.value, result), outdent_before=True)
            return result

        return evaluate


class DoubleSlashToken(Token):
    lbp = LBP.location_step

    def __repr__(self):
        return '(double-slash)'

    def led(self, left):
        right = self.parse_interface.expression(self.lbp)

        def evaluate(context):
            node_set = left(context)
            self.gab('iterating over {0} nodes from path so far.'.format(len(node_set)), indent_after=True)
            msg_format = 'evaluating remainder of path for node "{0}" and all of its descendants.'
            results = []
            for node in node_set:
                self.gab(msg_format.format(debug_dump_node(node)))
                preorder_traverse_node_tree(node, lambda n: results.extend(right(ExpressionContext(n))))
            results = make_node_set(results)
            self.gab('evaluation finished; returning {0} nodes.'.format(len(results)), outdent_before=True)
            return results

        return evaluate

    def nud(self):
        right = self.parse_interface.expression(self.lbp)

        def evaluate(context):
            msg_format = 'evaluating remainder of path for context node "{0}" and all of its descendants.'
            self.gab(msg_format.format(context.node.name))
            results = []
            preorder_traverse_node_tree(context.node, lambda n: results.extend(right(ExpressionContext(n))))
            return make_node_set(results)

        return evaluate


class EndToken(Token):
    lbp = LBP.nothing


class EqualityOperatorToken(Token):
    lbp = LBP.equality_op

    def __repr__(self):
        return '(equality-operator "{0}")'.format(self.value)

    def led(self, left):
        right = self.parse_interface.expression(self.lbp)

        def evaluate(context):
            self.gab('({0}) evaluation...'.format(self.value), indent_after=True)
            self.gab('Evaluating left-hand side.', indent_after=True)
            left_value = left(context)
            self.gab('Evaluating right-hand side.', outdent_before=True, indent_after=True)
            right_value = right(context)

            self.gab('Comparing values.', outdent_before=True)
            result = equals(left_value, right_value) if self.value == '=' else not_equals(left_value, right_value)

            self.gab('({0}) returning {1}'.format(self.value, result), outdent_before=True)
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
            self.gab('evaluating argument list for function "{0}."'.format(self.value))
            arguments = [gen(context) for gen in arg_generators]
            arg_types = ','.join(object_type_name(arg) for arg in arguments)
            self.gab('calling {0}({1}).'.format(self.value, arg_types))
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
            self.gab('evaluating predicate for {0} nodes'.format(len(node_set)), indent_after=True)
            result = make_node_set([node for node in node_set if boolean(right(ExpressionContext(node)))])
            self.gab('(predicate) evaluation returning {0} nodes'.format(len(result)),
                          outdent_before=True)
            return result
        return evaluate


class LiteralNumberToken(Token):
    lbp = LBP.nothing

    def __repr__(self):
        return '(literal-number {0})'.format(self.value)

    def nud(self):
        def value(context):
            self.gab('returning value {0}'.format(self.value))
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
            self.gab('returning value "{0}"'.format(self.value))
            return self.value
        return value


class MultiplyOperatorToken(Token):
    lbp = LBP.mult_or_div

    def __repr__(self):
        return '(times)'

    def led(self, left):
        right = self.parse_interface.expression(self.lbp)

        def evaluate(context):
            self.gab('evaluating left-hand side.', indent_after=True)
            left_value = number(left(context))
            self.gab('evaluating right-hand side.', outdent_before=True, indent_after=True)
            right_value = number(right(context))

            result = left_value * right_value
            self.gab('({0}) returning {1}'.format(self.value, result), outdent_before=True)
            return result

        return evaluate


class NameTestToken(Token):
    lbp = LBP.node_test

    def __repr__(self):
        return '(name-test "{0}")'.format(self.value)

    def led(self, left):
        def name_test(context, axis=Axis.child):
            node_set = left(context)
            QueryError.must_be_node_set(node_set)
            self.gab('evaluating {0} from {1} node(s)'.format(axis, len(node_set)))
            return self._evaluate(node_set, axis)
        return name_test

    def nud(self):
        def name_test(context, axis=Axis.child):
            msg_format = 'evaluating {0} from context node {1}'
            self.gab(msg_format.format(axis, debug_dump_node(context.node)))
            return self._evaluate(make_node_set(context.node), axis)
        return name_test

    def _evaluate(self, node_set, axis):
        test = NodeTest(self.value, name_test=True)
        ragged = [test.apply(axis, node) for node in node_set]
        result = make_node_set([item for sublist in ragged for item in sublist])
        self.gab('evaluation produced {0} node(s)'.format(len(result)))
        return result


class NodeTestToken(Token):
    lbp = LBP.node_test

    def __repr__(self):
        return '(node-test "{0}")'.format(self._dump_value())

    def led(self, left):
        def node_test(context, axis=Axis.child):
            node_set = left(context)
            QueryError.must_be_node_set(node_set)
            self.gab('evaluating {0} from {1} node(s)'.format(axis, len(node_set)))
            return self._evaluate(node_set, axis)
        return node_test

    def nud(self):
        def node_test(context, axis=Axis.child):
            self.gab('evaluating {0} from context node {1}'.format(axis, debug_dump_long_string(str(context.node))))
            return self._evaluate(make_node_set(context.node), axis)
        return node_test

    def _dump_value(self):
        return '{0}{1}'.format(self.value, '()' if self.value != '*' else '')

    def _evaluate(self, node_set, axis):
        test = NodeTest(self.value)
        ragged = [test.apply(axis, node) for node in node_set]
        result = make_node_set([item for sublist in ragged for item in sublist])
        self.gab('evaluation produced {0} node(s)'.format(len(result)))
        return result


class ParentNodeToken(Token):
    lbp = LBP.node_test

    def __repr__(self):
        return '(parent-node)'

    def led(self, left):
        def parent_node(context):
            node_set = left(context)
            self.gab('returning parent(s) of {0} nodes'.format(len(node_set)))
            return self._perform_parent_node(node_set)
        return parent_node

    def nud(self):
        def parent_node(context):
            self.gab('returning parent of context node')
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
            self.gab('returning document root as start of absolute path')
            return make_node_set(soup_from_any_tag(context.node))
        return root
