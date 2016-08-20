import re

from .tokens import *
from ..verbosity import verbose_print


token_config = [
    (r'(//)', DoubleSlashToken),
    (r'(/)', SlashToken),
    (r'(\[)', LeftBraceToken),
    (r'(\])', RightBraceToken),
    (r'(\.\.)', ParentNodeToken),
    (r'(\.)', ContextNodeToken),
    (r'(\+|-)', PlusOrMinusToken),
    (r'(\))', CloseParenthesisToken),
    (r'(!=|=)', EqualityOperatorToken),
    (r'({0})::'.format('|'.join([value.token() for value in Axis])), AxisToken),
    (r'"([^"]*)"', LiteralStringToken),
    (r"'([^']*)'", LiteralStringToken),
    (r'(-?\d[\d\.]*)', LiteralNumberToken),
    (r'(node|text)\(\)', NodeTestToken),
    (r'([a-z][a-z\-]*[a-z])\(', FunctionCallToken),
    (r'(\w[\w]*)', NameTestToken),
]


class ParseInterface:
    def advance(self):
        global next_token, token
        verbose_print('ParseInterface advancing over token {0}'.format(token))
        t = token
        token = next_token()
        return t

    def expression(self, rbp=0):
        return expression(rbp)


def query_xpath(soup, xpath_expression):
    verbose_print('PARSING XPATH', indent_after=True)
    expression_fn = parse(xpath_expression)
    verbose_print('EVALUATING XPATH', indent_after=True, outdent_before=True)
    result = expression_fn(ExpressionContext(node=soup))
    verbose_print('XPATH QUERY FINISHED', outdent_before=True)
    return result


def tokenize(program):
    parse_interface = ParseInterface()
    pattern = re.compile(r'\s*(?:{0})'.format('|'.join([pattern for pattern, _ in token_config])))

    for matches in pattern.findall(program):
        index, value = next((i, group) for i, group in enumerate(list(matches)) if bool(group))
        if index is None:
            raise SyntaxError("unknown token")
        yield token_config[index][1](parse_interface, value=value)

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
