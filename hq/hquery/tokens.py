from hq.soup_util import soup_from_any_tag, debug_dump_node
from hq.verbosity import verbose_print
from hq.hquery.equality_operators import equals, not_equals
from hq.hquery.function_support import FunctionSupport
from hq.hquery.functions.core_boolean import boolean
from hq.hquery.functions.core_number import number
from hq.hquery.node_test import NodeTest
from hq.hquery.object_type import make_node_set, object_type_name, string_value
from hq.hquery.evaluation_error import HqueryEvaluationError
from hq.hquery.relational_operators import RelationalOperator
from hq.hquery.syntax_error import HquerySyntaxError

from .axis import Axis
from .expression_context import get_context_node

function_support = FunctionSupport()


class LBP:
    """Left-binding precendence values."""
    (
        nothing, union, predicate, or_op, and_op, equality_op, relational_op, add_or_subtract, mult_or_div, prefix_op,
        function_call, location_step, node_test, parenthesized_expr
    ) = range(14)



class Token(object):

    def __init__(self, parse_interface, value=None, **kwargs):
        self.parse_interface = parse_interface
        self.value = value


    def _use_node_set_or_default_to_context_if_none(self, node_set_or_none):
        if node_set_or_none is None:
            node_set_or_none = [get_context_node()]
            description = 'context node {0}'.format(debug_dump_node(node_set_or_none[0]))
        else:
            HqueryEvaluationError.must_be_node_set(node_set_or_none)
            description = '{0} node(s)'.format(len(node_set_or_none))
        return node_set_or_none, description


    def _evaluate_binary_operands(self,
                                  left_generator,
                                  right_generator,
                                  constructor=lambda v: v,
                                  type_name='xpath object'):
        try:
            self._gab('operator evaluation...', indent_after=True)
            self._gab('evaluating left-hand side.', indent_after=True)
            left_value = constructor(left_generator())
            self._gab('evaluating right-hand side.', outdent_before=True, indent_after=True)
            right_value = constructor(right_generator())
            self._gab('operand evaluation complete', outdent_before=True)
            self._gab('evaluating expression {0} {1} {2}'.format(left_value, self, right_value), outdent_before=True)
            return left_value, right_value
        except TypeError:
            raise HquerySyntaxError('evaluated against a non-{0} operand'.format(type_name))


    def _evaluate_unary_operand(self, operand_generator, constructor=lambda v: v, type_name='xpath object'):
        try:
            self._gab('evaluating operand.', indent_after=True)
            operand_value = constructor(operand_generator())
            self._gab('operand evaluation complete', outdent_before=True)
            return operand_value
        except TypeError:
            raise HquerySyntaxError('evaluated against a non-{0} operand'.format(type_name))


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
            self._gab('returning {0}'.format(result))
            return result

        return evaluate

    def nud(self):
        if self.value != '-':
            raise HquerySyntaxError('unexpected {0} at beginning of an expression')

        right = self.parse_interface.expression(LBP.prefix_op)

        def evaluate():
            right_value = self._evaluate_unary_operand(right, constructor=number, type_name='number')
            result = -right_value
            self._gab('returning {0}'.format(result))
            return result

        return evaluate



class AndOperator(Token):
    lbp = LBP.or_op

    def __str__(self):
        return '(operator "and")'

    def led(self, left):
        right = self.parse_interface.expression(self.lbp)

        def evaluate():
            left_value, right_value = self._evaluate_binary_operands(left,
                                                                     right,
                                                                     constructor=boolean,
                                                                     type_name='boolean')
            result = bool(left_value) and bool(right_value)
            self._gab('returning {0}'.format(result))
            return result

        return evaluate



class AxisToken(Token):
    lbp = LBP.nothing

    def __init__(self, parse_interface, value, **kwargs):
        super(AxisToken, self).__init__(parse_interface, value if value != '@' else 'attribute', **kwargs)
        self.axis = Axis[self.value.replace('-', '_')]

    def __str__(self):
        return '(axis "{0}")'.format(self.value)

    def nud(self):
        return self.parse_interface.location_path(self).evaluate



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

    def nud(self):
        return self.parse_interface.location_path(self).evaluate



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

    def nud(self):
        return self.parse_interface.location_path(self).evaluate



class EndToken(Token):
    lbp = LBP.nothing



class EqualityOperatorToken(Token):
    lbp = LBP.equality_op

    def __str__(self):
        return '(equality-operator "{0}")'.format(self.value)

    def led(self, left):
        right = self.parse_interface.expression(self.lbp)

        def evaluate():
            left_value, right_value = self._evaluate_binary_operands(left, right)
            result = equals(left_value, right_value) if self.value == '=' else not_equals(left_value, right_value)
            self._gab('returning {0}'.format(result))
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



class InterpolatedStringToken(Token):
    lbp = LBP.nothing

    def __init__(self, parse_interface, value, **kwargs):
        super(InterpolatedStringToken, self).__init__(parse_interface, value[1:-1], **kwargs)

    def nud(self):
        expressions = self._parse_contents()
        return lambda: ''.join([string_value(exp()) for exp in expressions])

    def _parse_contents(self):
        expressions = []
        clauses = self.value.split('$')
        expressions.append(lambda: clauses[0])
        for clause in clauses[1:]:
            if clause[0] == '{':
                expr, _, static = clause[1:].partition('}')
                # expressions.append(lambda: 'PARSED({0})'.format(expr))
                expressions.append(self.parse_interface.parse_in_new_processor(expr))
                expressions.append(lambda: static)
            else:
                # parse variable
                pass
        return expressions


class LeftBraceToken(Token):
    lbp = LBP.predicate

    def __str__(self):
        return '(left-brace)'



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
        self.node_test = NodeTest(self.value, name_test=True)

    def __str__(self):
        return '(name-test "{0}")'.format(self.value)

    def nud(self):
        return self.parse_interface.location_path(self).evaluate



class NodeTestToken(Token):
    lbp = LBP.node_test

    def __init__(self, *args, **kwargs):
        super(NodeTestToken, self).__init__(*args, **kwargs)
        self.node_test = NodeTest(self.value)

    def __str__(self):
        return '(node-test "{0}")'.format(self._dump_value())

    def nud(self):
        return self.parse_interface.location_path(self).evaluate

    def _dump_value(self):
        return '{0}{1}'.format(self.value, '()' if self.value != '*' else '')



class OpenParenthesisToken(Token):
    lbp = LBP.parenthesized_expr

    def __str__(self):
        return '(open parenthesis)'

    def nud(self):
        expr = self.parse_interface.expression(LBP.nothing)
        self.parse_interface.advance(CloseParenthesisToken)
        return expr



class OrOperatorToken(Token):
    lbp = LBP.or_op

    def __str__(self):
        return '(operator "or")'

    def led(self, left):
        right = self.parse_interface.expression(self.lbp)

        def evaluate():
            left_value, right_value = self._evaluate_binary_operands(left,
                                                                     right,
                                                                     constructor=boolean,
                                                                     type_name='boolean')
            result = bool(left_value) or bool(right_value)
            self._gab('returning {0}'.format(result))
            return result

        return evaluate



class ParentNodeToken(Token):
    lbp = LBP.node_test

    def __str__(self):
        return '(parent-node)'

    def nud(self):
        return self.parse_interface.location_path(self).evaluate



class RelationalOperatorToken(Token):
    lbp = LBP.relational_op

    def __str__(self):
        return '(operator {0})'.format(RelationalOperator(self.value).name)

    def led(self, left):
        right = self.parse_interface.expression(self.lbp)

        def evaluate():
            left_value, right_value = self._evaluate_binary_operands(left, right)
            result = RelationalOperator(self.value).evaluate(left_value, right_value)
            self._gab('returning {0}'.format(result))
            return result

        return evaluate



class RightBraceToken(Token):
    lbp = LBP.nothing

    def __str__(self):
        return '(right-brace)'



class SlashToken(Token):
    lbp = LBP.location_step

    def __str__(self):
        return '(slash)'

    def nud(self):
        next_token = self.parse_interface.peek()
        absolute_path_followup_tokens = (AxisToken, ContextNodeToken, NameTestToken, NodeTestToken, ParentNodeToken)

        if any(isinstance(next_token, clz) for clz in absolute_path_followup_tokens):
            path = self.parse_interface.location_path(self)
            return path.evaluate
        else:
            return lambda: make_node_set(soup_from_any_tag(get_context_node()))



class UnionOperatorToken(Token):
    lbp = LBP.union

    def __str__(self):
        return '(union operator)'

    def led(self, left):
        right = self.parse_interface.expression(self.lbp)

        def evaluate():
            left_value, right_value = self._evaluate_binary_operands(left, right, type_name='node set')
            left_value.extend(right_value)
            result = make_node_set(left_value)
            self._gab('returning node set with {0} nodes'.format(len(result)))
            return result

        return evaluate