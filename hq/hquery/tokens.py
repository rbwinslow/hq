from hq.hquery.computed_constructors.hash_key_value import ComputedHashKeyValueConstructor
from hq.hquery.equality_operators import equals, not_equals
from hq.hquery.flwor import Flwor
from hq.hquery.function_support import FunctionSupport
from hq.hquery.functions.core_boolean import boolean
from hq.hquery.functions.core_number import number
from hq.hquery.node_test import NodeTest
from hq.hquery.object_type import object_type_name, debug_dump_anything
from hq.hquery.sequences import make_node_set, sequence_concat
from hq.hquery.relational_operators import RelationalOperator
from hq.hquery.string_interpolation import parse_interpolated_string
from hq.hquery.syntax_error import HquerySyntaxError
from hq.hquery.union_decomposition import UnionDecomposition
from hq.hquery.variables import value_of_variable
from hq.soup_util import soup_from_any_tag
from hq.string_util import html_entity_decode
from hq.verbosity import verbose_print

from .axis import Axis
from .expression_context import get_context_node

function_support = FunctionSupport()



class LBP:
    """Left-binding precendence values."""
    (
        nothing, sequence, union_decomp, union, range, abbrev_flwor, or_op,
        and_op, equality_op, relational_op, add_or_subtract, mult_or_div,
        prefix_op, function_call, location_step, node_test, parenthesized_expr
    ) = range(17)

assert LBP.sequence == LBP.nothing + 1



class Token(object):

    def __init__(self, parse_interface, value=None, **kwargs):
        self.parse_interface = parse_interface
        self.value = value


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
        verbose_print(u'{0} {1}'.format(self, msg), **kwargs)



class AbbreviatedFlworOperatorToken(Token):
    lbp = LBP.abbrev_flwor

    def __str__(self):
        return '(abbreviated-FLWOR-operator)'

    def led(self, left):
        right = self.parse_interface.expression(LBP.sequence)

        flwor = Flwor()
        flwor.set_iteration_expression('_', left)
        flwor.set_return_expression(right)
        return flwor.evaluate


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



class AssignmentOperatorToken(Token):
    lbp = LBP.nothing

    def __str__(self):
        return '(assignment-operator)'



class AxisToken(Token):
    lbp = LBP.nothing

    def __init__(self, parse_interface, value, **kwargs):
        super(AxisToken, self).__init__(parse_interface, Axis.canonicalize(value), **kwargs)
        self.axis = Axis[self.value]

    def __str__(self):
        return '(axis "{0}")'.format(self.value)

    def nud(self):
        return self.parse_interface.location_path(self).evaluate



class CloseCurlyBraceToken(Token):
    lbp = LBP.nothing

    def __str__(self):
        return '(close-curly-brace)'



class CloseParenthesisToken(Token):
    lbp = LBP.nothing

    def __str__(self):
        return '(close-parenthesis)'



class CloseSquareBraceToken(Token):
    lbp = LBP.nothing

    def __str__(self):
        return '(right-brace)'



class CommaToken(Token):
    lbp = LBP.sequence

    def __str__(self):
        return '(comma)'

    def led(self, left):
        right = self.parse_interface.expression(self.lbp)

        def evaluate():
            left_value, right_value = self._evaluate_binary_operands(left, right)
            return sequence_concat(left_value, right_value)

        return evaluate



class ComputedConstructorFiltersToken(Token):
    lbp = LBP.nothing

    def __init__(self, parse_interface, value, **kwargs):
        super(ComputedConstructorFiltersToken, self).__init__(parse_interface, value[1:-1], **kwargs)

    def __str__(self):
        return '(computed-constructor-filters "{0}")'.format(self.value)


class ConstructorReservedWordToken(Token):
    lbp = LBP.nothing

    def __str__(self):
        return '(constructor-keyword "{0}")'.format(self.value)

    def nud(self):
        return self.parse_interface.computed_constructor(self).evaluate



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

    def led(self, left):
        return self.parse_interface.location_path(self, root_expression=left).evaluate

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



class FlworReservedWordToken(Token):
    lbp = LBP.nothing

    def __init__(self, parse_interface, value, **kwargs):
        super(FlworReservedWordToken, self).__init__(parse_interface, value.lower(), **kwargs)

    def __str__(self):
        return '({0})'.format(self.value)

    def nud(self):
        return self.parse_interface.flwor(self).evaluate



class FunctionCallToken(Token):
    lbp = LBP.function_call

    def __str__(self):
        return '(function call "{0}")'.format(self.value)

    def nud(self):
        arg_generators = []

        while (not isinstance(self.parse_interface.peek(), CloseParenthesisToken)):
            arg_generators.append(self.parse_interface.expression(LBP.sequence))
            self.parse_interface.advance_if(CommaToken)

        self.parse_interface.advance(CloseParenthesisToken)

        def evaluate():
            self._gab('evaluating argument list for function "{0}."'.format(self.value))
            arguments = [gen() for gen in arg_generators]
            arg_types = ','.join(object_type_name(arg) for arg in arguments)
            self._gab('calling {0}({1}).'.format(self.value, arg_types))
            return function_support.call_function(self.value, *arguments)

        return evaluate



class HashKeyToken(Token):
    lpb = LBP.nothing

    def __str__(self):
        return '(hash-key "{0}")'.format(self.value)

    def nud(self):
        constructor = ComputedHashKeyValueConstructor(self.value)
        constructor.set_value(self.parse_interface.expression(LBP.sequence))
        return constructor.evaluate



class IfElseToken(Token):
    lbp = LBP.nothing

    def __str__(self):
        return '(if-reserved-word)'

    def nud(self):
        return self.parse_interface.if_then_else()



class InterpolatedStringToken(Token):
    lbp = LBP.nothing

    def __init__(self, parse_interface, value, **kwargs):
        super(InterpolatedStringToken, self).__init__(parse_interface, value[1:-1], **kwargs)

    def __str__(self):
        return u'(interpolated-string `{0}`)'.format(self.value)

    def nud(self):
        return parse_interpolated_string(self.value, self.parse_interface)



class LiteralNumberToken(Token):
    lbp = LBP.nothing

    def __str__(self):
        return '(literal-number {0})'.format(self.value)

    def nud(self):
        return lambda: number(self.value)



class LiteralStringToken(Token):
    lbp = LBP.nothing

    def __init__(self, parse_interface, value, **kwargs):
        super(LiteralStringToken, self).__init__(parse_interface, html_entity_decode(value[1:-1]), **kwargs)

    def __str__(self):
        return u'(literal-string "{0}")'.format(self.value)

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



class OpenCurlyBraceToken(Token):
    lbp = LBP.nothing

    def __str__(self):
        return '(open-curly-brace)'



class OpenParenthesisToken(Token):
    lbp = LBP.parenthesized_expr

    def __str__(self):
        return '(open-parenthesis)'

    def nud(self):
        expr = self.parse_interface.expression(LBP.nothing)
        self.parse_interface.advance(CloseParenthesisToken)
        return expr



class OpenSquareBraceToken(Token):
    lbp = LBP.location_step

    def __str__(self):
        return '(left-brace)'

    def led(self, left):
        path = self.parse_interface.location_path(self, root_expression=left)
        return path.evaluate



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



class RangeOperatorToken(Token):
    lbp = LBP.range

    def __str__(self):
        return '(range-operator)'

    def led(self, left):
        right = self.parse_interface.expression(self.lbp)

        def evaluate():
            left_value, right_value = self._evaluate_binary_operands(left,
                                                                     right,
                                                                     constructor=number,
                                                                     type_name='number')
            return list(number(x) for x in range(int(left_value), int(right_value + 1)))

        return evaluate



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



class SlashToken(Token):
    lbp = LBP.location_step

    def __str__(self):
        return '(slash)'

    def led(self, left):
        path = self.parse_interface.location_path(self, root_expression=left)
        return path.evaluate

    def nud(self):
        next_token = self.parse_interface.peek()
        absolute_path_followup_tokens = (AxisToken, ContextNodeToken, NameTestToken, NodeTestToken, ParentNodeToken)

        if any(isinstance(next_token, clz) for clz in absolute_path_followup_tokens):
            path = self.parse_interface.location_path(self)
            return path.evaluate
        else:
            return lambda: make_node_set(soup_from_any_tag(get_context_node()))



class UnionDecompositionToken(Token):
    lbp = LBP.union_decomp

    def __str__(self):
        return '(union decomposition)'

    def led(self, left):
        decomp = UnionDecomposition()
        mapping_generators = []

        if self.parse_interface.advance_if(OpenParenthesisToken) is None:
            while True:
                mapping_generators.append(self.parse_interface.expression(LBP.union))
                if self.parse_interface.advance_if(UnionOperatorToken) is None:
                    break
        else:
            while (not isinstance(self.parse_interface.peek(), CloseParenthesisToken)):
                mapping_generators.append(self.parse_interface.expression(LBP.union))
                self.parse_interface.advance_if(UnionOperatorToken)
            self.parse_interface.advance(CloseParenthesisToken)

        decomp.set_union_expression(left)
        decomp.set_mapping_generators(mapping_generators)
        return decomp.evaluate



class UnionOperatorToken(Token):
    lbp = LBP.union

    def __str__(self):
        return '(union operator)'

    def led(self, left):
        if hasattr(left, 'union_index'):
            left_union_index = left.union_index
        else:
            left_union_index = 0
        right_union_index = left_union_index + 1

        right = self.parse_interface.expression(self.lbp)

        def evaluate():
            left_value, right_value = self._evaluate_binary_operands(left, right, type_name='node set')
            for item in right_value:
                if not isinstance(getattr(item, 'union_index', None), int):
                    setattr(item, 'union_index', right_union_index)
            if left_union_index == 0:
                for item in left_value:
                    if not isinstance(getattr(item, 'union_index', None), int):
                        setattr(item, 'union_index', left_union_index)
            left_value.extend(right_value)
            result = make_node_set(left_value)
            self._gab('returning node set with {0} nodes'.format(len(result)))
            return result

        setattr(evaluate, 'union_index', right_union_index)

        return evaluate



class VariableToken(Token):
    lbp = LBP.nothing

    def __str__(self):
        return '(variable ${0})'.format(self.value)

    def nud(self):

        def evaluate():
            result = value_of_variable(self.value)
            self._gab(lambda: u'reference evaluating to value {0}'.format(debug_dump_anything(result)))
            return result

        return evaluate
