import re

from .tokens import *
from ..verbosity import verbose_print


axis_pattern = '({0})'.format('|'.join([value.token() for value in Axis]))
node_test_pattern = '(node|text)'
all_tokens_pattern = r'\s*(?:(//)|(/)|(\[)|(\])|(\.\.)|(\.)|(!=|=)|{0}::|"([^"]*)"|{1}|{2}\(\)|(\w[\w]*))'
token_pattern = re.compile(all_tokens_pattern.format(axis_pattern, "'([^']*)'", node_test_pattern))


def query_xpath(soup, xpath_expression):
    verbose_print('PARSING XPATH', indent_after=True)
    expression_fn = parse(xpath_expression)
    verbose_print('EVALUATING XPATH', indent_after=True, outdent_before=True)
    result = expression_fn(ExpressionContext(node=soup))
    verbose_print('XPATH QUERY FINISHED', outdent_before=True)
    return result


def tokenize(program):
    for double_slash, slash, left_brace, right_brace, double_dot, dot, equality_op, axis, dq_string, sq_string, \
            node_test, name_test in \
            token_pattern.findall(program):
        if double_slash:
            yield DoubleSlashToken()
        elif slash:
            yield SlashToken()
        elif left_brace:
            yield LeftBraceToken()
        elif right_brace:
            yield RightBraceToken()
        elif double_dot:
            yield ParentNodeToken()
        elif dot:
            yield ContextNodeToken()
        elif equality_op:
            yield EqualityOperatorToken(equality_op)
        elif axis:
            yield AxisToken(axis)
        elif dq_string:
            yield LiteralStringToken(dq_string)
        elif sq_string:
            yield LiteralStringToken(sq_string)
        elif node_test:
            yield NodeTestToken(node_test)
        elif name_test:
            yield NameTestToken(name_test)
        else:
            raise SyntaxError("unknown operator")
    yield EndToken()


def parse(program):
    global next, token
    generator = tokenize(program)
    next = generator.__next__ if hasattr(generator, '__next__') else generator.next
    token = next()
    return expression()


def expression(rbp=0):
    global next, token
    t = token
    verbose_print('parsing expression starting with {0}'.format(t), indent_after=True)
    token = next()
    left = t.nud(expression)
    while rbp < token.lbp:
        t = token
        verbose_print('continuing expression at {0}'.format(t))
        token = next()
        left = t.led(left, expression)
    verbose_print('finished expression', outdent_before=True)
    return left
