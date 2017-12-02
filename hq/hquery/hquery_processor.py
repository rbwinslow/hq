import re

from hq.hquery.computed_constructors.html_attribute import ComputedHtmlAttributeConstructor
from hq.hquery.computed_constructors.html_element import ComputedHtmlElementConstructor
from hq.hquery.computed_constructors.json_array import ComputedJsonArrayConstructor
from hq.hquery.computed_constructors.json_hash import ComputedJsonHashConstructor
from hq.hquery.evaluation_in_context import evaluate_in_context
from hq.hquery.location_path import LocationPath

from .tokens import *
from ..soup_util import debug_dump_long_string
from ..verbosity import verbose_print


def _is_name_test_predecessor(token):
    return any(isinstance(token, clazz) for clazz in (AxisToken, SlashToken, DoubleSlashToken))


def _pick_token_based_on_numeric_context(parse_interface, value, previous_token, numeric_class, other_class):
    numeric_predecessors = [CloseSquareBraceToken,
                            CloseParenthesisToken,
                            LiteralNumberToken,
                            NameTestToken,
                            VariableToken]
    if any(isinstance(previous_token, token_class) for token_class in numeric_predecessors):
        return numeric_class(parse_interface, value)
    else:
        return other_class(parse_interface, value)


def _pick_token_for_and_or_or(parse_interface, value, previous_token):
    if previous_token is None or _is_name_test_predecessor(previous_token):
        return NameTestToken(parse_interface, value)
    elif value == 'or':
        return OrOperatorToken(parse_interface, value)
    else:
        return AndOperator(parse_interface, value)


def _pick_token_for_asterisk(parse_interface, value, previous_token):
    return _pick_token_based_on_numeric_context(parse_interface,
                                                value,
                                                previous_token,
                                                MultiplyOperatorToken,
                                                NodeTestToken)


def _pick_token_for_div_or_mod(parse_interface, value, previous_token):
    return _pick_token_based_on_numeric_context(parse_interface,
                                                value,
                                                previous_token,
                                                DivOrModOperatorToken,
                                                NameTestToken)


def _pick_token_for_computed_constructor_reserved_word(parse_interface, value, previous_token):
    if _is_name_test_predecessor(previous_token):
        return NameTestToken(parse_interface, value)
    else:
        return ConstructorReservedWordToken(parse_interface, value)


def _pick_token_for_if_or_else(parse_interface, value, previous_token):
    if _is_name_test_predecessor(previous_token):
        return NameTestToken(parse_interface, value)
    else:
        return IfElseToken(parse_interface, value)


def _pick_token_for_flwor_reserved_word(parse_interface, value, previous_token):
    if _is_name_test_predecessor(previous_token):
        return NameTestToken(parse_interface, value)
    else:
        return FlworReservedWordToken(parse_interface, value)


def _pick_token_for_to(parse_interface, value, previous_token):
    return _pick_token_based_on_numeric_context(parse_interface,
                                                value,
                                                previous_token,
                                                RangeOperatorToken,
                                                NameTestToken)


_all_axes = [value.token() for value in Axis] + [re.escape(a) for a in Axis.abbreviations()]

token_config = [
    (r'(//)', DoubleSlashToken),
    (r'(/)', SlashToken),
    (r'(\[)', OpenSquareBraceToken),
    (r'(\])', CloseSquareBraceToken),
    (r'({0})::'.format('|'.join(_all_axes)), AxisToken),
    (r'(\.\.)', ParentNodeToken),
    (r'(\.)', ContextNodeToken),
    (r'(\))', CloseParenthesisToken),
    (r'(=>)', UnionDecompositionToken),
    (r'(!=|=)', EqualityOperatorToken),
    (r'(`[^`]*`)', InterpolatedStringToken),
    (r'("[^"]*")', LiteralStringToken),
    (r"('[^']*')", LiteralStringToken),
    (r'(\d[\d\.]*)', LiteralNumberToken),
    (r'(,)', CommaToken),
    (r'(@)', AxisToken),
    (r'(\*)', _pick_token_for_asterisk),
    (r'(->)', AbbreviatedFlworOperatorToken),
    (r'(\+|-)', AddOrSubtractOperatorToken),
    (r'(<=|<|>=|>)', RelationalOperatorToken),
    (r'(\|)', UnionOperatorToken),
    (r'\$([_\w][\w_\-]*)', VariableToken),
    (r'(:=)', AssignmentOperatorToken),
    (r'(for|let|return)(?!\w)', _pick_token_for_flwor_reserved_word),
    (r'(array|attribute|element|hash)(?!\w)', _pick_token_for_computed_constructor_reserved_word),
    (r'(node|text|comment)\(\)', NodeTestToken),
    (r'(div|mod)(?![a-zA-Z])', _pick_token_for_div_or_mod),
    (r'(and|or)(?![a-zA-Z])', _pick_token_for_and_or_or),
    (r'(if|else)(?![a-zA-Z])', _pick_token_for_if_or_else),
    (r'(to)(?![a-zA-Z])', _pick_token_for_to),
    (r'([a-z][a-z\-]*[a-z])\(', FunctionCallToken),
    (r'(\()', OpenParenthesisToken),
    (r'({[a-z]{1,3}(?::[^:]*)*:})', ComputedConstructorFiltersToken),
    (r'(\{)', OpenCurlyBraceToken),
    (r'(\})', CloseCurlyBraceToken),
    (r'(\w[\w_]*)\s*:', HashKeyToken),
    (r'(\w[\w\-]*)', NameTestToken),
]


class ParseInterface:

    def __init__(self, processor):
        self.processor = processor

    def advance(self, *expected_classes):
        return self.processor.advance(*expected_classes)

    def advance_if(self, *expected_classes):
        return self.processor.advance_if(*expected_classes)

    def computed_constructor(self, first_token):
        return self.processor.parse_computed_constructor(first_token)

    def expression(self, rbp=0):
        return self.processor.expression(rbp)

    def flwor(self, first_token):
        return self.processor.parse_flwor(first_token)

    def if_then_else(self):
        return self.processor.parse_if_then_else()

    def is_on(self, *token_classes):
        return self.processor.token_is(*token_classes)

    def location_path(self, first_token, root_expression=None):
        return self.processor.parse_location_path(first_token, root_expression=root_expression)

    def parse_in_new_processor(self, source):
        return HqueryProcessor(source).parse()

    def peek(self):
        return self.processor.token



class HqueryProcessor():

    token = None
    next_token = None


    def __init__(self, source, preserve_space=False):
        self.source = source
        self.preserve_space = preserve_space


    def query(self, starting_node):
        verbose_print(u'PARSING HQUERY "{0}"'.format(debug_dump_long_string(self.source)), indent_after=True)
        expression_fn = self.parse()
        verbose_print('EVALUATING HQUERY', indent_after=True, outdent_before=True)
        result = evaluate_in_context(starting_node, expression_fn, preserve_space=self.preserve_space)
        verbose_print('HQUERY FINISHED', outdent_before=True)
        return result


    def tokenize(self):
        parse_interface = ParseInterface(self)
        pattern = re.compile(r'\s*(?:{0})'.format('|'.join([pattern for pattern, _ in token_config])))
        previous_token = None

        for matches in pattern.findall(self.source):
            index, value = next((i, group) for i, group in enumerate(list(matches)) if bool(group))
            if value is None:
                raise SyntaxError("unknown token")
            this_token = token_config[index][1](parse_interface, value=value, previous_token=previous_token)
            yield this_token
            previous_token = this_token

        yield EndToken(parse_interface)


    def token_is(self, *token_classes):
        return any(isinstance(self.token, clz) for clz in token_classes)


    def advance_if(self, *expected_classes):
        result = None

        if self.token_is(expected_classes):
            verbose_print('ParseInterface advancing over token {0}'.format(self.token))
            result = self.token
            self.token = self.next_token()

        return result


    def advance_over_name(self):
        accept_token_that_looks_like_a_name_with_no_grammar_role_of_its_own = NameTestToken
        return self.advance(accept_token_that_looks_like_a_name_with_no_grammar_role_of_its_own).value


    def advance(self, *expected_classes):
        result = self.advance_if(expected_classes)
        if result is None:
            class_names = ' or '.join([clz.__name__ for clz in expected_classes])
            raise HquerySyntaxError('expected {0}; got {1}'.format(class_names, self.token.__class__.__name__))
        return result


    def parse(self):
        generator = self.tokenize()
        self.next_token = generator.__next__ if hasattr(generator, '__next__') else generator.next
        self.token = self.next_token()
        evaluation_fn = self.expression()
        if not self.token_is(EndToken):
            raise HquerySyntaxError('Unexpected token {0} beyond end of HQuery'.format(self.token))
        return evaluation_fn


    def parse_computed_array_constructor(self):
        constructor = ComputedJsonArrayConstructor()
        self.advance(OpenCurlyBraceToken)

        if not isinstance(self.token, CloseCurlyBraceToken):
            constructor.set_contents(self.expression())

        self.advance(CloseCurlyBraceToken)
        return constructor


    def parse_computed_attribute_constructor(self):
        constructor = ComputedHtmlAttributeConstructor(self.advance_over_name())
        self.advance(OpenCurlyBraceToken)

        if not isinstance(self.token, CloseCurlyBraceToken):
            constructor.set_content(self.expression())

        self.advance(CloseCurlyBraceToken)
        return constructor


    def parse_computed_constructor(self, first_token):
        if not isinstance(first_token, ConstructorReservedWordToken):
            raise HquerySyntaxError('Computed constructor parsing somehow triggered by {0}'.format(str(first_token)))

        verbose_print('Parsing computed constructor "{0}"'.format(first_token.value), indent_after=True)
        result = getattr(self, 'parse_computed_{0}_constructor'.format(first_token.value))()

        verbose_print('Finished parsing computed constructor "{0}"'.format(first_token.value), outdent_before=True)
        return result


    def parse_computed_element_constructor(self):
        constructor = ComputedHtmlElementConstructor(self.advance_over_name())
        self.advance(OpenCurlyBraceToken)

        if not isinstance(self.token, CloseCurlyBraceToken):
            constructor.set_content(self.expression())

        self.advance(CloseCurlyBraceToken)
        return constructor


    def parse_computed_hash_constructor(self):
        constructor = ComputedJsonHashConstructor()
        token = self.advance(ComputedConstructorFiltersToken, OpenCurlyBraceToken)

        if isinstance(token, ComputedConstructorFiltersToken):
            constructor.set_filters(token.value)
            self.advance(OpenCurlyBraceToken)

        if not isinstance(self.token, CloseCurlyBraceToken):
            constructor.set_contents(self.expression())

        self.advance(CloseCurlyBraceToken)
        return constructor


    def parse_if_then_else(self):
        verbose_print('Parsing if/then/else condition', indent_after=True)
        self.advance(OpenParenthesisToken)
        condition = self.expression()
        self.advance(CloseParenthesisToken)
        verbose_print('Parsing if/then/else "then" clause', outdent_before=True, indent_after=True)
        then = self.advance_over_name()
        if then.lower() != 'then':
            raise HquerySyntaxError('if/then/else expected "then" after condition; got "{0}"'.format(then))
        then_expr = self.expression()
        verbose_print('Parsing if/then/else "else" clause', outdent_before=True, indent_after=True)
        self._cannot_eat_else_same_as_then_because_else_needs_lower_lbp_so_then_expr_knows_when_to_stop()
        else_expr = self.expression()
        verbose_print('Finished parsing if/then/else', outdent_before=True)

        def evaluate():
            if boolean(condition()):
                return then_expr()
            else:
                return else_expr()

        return evaluate


    def parse_flwor(self, first_token):
        verbose_print('Parsing FLWOR starting with {0}'.format(first_token), indent_after=True)

        flwor = Flwor()
        token = first_token
        while True:
            if isinstance(token, FlworReservedWordToken):
                verbose_print('Parsing FLWOR "{0}" clause'.format(token.value))
                getattr(self, 'parse_flwor_{0}'.format(token.value))(flwor)
                if token.value == 'return':
                    break
            else:
                raise HquerySyntaxError('Unexpected token {0} at beginning of FLWOR'.format(first_token))
            token = self.advance_if(FlworReservedWordToken)
            if token is None:
                break

        if flwor.return_expression is None:
            raise HquerySyntaxError('no "return" clause at end of FLWOR')
        verbose_print(lambda: 'Finished parsing FLWOR {0}'.format(flwor.debug_dump()), outdent_before=True)
        return flwor


    def parse_flwor_for(self, flwor):
        variable_name = self.advance(VariableToken).value

        in_keyword = self.advance_over_name()
        if in_keyword.lower() != 'in':
            raise HquerySyntaxError('FLWOR expected reserved word "in," got "{0}"'.format(in_keyword))

        iteration_expression = self.expression()

        flwor.set_iteration_expression(variable_name, iteration_expression)


    def parse_flwor_let(self, flwor):
        variable_token = self.advance(VariableToken)
        self.advance(AssignmentOperatorToken)
        expression = self.expression(LBP.sequence)
        flwor.append_let(variable_token.value, expression)

        if self.advance_if(CommaToken):
            self.parse_flwor_let(flwor)


    def parse_flwor_return(self, flwor):
        flwor.set_return_expression(self.expression(LBP.sequence))


    def parse_location_path(self, first_token, root_expression=None):
        verbose_print(
            'Parsing location path {0} {1}'.format(
                'starting with' if root_expression is None else 'rooted at <expr> followed by',
                first_token
            ),
            indent_after=True
        )

        if isinstance(first_token, SlashToken):
            axis, node_test = self.parse_location_path_node_test()
            predicates = self.parse_location_path_predicates()
            path = LocationPath(axis,
                                node_test,
                                predicates,
                                absolute=(root_expression is None),
                                root_expression=root_expression)
        elif isinstance(first_token, DoubleSlashToken):
            path = LocationPath(Axis.descendant_or_self,
                                NodeTest('node'),
                                [],
                                absolute=(root_expression is None),
                                root_expression=root_expression)
            axis, node_test = self.parse_location_path_node_test()
            predicates = self.parse_location_path_predicates()
            path.append_step(axis, node_test, predicates)
        elif isinstance(first_token, AxisToken):
            _, node_test = self.parse_location_path_node_test()
            predicates = self.parse_location_path_predicates()
            path = LocationPath(first_token.axis, node_test, predicates)
        elif isinstance(first_token, ParentNodeToken):
            predicates = self.parse_location_path_predicates()
            path = LocationPath(Axis.parent, NodeTest('node'), predicates)
        elif isinstance(first_token, ContextNodeToken):
            predicates = self.parse_location_path_predicates()
            path = LocationPath(Axis.self, NodeTest('node'), predicates)
        elif isinstance(first_token, OpenSquareBraceToken):
            if root_expression is None:
                raise HquerySyntaxError('a predicate (left brace) must follow an expression that yields a node set')
            path = LocationPath(Axis.self,
                                NodeTest('node'),
                                self.parse_location_path_predicates(already_inside_brace=True),
                                root_expression=root_expression)
        else:
            if not (isinstance(first_token, NameTestToken) or isinstance(first_token, NodeTestToken)):
                raise HquerySyntaxError('Unexpected token {0}'.format(first_token))
            predicates = self.parse_location_path_predicates()
            path = LocationPath(Axis.child, first_token.node_test, predicates)

        while self.token_is(SlashToken, DoubleSlashToken):
            verbose_print('Continuing path after {0}'.format(self.token))

            if self.advance_if(DoubleSlashToken):
                path.append_step(Axis.descendant_or_self, NodeTest('node'), [])
            else:
                self.advance(SlashToken)

            axis, node_test = self.parse_location_path_node_test()
            predicates = self.parse_location_path_predicates()
            path.append_step(axis, node_test, predicates)

        verbose_print('Finished parsing location path {0}'.format(path), outdent_before=True)
        return path


    def parse_location_path_node_test(self):
        axis_token = self.advance_if(AxisToken)
        if axis_token is None:
            axis = Axis.child
        else:
            verbose_print('consumed {0}'.format(axis_token))
            axis = axis_token.axis

        node_test_token = self.advance(NameTestToken, NodeTestToken, ContextNodeToken, ParentNodeToken)
        verbose_print('consumed {0}'.format(node_test_token))

        is_abbreviated = False
        if isinstance(node_test_token, ContextNodeToken):
            is_abbreviated = True
            axis = Axis.self
        elif isinstance(node_test_token, ParentNodeToken):
            is_abbreviated = True
            axis = Axis.parent

        if is_abbreviated:
            if axis_token is not None:
                raise HquerySyntaxError('Axis {0} cannot be combined with abbreviated {1}.'.format(axis_token,
                                                                                                   node_test_token))
            node_test = NodeTest('node')
        else:
            node_test = node_test_token.node_test

        return (axis, node_test)


    def parse_location_path_predicates(self, already_inside_brace=False):
        expressions = []
        while already_inside_brace or self.advance_if(OpenSquareBraceToken):
            already_inside_brace = False
            verbose_print('parsing predicate expression starting with {0}'.format(self.token))
            expressions.append(self.expression())
            self.advance(CloseSquareBraceToken)
        return expressions


    def expression(self, rbp=LBP.nothing):
        t = self.token
        verbose_print(u'parsing expression starting with {0} (RBP={1})'.format(t, rbp), indent_after=True)
        try:

            self.token = self.next_token()
            left = t.nud()
            while rbp < self.token.lbp:
                t = self.token
                verbose_print('continuing expression at {0} (LBP={1})'.format(t, self.token.lbp))
                self.token = self.next_token()
                left = t.led(left)
            verbose_print('finished expression', outdent_before=True)
            return left

        except AttributeError as err:
            attr = re.search(r"has no attribute '(\w+)'", err.args[0]).group(1)
            if attr == 'nud':
                raise HquerySyntaxError('unexpected token {0} found at beginning of expression'.format(t))
            elif attr == 'led':
                raise HquerySyntaxError('unexpected token {0} encountered in expression'.format(t))
            else:
                raise


    def _cannot_eat_else_same_as_then_because_else_needs_lower_lbp_so_then_expr_knows_when_to_stop(self):
        else_token = self.advance(IfElseToken)
        if else_token.value.lower() != 'else':
            raise HquerySyntaxError('if/then/else expected "else" after "then" expression; got "{0}"'.format(
                else_token.value
            ))
