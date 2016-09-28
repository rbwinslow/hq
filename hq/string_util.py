import re
from html.entities import name2codepoint
from past.builtins import unichr


def html_entity_decode(s):
    result = re.sub('&(%s);' % '|'.join(name2codepoint), lambda m: unichr(name2codepoint[m.group(1)]), s)
    result = re.sub(r'&#(\d{2,3});', lambda m: chr(int(m.group(1))), result)
    return result


def truncate_string(s, length=50, one_line=True, suffix='...'):
    if len(s) <= length:
        result = s
    else:
        result = s[:length].rsplit(' ', 1)[0] + suffix
    if one_line:
        result = result.replace('\n', '\\n')
    return result
