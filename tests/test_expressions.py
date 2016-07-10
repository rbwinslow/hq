from ..query_css import query_css
from ..query_xpath import query_xpath


def test_expression(name, testfile, testline, language, source, expression, expected_result):
    raw_result = []
    if language == 'CSS':
        raw_result = query_css(source, expression)
    elif language == 'XPATH':
        raw_result = query_xpath(source, expression)
    actual_result = '\n'.join(tag.prettify().rstrip(' \t\n') for tag in raw_result)
    assert actual_result == expected_result
