import re

from .verbosity import verbose_print
from .xpath_tokens import *


token_pattern = re.compile('\s*(?:(//)|(/)|(\w[\w]*))')


def query_xpath(soup, xpath_expression):
    return parse(xpath_expression)(soup).nodes


def tokenize(program):
    for double_slash, slash, name_test in token_pattern.findall(program):
        if double_slash:
            yield DoubleSlashToken()
        elif slash:
            yield SlashToken()
        # elif operator == "+":
        elif name_test:
            yield NameTestToken(name_test)
        else:
            raise SyntaxError("unknown operator")
    yield EndToken()


def parse(program):
    global next, token
    next = tokenize(program).__next__
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
