import re

from hq.soup_util import debug_dump_long_string
from hq.xpath.expression_context import evaluate_in_context
from hq.xpath.location_path import LocationPath

from .tokens import *
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
        return OrOperator(parse_interface, value)
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
    (r'("[^"]*")', LiteralStringToken),
    (r"('[^']*')", LiteralStringToken),
    (r'(\d[\d\.]*)', LiteralNumberToken),
    (r'(,)', CommaToken),
    (r'(@)', AxisToken),
    (r'(\*)', _pick_token_for_asterisk),
    (r'(\+|-)', AddOrSubtractOperatorToken),
    (r'(<=|<|>=|>)', RelationalOperatorToken),
    (r'(node|text|comment)\(\)', NodeTestToken),
    (r'(div|mod)', _pick_token_for_div_or_mod),
    (r'(and|or)', _pick_token_for_and_or_or),
    (r'([a-z][a-z\-]*[a-z])\(', FunctionCallToken),
    (r'(\()', OpenParenthesisToken),
    (r'(\w[\w\-]*)', NameTestToken),
]


class ParseInterface:

    def advance(self, *expected_classes):
        return advance(*expected_classes)

    def advance_if(self, *expected_classes):
        return advance_if(*expected_classes)

    def expression(self, rbp=0):
        return expression(rbp)

    def is_on(self, *token_classes):
        return token_is(*token_classes)

    def location_path(self, first_token):
        return parse_location_path(first_token)

    def peek(self):
        return token


def query_xpath(soup, xpath_expression):
    verbose_print('PARSING XPATH "{0}"'.format(debug_dump_long_string(xpath_expression)), indent_after=True)
    expression_fn = parse(xpath_expression)
    verbose_print('EVALUATING XPATH', indent_after=True, outdent_before=True)
    result = evaluate_in_context(soup, expression_fn)
    verbose_print('XPATH QUERY FINISHED', outdent_before=True)
    return result


def tokenize(program):
    parse_interface = ParseInterface()
    pattern = re.compile(r'\s*(?:{0})'.format('|'.join([pattern for pattern, _ in token_config])))
    previous_token = None

    for matches in pattern.findall(program):
        index, value = next((i, group) for i, group in enumerate(list(matches)) if bool(group))
        if value is None:
            raise SyntaxError("unknown token")
        this_token = token_config[index][1](parse_interface, value=value, previous_token=previous_token)
        yield this_token
        previous_token = this_token

    yield EndToken(parse_interface)


def token_is(*token_classes):
    return any(isinstance(token, clz) for clz in token_classes)


def advance_if(*expected_classes):
    global token
    result = None

    if token_is(expected_classes):
        verbose_print('ParseInterface advancing over token {0}'.format(token))
        result = token
        token = next_token()

    return result


def advance(*expected_classes):
    global token

    result = advance_if(expected_classes)
    if result is None:
        class_names = ' or '.join([clz.__name__ for clz in expected_classes])
        raise XpathSyntaxError('{0} expected; got {1}'.format(class_names, token.__class__.__name__))
    return result


def parse(program):
    global next_token, token
    generator = tokenize(program)
    next_token = generator.__next__ if hasattr(generator, '__next__') else generator.next
    token = next_token()
    return expression()


def parse_location_path(first_token):
    verbose_print('Parsing location path starting with {0}'.format(first_token), indent_after=True)

    if isinstance(first_token, SlashToken):
        axis, node_test = parse_location_path_node_test()
        predicates = parse_location_path_predicates()
        path = LocationPath(axis, node_test, predicates, absolute=True)
    elif isinstance(first_token, DoubleSlashToken):
        path = LocationPath(Axis.descendant_or_self, NodeTest('node'), [], absolute=True)
        axis, node_test = parse_location_path_node_test()
        predicates = parse_location_path_predicates()
        path.append_step(axis, node_test, predicates)
    elif isinstance(first_token, AxisToken):
        _, node_test = parse_location_path_node_test()
        predicates = parse_location_path_predicates()
        path = LocationPath(first_token.axis, node_test, predicates)
    elif isinstance(first_token, ParentNodeToken):
        predicates = parse_location_path_predicates()
        path = LocationPath(Axis.parent, NodeTest('node'), predicates)
    elif isinstance(first_token, ContextNodeToken):
        predicates = parse_location_path_predicates()
        path = LocationPath(Axis.self, NodeTest('node'), predicates)
    else:
        if not (isinstance(first_token, NameTestToken) or isinstance(first_token, NodeTestToken)):
            raise XpathSyntaxError('Unexpected token {0}'.format(first_token))
        predicates = parse_location_path_predicates()
        path = LocationPath(Axis.child, first_token.node_test, predicates)

    while token_is(SlashToken, DoubleSlashToken):
        verbose_print('Continuing path after {0}'.format(token))

        if advance_if(DoubleSlashToken):
            path.append_step(Axis.descendant_or_self, NodeTest('node'), [])
        else:
            advance(SlashToken)

        axis, node_test = parse_location_path_node_test()
        predicates = parse_location_path_predicates()
        path.append_step(axis, node_test, predicates)

    verbose_print('Finished parsing location path {0}'.format(path), outdent_before=True)
    return path


def parse_location_path_node_test():
    axis_token = advance_if(AxisToken)
    if axis_token is None:
        axis = Axis.child
    else:
        verbose_print('consumed {0}'.format(axis_token))
        axis = axis_token.axis

    node_test_token = advance(NameTestToken, NodeTestToken, ContextNodeToken, ParentNodeToken)
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
            raise XpathSyntaxError('Axis {0} cannot be combined with abbreviated {1}.'.format(axis_token,
                                                                                              node_test_token))
        node_test = NodeTest('node')
    else:
        node_test = node_test_token.node_test

    return (axis, node_test)


def parse_location_path_predicates():
    expressions = []
    while advance_if(LeftBraceToken):
        verbose_print('parsing predicate expression starting with {0}'.format(token))
        expressions.append(expression(LBP.nothing))
        advance(RightBraceToken)
    return expressions


def expression(rbp=0):
    global next_token, token
    t = token
    verbose_print('parsing expression starting with {0} (RBP={1})'.format(t, rbp), indent_after=True)
    token = next_token()
    left = t.nud()
    while rbp < token.lbp:
        t = token
        verbose_print('continuing expression at {0} (LBP={1})'.format(t, token.lbp))
        token = next_token()
        left = t.led(left)
    verbose_print('finished expression', outdent_before=True)
    return left
