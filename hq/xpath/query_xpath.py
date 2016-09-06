import re

from hq.xpath.expression_context import evaluate_in_context

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
    (r'(node|text)\(\)', NodeTestToken),
    (r'(div|mod)', _pick_token_for_div_or_mod),
    (r'(and|or)', _pick_token_for_and_or_or),
    (r'([a-z][a-z\-]*[a-z])\(', FunctionCallToken),
    (r'(\w[\w]*)', NameTestToken),
]


class ParseInterface:

    def advance(self, expected_class):
        global token
        result = self.advance_if(expected_class)
        if result is None:
            raise RuntimeError('{0} expected; got {1}'.format(expected_class.__name__, token.__class__.__name__))
        return result

    def advance_if(self, expected_class):
        global next_token, token
        result = None

        if isinstance(token, expected_class):
            verbose_print('ParseInterface advancing over token {0}'.format(token))
            result = token
            token = next_token()

        return result

    def expression(self, rbp=0):
        return expression(rbp)

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


def parse(program):
    global next_token, token
    generator = tokenize(program)
    next_token = generator.__next__ if hasattr(generator, '__next__') else generator.next
    token = next_token()
    return expression()


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
