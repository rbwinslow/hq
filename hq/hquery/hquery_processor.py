import re

from hq.hquery.evaluation_in_context import evaluate_in_context
from hq.hquery.location_path import LocationPath

from .tokens import *
from ..soup_util import debug_dump_long_string
from ..verbosity import verbose_print


def _pick_token_based_on_numeric_context(parse_interface, value, previous_token, numeric_class, other_class):
    numeric_predecessors = [LiteralNumberToken, CloseParenthesisToken]
    if any(isinstance(previous_token, token_class) for token_class in numeric_predecessors):
        return numeric_class(parse_interface, value)
    else:
        return other_class(parse_interface, value)


def _pick_token_for_and_or_or(parse_interface, value, previous_token):
    name_test_predecessors = (AxisToken, SlashToken, DoubleSlashToken)
    if previous_token is None or any(isinstance(previous_token, clazz) for clazz in name_test_predecessors):
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


def _pick_token_for_to(parse_interface, value, previous_token):
    return _pick_token_based_on_numeric_context(parse_interface,
                                                value,
                                                previous_token,
                                                RangeOperatorToken,
                                                NameTestToken)


token_config = [
    (r'(//)', DoubleSlashToken),
    (r'(/)', SlashToken),
    (r'(\[)', LeftBraceToken),
    (r'(\])', RightBraceToken),
    (r'(\.\.)', ParentNodeToken),
    (r'(\.)', ContextNodeToken),
    (r'(\))', CloseParenthesisToken),
    (r'(!=|=)', EqualityOperatorToken),
    (r'({0})::'.format('|'.join([value.token() for value in Axis])), AxisToken),
    (r'(`[^`]*`)', InterpolatedStringToken),
    (r'("[^"]*")', LiteralStringToken),
    (r"('[^']*')", LiteralStringToken),
    (r'(\d[\d\.]*)', LiteralNumberToken),
    (r'(,)', CommaToken),
    (r'(@)', AxisToken),
    (r'(\*)', _pick_token_for_asterisk),
    (r'(\+|-)', AddOrSubtractOperatorToken),
    (r'(<=|<|>=|>)', RelationalOperatorToken),
    (r'(\|)', UnionOperatorToken),
    (r'(node|text|comment)\(\)', NodeTestToken),
    (r'(div|mod)', _pick_token_for_div_or_mod),
    (r'(and|or)', _pick_token_for_and_or_or),
    (r'(to)', _pick_token_for_to),
    (r'([a-z][a-z\-]*[a-z])\(', FunctionCallToken),
    (r'(\()', OpenParenthesisToken),
    (r'(\w[\w\-]*)', NameTestToken),
]


class ParseInterface:

    def __init__(self, processor):
        self.processor = processor

    def advance(self, *expected_classes):
        return self.processor.advance(*expected_classes)

    def advance_if(self, *expected_classes):
        return self.processor.advance_if(*expected_classes)

    def expression(self, rbp=0):
        return self.processor.expression(rbp)

    def is_on(self, *token_classes):
        return self.processor.token_is(*token_classes)

    def location_path(self, first_token):
        return self.processor.parse_location_path(first_token)

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
        verbose_print('PARSING HQUERY "{0}"'.format(debug_dump_long_string(self.source)), indent_after=True)
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
        return self.expression()


    def parse_location_path(self, first_token):
        verbose_print('Parsing location path starting with {0}'.format(first_token), indent_after=True)

        if isinstance(first_token, SlashToken):
            axis, node_test = self.parse_location_path_node_test()
            predicates = self.parse_location_path_predicates()
            path = LocationPath(axis, node_test, predicates, absolute=True)
        elif isinstance(first_token, DoubleSlashToken):
            path = LocationPath(Axis.descendant_or_self, NodeTest('node'), [], absolute=True)
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


    def parse_location_path_predicates(self):
        expressions = []
        while self.advance_if(LeftBraceToken):
            verbose_print('parsing predicate expression starting with {0}'.format(self.token))
            expressions.append(self.expression(LBP.nothing))
            self.advance(RightBraceToken)
        return expressions


    def expression(self, rbp=0):
        t = self.token
        verbose_print('parsing expression starting with {0} (RBP={1})'.format(t, rbp), indent_after=True)
        self.token = self.next_token()
        left = t.nud()
        while rbp < self.token.lbp:
            t = self.token
            verbose_print('continuing expression at {0} (LBP={1})'.format(t, self.token.lbp))
            self.token = self.next_token()
            left = t.led(left)
        verbose_print('finished expression', outdent_before=True)
        return left
