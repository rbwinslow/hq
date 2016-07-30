import re

from ..verbosity import verbose_print
from .xpath_tokens import *


axes = ['child', 'descendant']
axis_pattern = '({0})'.format('|'.join(axes))
token_pattern = re.compile('\s*(?:(//)|(/)|{0}::|(\w[\w]*))'.format(axis_pattern))


def query_xpath(soup, xpath_expression):
    return parse(xpath_expression)(soup).nodes


def tokenize(program):
    for double_slash, slash, axis, name_test in token_pattern.findall(program):
        if double_slash:
            yield DoubleSlashToken()
        elif slash:
            yield SlashToken()
        elif axis:
            yield Axis(axis)
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
    left = t.nud()
    while rbp < token.lbp:
        t = token
        verbose_print('continuing expression at {0}'.format(t))
        token = next()
        left = t.led(left)
    verbose_print('finished expression; parsed node is {0}'.format(left), outdent_before=True)
    return left
