from hq.soup_util import soup_from_any_tag, debug_dump_node, preorder_traverse_node_tree, debug_dump_long_string
from hq.verbosity import verbose_print
from hq.xpath.equality_operators import equals, not_equals
from hq.xpath.function_support import FunctionSupport
from hq.xpath.functions.core_boolean import boolean
from hq.xpath.functions.core_number import number
from hq.xpath.node_test import NodeTest
from hq.xpath.object_type import make_node_set, object_type_name
from hq.xpath.query_error import XpathQueryError
from hq.xpath.relational_operators import RelationalOperator
from hq.xpath.syntax_error import XpathSyntaxError

from .axis import Axis
from .expression_context import peek_context, evaluate_across_contexts, evaluate_in_context

function_support = FunctionSupport()


class LBP:
    """Left-binding precendence values."""
    (
        nothing, predicate, relational_op, add_or_subtract, mult_or_div, prefix_op, function_call, location_step,
        node_test
    ) = range(9)



class Token(object):

    def __init__(self, parse_interface, value=None, **kwargs):
        self.parse_interface = parse_interface
        self.value = value


    def _default_node_set_to_context_and_describe(self, node_set_or_none):
        if node_set_or_none is None:
            node_set_or_none = [peek_context().node]
            description = 'context node {0}'.format(debug_dump_node(node_set_or_none[0]))
        else:
            XpathQueryError.must_be_node_set(node_set_or_none)
            description = '{0} node(s)'.format(len(node_set_or_none))
        return node_set_or_none, description


    def _evaluate_binary_operands(self,
                                  left_generator,
                                  right_generator,
                                  constructor=lambda v: v,
                                  type_name='xpath object'):
        try:
            self._gab('{0} evaluation...'.format(self), indent_after=True)
            self._gab('evaluating left-hand side.', indent_after=True)
            left_value = constructor(left_generator())
            self._gab('evaluating right-hand side.', outdent_before=True, indent_after=True)
            right_value = constructor(right_generator())
            self._gab('operand evaluation complete', outdent_before=True)
            self._gab('evaluating expression {0} {1} {2}'.format(left_value, self, right_value), outdent_before=True)
            return left_value, right_value
        except TypeError:
            raise XpathSyntaxError('{0} evaluated against a non-{1} operand'.format(self, type_name))


    def _evaluate_unary_operand(self, operand_generator, constructor=lambda v: v, type_name='xpath object'):
        try:
            self._gab('evaluating operand.', indent_after=True)
            operand_value = constructor(operand_generator())
            self._gab('operand evaluation complete', outdent_before=True)
            return operand_value
        except TypeError:
            raise XpathSyntaxError('{0} evaluated against a non-{1} operand'.format(self, type_name))


    def _gab(self, msg, **kwargs):
        verbose_print('{0} {1}'.format(self, msg), **kwargs)



class AddOrSubtractOperatorToken(Token):
    lbp = LBP.add_or_subtract

    def __str__(self):
        return '(plus)' if self.value == '+' else '(minus)'

    def led(self, left):
        right = self.parse_interface.expression(self.lbp)

        def evaluate():
            left_value, right_value = self._evaluate_binary_operands(left, right, constructor=number, type_name='number')
            result = left_value + right_value if self.value == '+' else left_value - right_value
            self._gab('{0} returning {1}'.format(self, result))
            return result

        return evaluate

    def nud(self):
        if self.value != '-':
            raise XpathSyntaxError('unexpected {0} at beginning of an expression')

        right = self.parse_interface.expression(LBP.prefix_op)

        def evaluate():
            right_value = self._evaluate_unary_operand(right, constructor=number, type_name='number')
            result = -right_value
            self._gab('{0} returning {1}'.format(self, result))
            return result

        return evaluate


class AxisToken(Token):
    lbp = LBP.node_test

    def __init__(self, parse_interface, value, **kwargs):
        super(AxisToken, self).__init__(parse_interface, value if value != '@' else 'attribute', **kwargs)

    def __str__(self):
        return '(axis "{0}")'.format(self.value)

    def led(self, left=None):
        right = self.parse_interface.expression(self.lbp)

        def node_test():
            return evaluate_across_contexts(left(), right, axis=Axis[self.value.replace('-', '_')])

        return node_test

    def nud(self):
        right = self.parse_interface.expression(self.lbp)

        def node_test():
            self._gab('evaluating node test on context node {0}'.format(debug_dump_node(peek_context().node)))
            return right(axis=Axis[self.value.replace('-', '_')])

        return node_test



class CloseParenthesisToken(Token):
    lbp = LBP.nothing

    def __str__(self):
        return '(close-parenthesis)'



class CommaToken(Token):
    lbp = LBP.nothing

    def __str__(self):
        return '(comma)'



class ContextNodeToken(Token):
    lbp = LBP.node_test

    def __str__(self):
        return '(context-node)'

    def led(self, left):

        def identity():
            result = left()
            self._gab('passing along {0}'.format(result))
            return result

        return identity

    def nud(self):

        def context_node():
            context_node = peek_context().node
            self._gab('returning node set containing context node {0}'.format(context_node))
            return make_node_set(context_node)

        return context_node



class DivOrModOperatorToken(Token):
    lbp = LBP.mult_or_div

    def __str__(self):
        return '(operator "{0}")'.format(self.value)

    def led(self, left):
        right = self.parse_interface.expression(self.lbp)

        def evaluate():
            left_value, right_value = self._evaluate_binary_operands(left, right, constructor=number, type_name='number')
            result = left_value / right_value if self.value == 'div' else left_value % right_value
            self._gab('{0} returning {1}'.format(self, result))
            return result

        return evaluate



class DoubleSlashToken(Token):
    lbp = LBP.location_step
    evaluating_message = 'evaluating remainder of path for node "{0}" and all of its descendants.'

    def __str__(self):
        return '(double-slash)'

    def led(self, left):
        right = self.parse_interface.expression(self.lbp)

        def evaluate():
            return self._evaluate(right, node_set=left())

        return evaluate

    def nud(self):
        right = self.parse_interface.expression(self.lbp)

        def evaluate():
            return self._evaluate(right)

        return evaluate

    def _evaluate(self, expression_fn, node_set=None):
        node_set, input_desc = self._default_node_set_to_context_and_describe(node_set)
        self._gab('evaluating for {0}'.format(input_desc), indent_after=True)

        results = []
        for node in node_set:
            self._gab(self.evaluating_message.format(debug_dump_node(node)))
            preorder_traverse_node_tree(node, lambda n: results.extend(evaluate_in_context(n, expression_fn)))
        results = make_node_set(results)

        self._gab('evaluation finished; returning {0} nodes.'.format(len(results)), outdent_before=True)
        return results



class EndToken(Token):
    lbp = LBP.nothing



class EqualityOperatorToken(Token):
    lbp = LBP.relational_op

    def __str__(self):
        return '(equality-operator "{0}")'.format(self.value)

    def led(self, left):
        right = self.parse_interface.expression(self.lbp)

        def evaluate():
            left_value, right_value = self._evaluate_binary_operands(left, right)
            result = equals(left_value, right_value) if self.value == '=' else not_equals(left_value, right_value)
            self._gab('{0} returning {1}'.format(self, result))
            return result

        return evaluate



class FunctionCallToken(Token):
    lbp = LBP.function_call

    def __str__(self):
        return '(function call "{0}")'.format(self.value)

    def nud(self):
        arg_generators = []

        while (not isinstance(self.parse_interface.peek(), CloseParenthesisToken)):
            arg_generators.append(self.parse_interface.expression(LBP.nothing))
            self.parse_interface.advance_if(CommaToken)

        self.parse_interface.advance(CloseParenthesisToken)

        def evaluate():
            self._gab('evaluating argument list for function "{0}."'.format(self.value))
            arguments = [gen() for gen in arg_generators]
            arg_types = ','.join(object_type_name(arg) for arg in arguments)
            self._gab('calling {0}({1}).'.format(self.value, arg_types))
            return function_support.call_function(self.value, *arguments)

        return evaluate



class LeftBraceToken(Token):
    lbp = LBP.predicate

    def __str__(self):
        return '(left-brace)'

    def led(self, left):
        right = self.parse_interface.expression(self.lbp)

        def context_node_if_selected():
            context_node = peek_context().node
            return [context_node] if boolean(right()) else []

        def evaluate():
            node_set = left()
            self._gab('evaluating predicate for {0} nodes'.format(len(node_set)), indent_after=True)

            result = evaluate_across_contexts(node_set, context_node_if_selected)
            self._gab('evaluation returning {0} nodes'.format(len(result)), outdent_before=True)
            return result

        return evaluate



class LiteralNumberToken(Token):
    lbp = LBP.nothing

    def __str__(self):
        return '(literal-number {0})'.format(self.value)

    def nud(self):
        return lambda: number(self.value)



class LiteralStringToken(Token):
    lbp = LBP.nothing

    def __init__(self, parse_interface, value, **kwargs):
        super(LiteralStringToken, self).__init__(parse_interface, value[1:-1], **kwargs)

    def __str__(self):
        return '(literal-string "{0}")'.format(self.value)

    def nud(self):
        return lambda: self.value



class MultiplyOperatorToken(Token):
    lbp = LBP.mult_or_div

    def __str__(self):
        return '(times)'

    def led(self, left):
        right = self.parse_interface.expression(self.lbp)

        def evaluate():
            left_value, right_value = self._evaluate_binary_operands(left, right, constructor=number, type_name='number')
            result = left_value * right_value
            self._gab('{0} returning {1}'.format(self, result))
            return result

        return evaluate



class NameTestToken(Token):
    lbp = LBP.node_test

    def __init__(self, *args, **kwargs):
        super(NameTestToken, self).__init__(*args, **kwargs)
        self.test = NodeTest(self.value, name_test=True)

    def __str__(self):
        return '(name-test "{0}")'.format(self.value)

    def led(self, left):

        def name_test(axis=Axis.child):
            node_set = left()
            XpathQueryError.must_be_node_set(node_set)
            return self._evaluate(axis, node_set)

        return name_test

    def nud(self):

        def name_test(axis=Axis.child):
            return self._evaluate(axis)

        return name_test

    def _evaluate(self, axis, node_set=None):
        node_set, input_desc = self._default_node_set_to_context_and_describe(node_set)
        self._gab('evaluating {0}::{1} from {2}'.format(axis, self.value, input_desc))

        result = evaluate_across_contexts(node_set, lambda: make_node_set(self.test.apply(axis, peek_context().node)))
        self._gab('evaluation produced {0} node(s)'.format(len(result)))
        return result



class NodeTestToken(Token):
    lbp = LBP.node_test

    def __init__(self, *args, **kwargs):
        super(NodeTestToken, self).__init__(*args, **kwargs)
        self.test = NodeTest(self.value)

    def __str__(self):
        return '(node-test "{0}")'.format(self._dump_value())

    def led(self, left):

        def node_test(axis=Axis.child):
            node_set = left()
            XpathQueryError.must_be_node_set(node_set)
            return self._evaluate(axis, node_set)

        return node_test

    def nud(self):

        def node_test(axis=Axis.child):
            return self._evaluate(axis)

        return node_test

    def _dump_value(self):
        return '{0}{1}'.format(self.value, '()' if self.value != '*' else '')

    def _evaluate(self, axis, node_set=None):
        node_set, input_desc = self._default_node_set_to_context_and_describe(node_set)
        self._gab('evaluating {0}::{1} from {2}'.format(axis, self._dump_value(), input_desc))

        result = evaluate_across_contexts(node_set,
                                          lambda: make_node_set(self.test.apply(axis, peek_context().node)))
        self._gab('evaluation produced {0} node(s)'.format(len(result)))
        return result



class ParentNodeToken(Token):
    lbp = LBP.node_test

    def __str__(self):
        return '(parent-node)'

    def led(self, left):
        def parent_node():
            return self._evaluate(left())
        return parent_node

    def nud(self):
        def parent_node():
            return self._evaluate()
        return parent_node

    def _evaluate(self, node_set=None):
        node_set, from_what = self._default_node_set_to_context_and_describe(node_set)
        self._gab('returning parent(s) of {0}'.format(from_what))
        return make_node_set([node.parent for node in node_set])



class RelationalOperatorToken(Token):
    lbp = LBP.relational_op

    def __str__(self):
        return '(operator {0})'.format(RelationalOperator(self.value).name)

    def led(self, left):
        right = self.parse_interface.expression(self.lbp)

        def evaluate():
            left_value, right_value = self._evaluate_binary_operands(left, right)
            result = RelationalOperator(self.value).evaluate(left_value, right_value)
            self._gab('returning {1}'.format(self, result))
            return result

        return evaluate



class RightBraceToken(Token):
    lbp = LBP.predicate

    def __str__(self):
        return '(right-brace)'

    def led(self, left):
        return left



class SlashToken(Token):
    lbp = LBP.location_step

    def __str__(self):
        return '(slash)'

    def led(self, left):
        return left

    def nud(self):
        def root():
            self._gab('returning document root as start of absolute path')
            return make_node_set(soup_from_any_tag(peek_context().node))
        return root
